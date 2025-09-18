"""
메인 GUI 윈도우 모듈
"""

import sys
import os
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
                           QTableWidget, QTableWidgetItem, QComboBox, QDateEdit,
                           QCheckBox, QSpinBox, QProgressBar, QTextEdit, QTabWidget,
                           QGroupBox, QMessageBox, QFileDialog, QHeaderView,
                           QAbstractItemView, QSplitter, QToolBar, QAction, QStatusBar,
                           QDialog)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap
from typing import Dict, List, Any

# 프로젝트 모듈들
try:
    from statistical_analysis import StatisticalAnalyzer
    HAS_STATISTICS = True
except ImportError:
    HAS_STATISTICS = False


class NumericTableWidgetItem(QTableWidgetItem):
    """숫자 정렬을 위한 커스텀 테이블 아이템"""
    def __lt__(self, other):
        # UserRole에 저장된 숫자 값으로 비교
        self_data = self.data(Qt.UserRole)
        other_data = other.data(Qt.UserRole)
        
        if self_data is not None and other_data is not None:
            return self_data < other_data
        
        # UserRole 데이터가 없으면 텍스트로 비교
        return self.text() < other.text()


class SearchWorker(QThread):
    """백그라운드에서 YouTube 검색을 실행하는 워커 스레드"""
    
    finished = pyqtSignal(list)  # 검색 완료 시그널
    error = pyqtSignal(str)      # 에러 발생 시그널
    progress = pyqtSignal(int)   # 진행률 시그널
    
    def __init__(self, youtube_api, search_params):
        super().__init__()
        self.youtube_api = youtube_api
        self.search_params = search_params
    
    def run(self):
        """검색 실행"""
        try:
            self.progress.emit(10)
            
            # YouTube API 검색 실행
            results = self.youtube_api.search_videos(**self.search_params)
            
            self.progress.emit(100)
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """메인 GUI 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.youtube_api = None
        self.data_processor = None
        self.statistical_analyzer = None
        self.current_data = []
        self.search_worker = None
        
        self.init_ui()
        self.init_apis()
    
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("YouTube 트렌드 판별기 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # 툴바 추가
        self.create_toolbar()
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        
        # 상단 검색 영역
        search_group = self.create_search_area()
        main_layout.addWidget(search_group)
        
        # 진행률 표시줄
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 하단 결과 영역 (탭 위젯)
        self.result_tabs = QTabWidget()
        
        # 데이터 테이블 탭
        self.table_tab = self.create_table_tab()
        self.result_tabs.addTab(self.table_tab, "검색 결과")
        
        # 통계 탭
        self.stats_tab = self.create_stats_tab()
        self.result_tabs.addTab(self.stats_tab, "통계 분석")
        
        main_layout.addWidget(self.result_tabs)
        
        # 하단 버튼 영역
        button_layout = self.create_button_area()
        main_layout.addLayout(button_layout)
        
        # 상태바
        self.statusBar().showMessage("준비됨")
    
    def create_toolbar(self):
        """툴바 생성"""
        toolbar = self.addToolBar('메인 툴바')
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # API 키 설정
        api_key_action = QAction('🔑 API 키 설정', self)
        api_key_action.setStatusTip('YouTube Data API 키 설정')
        api_key_action.triggered.connect(self.show_api_key_dialog)
        toolbar.addAction(api_key_action)
        
        toolbar.addSeparator()
        
        # 도움말
        help_action = QAction('❓ 도움말', self)
        help_action.setStatusTip('사용법 및 도움말')
        help_action.triggered.connect(self.show_help)
        toolbar.addAction(help_action)
        
        # 프로그램 정보
        about_action = QAction('ℹ️ 정보', self)
        about_action.setStatusTip('프로그램 정보')
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def create_search_area(self) -> QGroupBox:
        """검색 조건 입력 영역 생성"""
        group = QGroupBox("검색 조건")
        main_layout = QVBoxLayout(group)
        
        # 상단 행: 검색어와 최대 결과 수
        top_layout = QHBoxLayout()
        
        top_layout.addWidget(QLabel("검색어:"))
        self.search_query = QLineEdit()
        self.search_query.setPlaceholderText("검색할 키워드를 입력하세요")
        top_layout.addWidget(self.search_query, 2)  # stretch factor 2
        
        top_layout.addSpacing(20)
        
        top_layout.addWidget(QLabel("최대 결과 수:"))
        self.max_results = QSpinBox()
        self.max_results.setRange(1, 100)
        self.max_results.setValue(50)
        self.max_results.setMinimumWidth(80)
        top_layout.addWidget(self.max_results)
        
        main_layout.addLayout(top_layout)
        
        # 중간 행: 영상 설정
        middle_layout = QHBoxLayout()
        
        middle_layout.addWidget(QLabel("영상 길이:"))
        self.video_duration = QComboBox()
        self.video_duration.addItem("전체", "any")
        self.video_duration.addItem("4분 미만 (숏폼)", "short")
        self.video_duration.addItem("4-20분", "medium")
        self.video_duration.addItem("20분 이상 (롱폼)", "long")
        self.video_duration.setMinimumWidth(150)
        middle_layout.addWidget(self.video_duration)
        
        middle_layout.addSpacing(20)
        
        middle_layout.addWidget(QLabel("정렬 방식:"))
        self.order_type = QComboBox()
        self.order_type.addItem("관련성", "relevance")
        self.order_type.addItem("최신순", "date")
        self.order_type.addItem("조회수", "viewCount")
        self.order_type.addItem("평점", "rating")
        self.order_type.addItem("제목", "title")
        self.order_type.setMinimumWidth(120)
        middle_layout.addWidget(self.order_type)
        
        middle_layout.addSpacing(20)
        
        middle_layout.addWidget(QLabel("국가/지역:"))
        from gui.widgets import CountrySelector
        self.country_selector = CountrySelector()
        self.country_selector.setMinimumWidth(100)
        middle_layout.addWidget(self.country_selector)
        
        middle_layout.addStretch()  # 오른쪽 여백
        
        main_layout.addLayout(middle_layout)
        
        # 하단 행: 연령층과 날짜 설정
        bottom_layout = QHBoxLayout()
        
        bottom_layout.addWidget(QLabel("연령층:"))
        self.age_group = QComboBox()
        self.age_group.addItem("전체", "전체")
        self.age_group.addItem("어린이 (7세 이하)", "어린이 (7세 이하)")
        self.age_group.addItem("청소년 (8-17세)", "청소년 (8-17세)")
        self.age_group.addItem("청년 (18-24세)", "청년 (18-24세)")
        self.age_group.addItem("성인 (25-34세)", "성인 (25-34세)")
        self.age_group.addItem("중년 (35-54세)", "중년 (35-54세)")
        self.age_group.addItem("장년 (55세 이상)", "장년 (55세 이상)")
        self.age_group.setMinimumWidth(150)
        bottom_layout.addWidget(self.age_group)
        
        bottom_layout.addSpacing(20)
        
        bottom_layout.addWidget(QLabel("검색 기간:"))
        
        # 시작일
        bottom_layout.addWidget(QLabel("시작일:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setMinimumWidth(120)
        self.date_from.dateChanged.connect(self.validate_date_range)
        bottom_layout.addWidget(self.date_from)
        
        bottom_layout.addSpacing(10)
        
        # 종료일
        bottom_layout.addWidget(QLabel("종료일:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setMinimumWidth(120)
        self.date_to.dateChanged.connect(self.validate_date_range)
        bottom_layout.addWidget(self.date_to)
        
        bottom_layout.addStretch()  # 오른쪽 여백
        
        main_layout.addLayout(bottom_layout)
        
        # 버튼들을 위한 가운데 정렬 레이아웃
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 왼쪽 공간
        
        # 검색 버튼
        self.search_button = QPushButton("검색 실행")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.search_button.clicked.connect(self.start_search)
        button_layout.addWidget(self.search_button)
        
        button_layout.addSpacing(20)  # 버튼 간 간격
        
        # 인기 급상승 버튼
        self.trending_button = QPushButton("인기 급상승")
        self.trending_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
            QPushButton:pressed {
                background-color: #E53935;
            }
        """)
        self.trending_button.clicked.connect(self.load_trending_videos)
        button_layout.addWidget(self.trending_button)
        
        button_layout.addStretch()  # 오른쪽 공간
        
        # 버튼 레이아웃을 메인 레이아웃에 추가
        main_layout.addLayout(button_layout)
        
        return group
    
    def create_table_tab(self) -> QWidget:
        """데이터 테이블 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 필터 영역
        filter_group = QGroupBox("필터")
        filter_layout = QHBoxLayout(filter_group)
        
        # 키워드 필터
        filter_layout.addWidget(QLabel("키워드:"))
        self.filter_keyword = QLineEdit()
        self.filter_keyword.setPlaceholderText("제목/태그에서 검색")
        filter_layout.addWidget(self.filter_keyword)
        
        # 조회수 필터
        filter_layout.addWidget(QLabel("최소 조회수:"))
        self.filter_min_views = QSpinBox()
        self.filter_min_views.setRange(0, 999999999)
        self.filter_min_views.setSuffix(" 회")
        filter_layout.addWidget(self.filter_min_views)
        
        # 숏폼/롱폼 필터
        self.filter_short_only = QCheckBox("숏폼만")
        self.filter_long_only = QCheckBox("롱폼만")
        filter_layout.addWidget(self.filter_short_only)
        filter_layout.addWidget(self.filter_long_only)
        
        # 필터 적용 버튼
        filter_button = QPushButton("필터 적용")
        filter_button.clicked.connect(self.apply_filters)
        filter_layout.addWidget(filter_button)
        
        # 필터 초기화 버튼
        clear_filter_button = QPushButton("필터 초기화")
        clear_filter_button.clicked.connect(self.clear_filters)
        filter_layout.addWidget(clear_filter_button)
        
        layout.addWidget(filter_group)
        
        # 데이터 테이블
        self.data_table = QTableWidget()
        self.setup_table()
        layout.addWidget(self.data_table)
        
        return tab
    
    def setup_table(self):
        """데이터 테이블 설정"""
        # 컬럼 설정
        columns = [
            "제목", "채널", "게시일", "조회수", "좋아요", "댓글수", 
            "재생시간", "분류", "좋아요율(%)", "댓글율(%)", "참여도점수", "태그"
        ]
        
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)
        
        # 테이블 설정
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data_table.setSortingEnabled(True)
        
        # 컬럼 크기 조정
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 제목 컬럼 늘어나기
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 채널
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 게시일
        
        # 더블클릭 이벤트
        self.data_table.cellDoubleClicked.connect(self.on_cell_double_click)
    
    def create_stats_tab(self) -> QWidget:
        """통계 분석 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 요약 통계
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        layout.addWidget(QLabel("요약 통계:"))
        layout.addWidget(self.stats_text)
        
        # 상위 성과 영상
        layout.addWidget(QLabel("상위 성과 영상:"))
        self.top_videos_table = QTableWidget()
        self.top_videos_table.setColumnCount(5)
        self.top_videos_table.setHorizontalHeaderLabels(["제목", "조회수", "좋아요", "댓글수", "참여도점수"])
        layout.addWidget(self.top_videos_table)
        
        return tab
    
    def create_button_area(self) -> QHBoxLayout:
        """하단 버튼 영역 생성"""
        layout = QHBoxLayout()
        
        # CSV 내보내기
        csv_button = QPushButton("CSV로 내보내기")
        csv_button.clicked.connect(self.export_csv)
        layout.addWidget(csv_button)
        
        # 기초 통계 분석 버튼
        self.stats_button = QPushButton("기초 통계 분석")
        self.stats_button.clicked.connect(self.run_advanced_analysis)
        self.stats_button.setEnabled(False)  # 데이터가 있을 때만 활성화
        layout.addWidget(self.stats_button)
        
        layout.addStretch()  # 좌측 정렬을 위한 스트레치
        
        # 정보 레이블
        self.info_label = QLabel("데이터 없음")
        layout.addWidget(self.info_label)
        
        return layout
    
    def init_apis(self):
        """API 초기화"""
        try:
            # 상위 디렉토리의 모듈들을 import
            import sys
            import os
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            # YouTube API 초기화
            from youtube_api import YouTubeAPI
            from data_processor import DataProcessor
            
            self.youtube_api = YouTubeAPI()
            self.data_processor = DataProcessor()
            
            # API 키 상태 확인
            if not self.youtube_api.api_key or not self.youtube_api.youtube:
                self.statusBar().showMessage("⚠️ YouTube API 키가 설정되지 않았습니다. 상단 메뉴에서 API 키를 설정해주세요.")
                # API 키가 없어도 UI는 활성화하되, 검색 기능만 비활성화
                self.search_button.setEnabled(False)
                self.trending_button.setEnabled(False)
            else:
                self.statusBar().showMessage("✅ API 초기화 완료")
                self.search_button.setEnabled(True)
                self.trending_button.setEnabled(True)
            
            # 통계 분석기 초기화
            if HAS_STATISTICS:
                self.statistical_analyzer = StatisticalAnalyzer()
                print("기초 통계 분석 기능이 활성화되었습니다.")
            
        except Exception as e:
            QMessageBox.critical(self, "초기화 오류", 
                               f"API 초기화 중 오류가 발생했습니다:\n{str(e)}")
            self.search_button.setEnabled(False)
            self.trending_button.setEnabled(False)
    
    def validate_date_range(self):
        """날짜 범위 실시간 검증"""
        start_date = self.date_from.date()
        end_date = self.date_to.date()
        
        if start_date > end_date:
            # 날짜 위젯 스타일 변경 (빨간색 테두리)
            error_style = """
                QDateEdit {
                    border: 2px solid #e74c3c;
                    border-radius: 4px;
                    background-color: #fdf2f2;
                }
            """
            self.date_from.setStyleSheet(error_style)
            self.date_to.setStyleSheet(error_style)
            
            # 검색 버튼 비활성화
            self.search_button.setEnabled(False)
            
            # 상태바에 오류 메시지 표시
            self.statusBar().showMessage(f"날짜 오류: 시작일이 종료일보다 늦습니다 "
                                       f"({start_date.toString('yyyy-MM-dd')} > {end_date.toString('yyyy-MM-dd')})")
        else:
            # 정상 스타일로 복원
            normal_style = ""
            self.date_from.setStyleSheet(normal_style)
            self.date_to.setStyleSheet(normal_style)
            
            # 검색 버튼 활성화 (API가 초기화된 경우에만)
            if self.youtube_api:
                self.search_button.setEnabled(True)
            
            # 상태바 메시지 클리어
            self.statusBar().clearMessage()
    
    def start_search(self):
        """검색 시작"""
        if not self.youtube_api:
            QMessageBox.warning(self, "오류", "API가 초기화되지 않았습니다.")
            return
        
        # API 키 확인
        if not self.youtube_api.api_key or not self.youtube_api.youtube:
            QMessageBox.warning(self, "API 키 필요", 
                              "YouTube API 키가 설정되지 않았습니다.\n"
                              "상단 메뉴바의 '🔑 API 키 설정'을 클릭하여 API 키를 입력해주세요.")
            self.show_api_key_dialog()
            return
        
        query = self.search_query.text().strip()
        if not query:
            QMessageBox.warning(self, "입력 오류", "검색어를 입력해주세요.")
            return
        
        # 날짜 검증
        start_date = self.date_from.date()
        end_date = self.date_to.date()
        
        if start_date > end_date:
            QMessageBox.warning(self, "날짜 오류", 
                              f"시작일({start_date.toString('yyyy-MM-dd')})이 "
                              f"종료일({end_date.toString('yyyy-MM-dd')})보다 늦습니다.\n"
                              "날짜를 다시 확인해주세요.")
            return
        
        # 검색 매개변수 설정
        search_params = {
            'query': query,
            'max_results': self.max_results.value(),
            'video_duration': self.video_duration.currentData(),
            'order': self.order_type.currentData(),
            'published_after': start_date.toString('yyyy-MM-dd'),
            'published_before': end_date.toString('yyyy-MM-dd'),
            'age_group': self.age_group.currentData()  # 연령층 필터 (수정됨)
        }
        
        # 국가 코드 추가 (선택된 경우)
        country_code = self.country_selector.currentData()
        if country_code:
            search_params['region_code'] = country_code
        
        # UI 상태 변경
        self.search_button.setEnabled(False)
        self.trending_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.statusBar().showMessage("검색 중...")
        
        # 워커 스레드 시작
        self.search_worker = SearchWorker(self.youtube_api, search_params)
        self.search_worker.finished.connect(self.on_search_finished)
        self.search_worker.error.connect(self.on_search_error)
        self.search_worker.progress.connect(self.progress_bar.setValue)
        self.search_worker.start()
    
    def load_trending_videos(self):
        """인기 급상승 영상 로드"""
        if not self.youtube_api:
            QMessageBox.warning(self, "오류", "API가 초기화되지 않았습니다.")
            return
        
        # API 키 확인
        if not self.youtube_api.api_key or not self.youtube_api.youtube:
            QMessageBox.warning(self, "API 키 필요", 
                              "YouTube API 키가 설정되지 않았습니다.\n"
                              "상단 메뉴바의 '🔑 API 키 설정'을 클릭하여 API 키를 입력해주세요.")
            self.show_api_key_dialog()
            return
        
        try:
            self.statusBar().showMessage("인기 급상승 영상 로딩 중...")
            self.search_button.setEnabled(False)
            self.trending_button.setEnabled(False)
            
            # 선택된 국가 코드 가져오기
            country_code = self.country_selector.currentData()
            if not country_code:
                country_code = "KR"  # 기본값: 한국
            
            # 트렌딩 영상 가져오기
            trending_videos = self.youtube_api.get_trending_videos(
                region_code=country_code, 
                max_results=50
            )
            self.on_search_finished(trending_videos)
            
        except Exception as e:
            self.on_search_error(str(e))
    
    def on_search_finished(self, results: List[Dict]):
        """검색 완료 처리"""
        try:
            self.current_data = results
            
            # 데이터 처리
            if results:
                df = self.data_processor.process_youtube_data(results)
                self.update_table(df)
                self.update_stats()
                
                # 기초 통계 분석 버튼 활성화
                self.stats_button.setEnabled(len(results) > 0 and HAS_STATISTICS)
                
                self.info_label.setText(f"총 {len(results)}개 영상")
                self.statusBar().showMessage(f"검색 완료 - {len(results)}개 영상 발견")
            else:
                self.clear_table()
                self.stats_button.setEnabled(False)
                self.info_label.setText("검색 결과 없음")
                self.statusBar().showMessage("검색 결과가 없습니다")
            
        except Exception as e:
            self.on_search_error(f"데이터 처리 중 오류: {str(e)}")
        
        finally:
            # UI 상태 복원
            self.search_button.setEnabled(True)
            self.trending_button.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def on_search_error(self, error_message: str):
        """검색 오류 처리"""
        QMessageBox.critical(self, "검색 오류", f"검색 중 오류가 발생했습니다:\n{error_message}")
        
        self.search_button.setEnabled(True)
        self.trending_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("검색 실패")
    
    def update_table(self, df):
        """테이블 업데이트"""
        if df.empty:
            self.clear_table()
            return
        
        # 정렬을 임시로 비활성화
        self.data_table.setSortingEnabled(False)
        self.data_table.setRowCount(len(df))
        
        for row in range(len(df)):
            data = df.iloc[row]
            
            # 각 컬럼 데이터 설정
            title_item = QTableWidgetItem(str(data['title']))
            # 비디오 ID를 각 행의 첫 번째 아이템에 숨겨진 데이터로 저장
            video_id = str(data.get('video_id', ''))
            print(f"행 {row}: 비디오 ID '{video_id}' 저장")
            title_item.setData(Qt.UserRole, video_id)
            self.data_table.setItem(row, 0, title_item)
            
            channel_item = QTableWidgetItem(str(data['channel_title']))
            self.data_table.setItem(row, 1, channel_item)
            
            # 날짜 포맷팅
            if data['published_at']:
                date_str = data['published_at'].strftime('%Y-%m-%d')
            else:
                date_str = "알 수 없음"
            date_item = QTableWidgetItem(date_str)
            self.data_table.setItem(row, 2, date_item)
            
            # 숫자 데이터 - 정렬을 위해 커스텀 아이템 사용
            view_item = NumericTableWidgetItem(f"{data['view_count']:,}")
            view_item.setData(Qt.UserRole, int(data['view_count']))
            self.data_table.setItem(row, 3, view_item)
            
            like_item = NumericTableWidgetItem(f"{data['like_count']:,}")
            like_item.setData(Qt.UserRole, int(data['like_count']))
            self.data_table.setItem(row, 4, like_item)
            
            comment_item = NumericTableWidgetItem(f"{data['comment_count']:,}")
            comment_item.setData(Qt.UserRole, int(data['comment_count']))
            self.data_table.setItem(row, 5, comment_item)
            
            duration_item = QTableWidgetItem(str(data['duration_formatted']))
            self.data_table.setItem(row, 6, duration_item)
            
            category_item = QTableWidgetItem("숏폼" if data['is_short_form'] else "롱폼")
            self.data_table.setItem(row, 7, category_item)
            
            like_rate_item = NumericTableWidgetItem(f"{data['like_rate']:.2f}")
            like_rate_item.setData(Qt.UserRole, float(data['like_rate']))
            self.data_table.setItem(row, 8, like_rate_item)
            
            comment_rate_item = NumericTableWidgetItem(f"{data['comment_rate']:.2f}")
            comment_rate_item.setData(Qt.UserRole, float(data['comment_rate']))
            self.data_table.setItem(row, 9, comment_rate_item)
            
            engagement_item = NumericTableWidgetItem(f"{data['engagement_score']:,}")
            engagement_item.setData(Qt.UserRole, int(data['engagement_score']))
            self.data_table.setItem(row, 10, engagement_item)
            
            tags_item = QTableWidgetItem(str(data['tags']))
            self.data_table.setItem(row, 11, tags_item)
        
        # 정렬 기능 다시 활성화
        self.data_table.setSortingEnabled(True)
        
        # 테이블 크기 조정
        self.data_table.resizeColumnsToContents()
    
    def clear_table(self):
        """테이블 클리어"""
        self.data_table.setRowCount(0)
    
    def update_stats(self):
        """통계 정보 업데이트"""
        if not self.data_processor.df is not None:
            return
        
        stats = self.data_processor.get_summary_stats()
        
        # 요약 통계 텍스트
        stats_text = f"""
총 영상 수: {stats.get('total_videos', 0):,}개
숏폼 영상: {stats.get('short_form_count', 0):,}개
롱폼 영상: {stats.get('long_form_count', 0):,}개

평균 조회수: {stats.get('avg_views', 0):,.0f}회
중간값 조회수: {stats.get('median_views', 0):,.0f}회
최대 조회수: {stats.get('max_views', 0):,}회

평균 좋아요: {stats.get('avg_likes', 0):,.0f}개
평균 댓글수: {stats.get('avg_comments', 0):,.0f}개

평균 좋아요율: {stats.get('avg_like_rate', 0):.3f}%
평균 댓글율: {stats.get('avg_comment_rate', 0):.3f}%
평균 재생시간: {stats.get('avg_duration', 0):.0f}초
        """
        
        self.stats_text.setText(stats_text)
        
        # 상위 성과 영상 테이블
        top_videos = self.data_processor.get_top_performers('view_count', 10)
        
        self.top_videos_table.setRowCount(len(top_videos))
        
        for row in range(len(top_videos)):
            data = top_videos.iloc[row]
            self.top_videos_table.setItem(row, 0, QTableWidgetItem(str(data['title'])))
            self.top_videos_table.setItem(row, 1, QTableWidgetItem(f"{data['view_count']:,}"))
            self.top_videos_table.setItem(row, 2, QTableWidgetItem(f"{data['like_count']:,}"))
            self.top_videos_table.setItem(row, 3, QTableWidgetItem(f"{data['comment_count']:,}"))
            self.top_videos_table.setItem(row, 4, QTableWidgetItem(f"{data['engagement_score']:,}"))
        
        self.top_videos_table.resizeColumnsToContents()
    
    def apply_filters(self):
        """필터 적용"""
        if not self.data_processor.df is not None:
            return
        
        filters = {
            'keyword': self.filter_keyword.text().strip(),
            'min_views': self.filter_min_views.value() if self.filter_min_views.value() > 0 else None,
            'short_form_only': self.filter_short_only.isChecked(),
            'long_form_only': self.filter_long_only.isChecked()
        }
        
        # 상호 배타적 필터 처리
        if filters['short_form_only'] and filters['long_form_only']:
            QMessageBox.warning(self, "필터 오류", "숏폼과 롱폼을 동시에 선택할 수 없습니다.")
            return
        
        try:
            filtered_df = self.data_processor.filter_data(filters)
            self.update_table(filtered_df)
            self.info_label.setText(f"필터 적용 - {len(filtered_df)}개 영상")
            
        except Exception as e:
            QMessageBox.critical(self, "필터 오류", f"필터 적용 중 오류가 발생했습니다:\n{str(e)}")
    
    def clear_filters(self):
        """필터 초기화"""
        self.filter_keyword.clear()
        self.filter_min_views.setValue(0)
        self.filter_short_only.setChecked(False)
        self.filter_long_only.setChecked(False)
        
        if self.data_processor.df is not None:
            self.update_table(self.data_processor.df)
            self.info_label.setText(f"총 {len(self.data_processor.df)}개 영상")
    
    def on_cell_double_click(self, row: int, column: int):
        """셀 더블클릭 처리 (썸네일 뷰어 또는 YouTube 링크 열기)"""
        if self.data_processor.df is not None and row < self.data_table.rowCount():
            # 클릭된 행의 비디오 ID 가져오기 (제목 열에 저장됨)
            title_item = self.data_table.item(row, 0)
            if title_item:
                video_id = title_item.data(Qt.UserRole)
                print(f"클릭된 행: {row}, 비디오 ID: {video_id}")
                
                if video_id:
                    # 비디오 ID로 원본 데이터에서 해당 영상 찾기
                    matching_rows = self.data_processor.df[self.data_processor.df['video_id'] == video_id]
                    print(f"매칭된 행 수: {len(matching_rows)}")
                    
                    if not matching_rows.empty:
                        video_data = matching_rows.iloc[0].to_dict()
                        print(f"영상 제목: {video_data.get('title', 'N/A')}")
                        
                        # 썸네일 뷰어 열기
                        from gui.widgets import ThumbnailViewer
                        thumbnail_viewer = ThumbnailViewer(video_data, self)
                        thumbnail_viewer.exec_()
                    else:
                        QMessageBox.warning(self, "오류", f"해당 영상 데이터를 찾을 수 없습니다. (비디오 ID: {video_id})")
                else:
                    QMessageBox.warning(self, "오류", "영상 ID 정보가 없습니다.")
            else:
                QMessageBox.warning(self, "오류", "테이블 아이템을 찾을 수 없습니다.")
    
    def show_api_key_dialog(self):
        """API 키 설정 다이얼로그 표시"""
        from gui.widgets import ApiKeyDialog
        
        current_api_key = ""
        if self.youtube_api and hasattr(self.youtube_api, 'api_key'):
            current_api_key = self.youtube_api.api_key
        
        dialog = ApiKeyDialog(current_api_key, self)
        dialog.api_key_changed.connect(self.update_api_key)
        dialog.exec_()
    
    def update_api_key(self, new_api_key: str):
        """API 키 업데이트"""
        try:
            # 설정 파일 업데이트
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config', 'config.json')
            
            # 기존 설정 로드
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # API 키 업데이트
            config['youtube_api_key'] = new_api_key
            
            # 설정 파일 저장
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # YouTube API 재초기화
            self.init_apis()
            
            QMessageBox.information(self, "API 키 업데이트", "API 키가 성공적으로 업데이트되었습니다.")
            
        except Exception as e:
            QMessageBox.critical(self, "API 키 업데이트 오류", f"API 키 업데이트 중 오류가 발생했습니다:\n{str(e)}")
    
    def show_help(self):
        """도움말 표시 (탭 형태)"""
        # 도움말 다이얼로그 생성
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("도움말")
        help_dialog.setModal(True)
        help_dialog.resize(800, 600)
        
        # 레이아웃 설정
        layout = QVBoxLayout(help_dialog)
        
        # 탭 위젯 생성
        tab_widget = QTabWidget()
        
        # 첫 번째 탭: 기본 사용법
        basic_tab = QTextEdit()
        basic_tab.setReadOnly(True)
        basic_help_text = """
<h2>🔍 기본 사용법</h2>

<h3>검색 조건</h3>
<ul>
<li><b>검색어</b>: 키워드 입력</li>
<li><b>최대 결과 수</b>: 1~100개 (기본: 50개)</li>
<li><b>영상 길이</b>: 숏폼/미디엄/롱폼</li>
<li><b>정렬</b>: 관련성, 최신순, 조회수</li>
<li><b>지역</b>: 국가별 트렌드</li>
</ul>

<h3>🎯 연령층 타겟팅</h3>
<ul>
<li><b>어린이</b>: 7세 이하</li>
<li><b>청소년</b>: 8-17세</li>
<li><b>청년</b>: 18-24세</li>
<li><b>성인</b>: 25-34세</li>
<li><b>중년</b>: 35-54세</li>
<li><b>장년</b>: 55세 이상</li>
</ul>

<h3>📊 결과 확인</h3>
<ul>
<li><b>테이블 정렬</b>: 컬럼 헤더 클릭</li>
<li><b>썸네일</b>: 제목 더블클릭</li>
<li><b>CSV 내보내기</b>: 결과 저장</li>
</ul>

<h3>⚙️ 설정</h3>
<ul>
<li><b>API 키</b>: 툴바에서 설정</li>
<li><b>연결 테스트</b>: 상태 확인</li>
</ul>
        """
        basic_tab.setHtml(basic_help_text)
        tab_widget.addTab(basic_tab, "기본 사용법")
        
        # 두 번째 탭: 통계 분석 설명
        stats_tab = QTextEdit()
        stats_tab.setReadOnly(True)
        stats_help_text = """
<h2>� 통계 분석 기능</h2>

<h3>✅ 1. 상관분석 (Correlation)</h3>
<p><b>목적:</b> 지표 간의 관계 파악</p>
<ul>
<li><b>조회수 ↔ 좋아요:</b> 0.85 (높음) → 조회수↑ = 좋아요↑</li>
<li><b>조회수 ↔ 댓글:</b> 0.62 (중간) → 어느 정도 함께 증가</li>
<li><b>조회수 ↔ 영상길이:</b> -0.30 (음의 관계) → 길어질수록 조회수↓</li>
</ul>
<p><b>해석 기준:</b></p>
<ul>
<li>±0.7 이상: 꽤 강한 관계</li>
<li>±0.3~0.7: 중간 정도</li>
<li>±0.3 이하: 거의 관계 없음</li>
</ul>

<h3>✅ 2. 그룹 비교 (Group Comparison)</h3>
<p><b>목적:</b> 카테고리별 성과 차이 확인</p>
<ul>
<li><b>요일별:</b> 주말 15,000 vs 평일 9,000 → 주말이 유리</li>
<li><b>영상 길이별:</b> 5분 미만(12K), 5-15분(18K), 15분+(8K)</li>
<li><b>결론:</b> 5-15분 영상이 가장 좋은 성과</li>
</ul>

<h3>✅ 3. 상위 분석 (Top N / Pareto)</h3>
<p><b>목적:</b> 성공 영상의 공통점 찾기</p>
<ul>
<li><b>파레토 법칙:</b> 상위 10% 영상이 전체 조회수의 65% 차지</li>
<li><b>성공 패턴:</b> 특정 키워드, 7-12분 길이, 주말 업로드</li>
<li><b>활용:</b> 성공 요소를 반복 적용</li>
</ul>

<h3>📈 참여도 지표</h3>
<ul>
<li><b>참여도 점수:</b> (좋아요 + 댓글) 기반</li>
<li><b>좋아요율:</b> 좋아요 ÷ 조회수 × 100</li>
<li><b>댓글율:</b> 댓글 ÷ 조회수 × 100</li>
</ul>
        """
        stats_tab.setHtml(stats_help_text)
        tab_widget.addTab(stats_tab, "기초 통계 가이드")
        
        # 레이아웃에 탭 위젯 추가
        layout.addWidget(tab_widget)
        
        # 닫기 버튼
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("닫기")
        close_button.clicked.connect(help_dialog.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        # 다이얼로그 표시
        help_dialog.exec_()

    def show_about(self):
        """프로그램 정보 표시"""
        about_text = """
<h2>YouTube 트렌드 판별기 v1.0</h2>

<p><b>YouTube Data API v3를 활용한 영상 데이터 수집 및 분석 도구</b></p>

<h3>주요 기능</h3>
<ul>
<li>🔍 강력한 검색 및 필터링</li>
<li>📊 상세한 데이터 분석</li>
<li>🖼️ 썸네일 미리보기</li>
<li>🌍 국가별 트렌드 분석</li>
<li>💾 CSV 데이터 내보내기</li>
</ul>

<h3>기술 스택</h3>
<ul>
<li>Python 3.8+</li>
<li>PyQt5 (GUI)</li>
<li>Pandas (데이터 처리)</li>
<li>Google API Client (YouTube API)</li>
</ul>

<h3>개발자 정보</h3>
<p>YouTube Trend Analyzer Team</p>
<p>© 2024 All rights reserved</p>

<p><i>이 프로그램이 도움이 되었다면 ⭐를 눌러주세요!</i></p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("프로그램 정보")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def export_csv(self):
        stats_help_text = """
<h2>📊 기초 통계 분석 기능 상세 설명</h2>

<h3>📈 기본 개요</h3>
<p>YouTube 영상 데이터의 기본적인 통계 지표를 분석하여 실용적인 인사이트를 제공하는 기능입니다.</p>

<h3>� 주요 분석 항목</h3>

<h4>1. 상관관계 분석</h4>
<ul>
<li><b>조회수 ↔ 좋아요</b>: 일반적으로 0.7~0.9의 높은 상관관계 (예: 0.85)</li>
<li><b>조회수 ↔ 댓글수</b>: 보통 0.5~0.8의 중간 상관관계 (예: 0.72)</li>
<li><b>좋아요 ↔ 댓글수</b>: 참여도 지표 간 상관관계 분석</li>
<li><b>해석</b>: 1에 가까울수록 강한 양의 상관관계, 0에 가까울수록 무관</li>
</ul>

<h4>2. 그룹 비교 분석</h4>
<ul>
<li><b>요일별 성과</b>: 월~일요일 업로드 영상의 평균 조회수 비교</li>
<li><b>영상 길이별 성과</b>: 숏폼(4분 미만) vs 롱폼(4분 이상) 성과 차이</li>
<li><b>시간대별 업로드</b>: 오전/오후/저녁 업로드 시간에 따른 성과 분석</li>
<li><b>실용적 활용</b>: 최적의 업로드 요일과 시간대 발견</li>
</ul>

<h4>3. 상위 성과 분석 (파레토 법칙)</h4>
<ul>
<li><b>80/20 법칙</b>: 상위 20% 영상이 전체 조회수의 80% 차지하는지 확인</li>
<li><b>Top 20% 영상 특성</b>: 높은 성과를 보이는 영상들의 공통점 분석</li>
<li><b>성과 집중도</b>: 소수의 영상에 얼마나 성과가 집중되어 있는지 측정</li>
<li><b>전략적 시사점</b>: 핵심 콘텐츠 유형 식별 및 집중 전략 수립</li>
</ul>

<h3>� 실제 활용 예시</h3>

<h4>콘텐츠 크리에이터를 위한 팁</h4>
<ul>
<li><b>업로드 최적화</b>: "화요일 오후 2시 업로드시 평균 조회수 1.3배 증가"</li>
<li><b>길이 전략</b>: "4분 미만 숏폼이 참여율 25% 더 높음"</li>
<li><b>핵심 콘텐츠</b>: "요리 레시피 중 20%가 전체 조회수의 75% 차지"</li>
</ul>

<h4>마케터를 위한 인사이트</h4>
<ul>
<li><b>타겟팅</b>: 높은 상관관계 영상을 통한 효과적인 광고 집행</li>
<li><b>콘텐츠 선별</b>: 상위 20% 성과 영상 유형에 마케팅 집중</li>
<li><b>시기 결정</b>: 요일별/시간대별 분석으로 캠페인 타이밍 최적화</li>
</ul>

<h3>⚠️ 주의사항</h3>
<ul>
<li>분석 결과는 현재 수집된 데이터를 기반으로 하며, 지속적인 업데이트 필요</li>
<li>최소 20개 이상의 영상 데이터가 있어야 의미있는 분석 가능</li>
<li>계절성, 이벤트 등 외부 요인은 별도로 고려해야 함</li>
</ul>

<h3>🔧 기술 스택</h3>
<ul>
<li><b>Pandas</b>: 데이터 처리 및 기초 통계 계산</li>
<li><b>NumPy</b>: 수치 계산 및 상관관계 분석</li>
<li><b>기초 통계학</b>: 평균, 상관계수, 백분위수 등 기본 통계 지표</li>
</ul>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("기초 통계 분석 상세 설명")
        msg.setTextFormat(Qt.RichText)
        msg.setText(stats_help_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def export_csv(self):
        """CSV 내보내기"""
        if self.data_processor.df is None or self.data_processor.df.empty:
            QMessageBox.warning(self, "내보내기 오류", "내보낼 데이터가 없습니다.")
            return
        
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "CSV 파일 저장", "youtube_data.csv", "CSV 파일 (*.csv)"
            )
            
            if filename:
                # 전체 경로를 사용하여 CSV 파일 저장
                self.data_processor.df.to_csv(filename, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, "내보내기 완료", f"CSV 파일이 저장되었습니다:\n{filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "내보내기 오류", f"CSV 내보내기 중 오류가 발생했습니다:\n{str(e)}")
    


    
    def run_advanced_analysis(self):
        """기초 통계 분석 실행"""
        if not self.current_data:
            QMessageBox.warning(self, "분석 불가", "분석할 데이터가 없습니다. 먼저 YouTube 데이터를 검색해주세요.")
            return
            
        if not HAS_STATISTICS:
            QMessageBox.warning(self, "분석 불가", "통계 분석 모듈이 설치되지 않았습니다.")
            return
            
        if not self.statistical_analyzer:
            QMessageBox.warning(self, "분석 불가", "통계 분석기가 초기화되지 않았습니다.")
            return
        
        try:
            self.statusBar().showMessage("기초 통계 분석 중...")
            self.stats_button.setEnabled(False)
            
            # 데이터 확인
            print(f"현재 데이터 개수: {len(self.current_data)}")
            print(f"데이터 샘플: {self.current_data[0] if self.current_data else 'None'}")
            
            # 종합 분석 보고서 생성
            report = self.statistical_analyzer.generate_comprehensive_report(self.current_data)
            
            # 보고서 확인
            print(f"생성된 보고서 키: {list(report.keys())}")
            if 'error' in report:
                print(f"보고서 생성 오류: {report['error']}")
            
            # 결과를 통계 탭에 표시
            self.display_analysis_results(report)
            
            # 통계 탭으로 전환
            self.result_tabs.setCurrentIndex(1)
            
            self.statusBar().showMessage("기초 통계 분석 완료")
            
        except Exception as e:
            error_msg = f"통계 분석 중 오류가 발생했습니다:\n{str(e)}"
            print(f"분석 오류: {error_msg}")
            QMessageBox.critical(self, "분석 오류", error_msg)
            
        finally:
            self.stats_button.setEnabled(True)
    
    def display_analysis_results(self, report: Dict[str, Any]):
        """분석 결과를 통계 탭에 표시"""
        try:
            # 기존 내용 지우기
            self.stats_text.clear()
            
            # 보고서 포맷팅
            formatted_report = self.format_analysis_report(report)
            
            # HTML 형식으로 표시
            self.stats_text.setHtml(formatted_report)
            
        except Exception as e:
            self.stats_text.setPlainText(f"결과 표시 중 오류: {str(e)}")
    
    def format_analysis_report(self, report: Dict[str, Any]) -> str:
        """분석 보고서를 HTML 형식으로 포맷팅"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: 'Malgun Gothic', Arial, sans-serif; margin: 20px; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; margin-top: 25px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }
                h3 { color: #7f8c8d; }
                .metric { background-color: #f8f9fa; padding: 8px; margin: 5px 0; border-radius: 4px; border-left: 3px solid #3498db; }
                .highlight { color: #e74c3c; font-weight: bold; }
                .stats-table { border-collapse: collapse; width: 100%; margin: 10px 0; }
                .stats-table th, .stats-table td { border: 1px solid #bdc3c7; padding: 8px; text-align: left; }
                .stats-table th { background-color: #ecf0f1; }
                .error { color: #e74c3c; background-color: #fdf2f2; padding: 10px; border-radius: 4px; }
                .correlation-strong { color: #27ae60; font-weight: bold; }
                .correlation-moderate { color: #f39c12; font-weight: bold; }
                .correlation-weak { color: #95a5a6; }
            </style>
        </head>
        <body>
        """
        
        try:
            # 오류 체크
            if 'error' in report:
                html += f'<div class="error"><h2>⚠️ 분석 오류</h2><p>{report["error"]}</p></div>'
                html += "</body></html>"
                return html
            
            # 제목
            html += "<h1>📊 YouTube 트렌드 기초 통계 분석 보고서</h1>"
            
            # 요약 정보
            if 'summary' in report:
                summary = report['summary']
                if 'error' not in summary:
                    html += f"""
                    <h2>📈 분석 요약</h2>
                    <div class="metric">총 분석 영상 수: <span class="highlight">{summary.get('total_videos', 0):,}개</span></div>
                    <div class="metric">평균 조회수: <span class="highlight">{summary.get('avg_views', 0):,}회</span></div>
                    <div class="metric">평균 참여도: <span class="highlight">{summary.get('avg_engagement', 0):.4f}</span></div>
                    <div class="metric">분석 일시: {summary.get('analysis_date', 'N/A')}</div>
                    """
            
            # 기본 통계
            if 'basic_stats' in report:
                basic_stats = report['basic_stats']
                if 'error' not in basic_stats:
                    html += "<h2>� 기본 통계</h2>"
                    html += '<table class="stats-table">'
                    html += '<tr><th>지표</th><th>평균</th><th>중간값</th><th>표준편차</th><th>최소값</th><th>최대값</th></tr>'
                    
                    stat_names = {
                        'view_count': '조회수',
                        'like_count': '좋아요',
                        'comment_count': '댓글',
                        'engagement_rate': '참여도'
                    }
                    
                    for key, stats in basic_stats.items():
                        if isinstance(stats, dict) and 'mean' in stats:
                            name = stat_names.get(key, key)
                            html += f"""
                            <tr>
                                <td>{name}</td>
                                <td>{stats.get('mean', 0):,.2f}</td>
                                <td>{stats.get('median', 0):,.2f}</td>
                                <td>{stats.get('std', 0):,.2f}</td>
                                <td>{stats.get('min', 0):,.2f}</td>
                                <td>{stats.get('max', 0):,.2f}</td>
                            </tr>
                            """
                    
                    html += '</table>'
            
            # 상관분석
            if 'correlation_analysis' in report:
                corr_analysis = report['correlation_analysis']
                if 'error' not in corr_analysis:
                    html += "<h2>🔗 상관관계 분석</h2>"
                    
                    if 'correlations' in corr_analysis:
                        correlations = corr_analysis['correlations']
                        for rel_name, rel_data in correlations.items():
                            correlation_val = rel_data.get('correlation', 0)
                            strength = rel_data.get('strength', '알 수 없음')
                            interpretation = rel_data.get('interpretation', '해석 없음')
                            
                            # 상관관계 강도에 따른 색상 클래스
                            if abs(correlation_val) >= 0.7:
                                corr_class = "correlation-strong"
                            elif abs(correlation_val) >= 0.3:
                                corr_class = "correlation-moderate"
                            else:
                                corr_class = "correlation-weak"
                            
                            html += f"""
                            <div class="metric">
                                <strong>{rel_name.replace('_', ' & ')}:</strong> 
                                <span class="{corr_class}">{correlation_val:.3f} ({strength})</span><br>
                                <small>{interpretation}</small>
                            </div>
                            """
                    
                    if 'summary' in corr_analysis:
                        html += f'<div class="metric"><strong>요약:</strong> {corr_analysis["summary"]}</div>'
            
            # 그룹 비교 분석
            if 'group_comparison' in report:
                group_comp = report['group_comparison']
                if 'error' not in group_comp:
                    html += "<h2>� 그룹 비교 분석</h2>"
                    
                    if 'duration_analysis' in group_comp:
                        duration = group_comp['duration_analysis']
                        html += "<h3>⏱️ 영상 길이별 성과</h3>"
                        
                        if 'groups' in duration:
                            for group_name, group_data in duration['groups'].items():
                                html += f"""
                                <div class="metric">
                                    <strong>{group_name}:</strong> 
                                    평균 조회수 {group_data.get('avg_views', 0):,.0f}, 
                                    평균 참여도 {group_data.get('avg_engagement', 0):.4f}
                                </div>
                                """
                        
                        if 'insights' in duration:
                            for insight in duration['insights']:
                                html += f'<div class="metric">💡 {insight}</div>'
            
            # 상위 성과 분석
            if 'top_analysis' in report:
                top_analysis = report['top_analysis']
                if 'error' not in top_analysis:
                    html += "<h2>🏆 상위 성과 분석</h2>"
                    
                    if 'top_videos' in top_analysis:
                        top_videos = top_analysis['top_videos']
                        html += "<h3>🔥 조회수 상위 영상</h3>"
                        html += '<table class="stats-table">'
                        html += '<tr><th>제목</th><th>조회수</th><th>좋아요</th><th>댓글</th><th>참여도</th></tr>'
                        
                        for video in top_videos[:5]:  # 상위 5개만 표시
                            html += f"""
                            <tr>
                                <td>{video.get('title', 'N/A')[:50]}{'...' if len(video.get('title', '')) > 50 else ''}</td>
                                <td>{video.get('view_count', 0):,}</td>
                                <td>{video.get('like_count', 0):,}</td>
                                <td>{video.get('comment_count', 0):,}</td>
                                <td>{video.get('engagement_rate', 0):.4f}</td>
                            </tr>
                            """
                        
                        html += '</table>'
                    
                    if 'characteristics' in top_analysis:
                        characteristics = top_analysis['characteristics']
                        html += "<h3>📋 상위 영상 특성</h3>"
                        html += f"""
                        <div class="metric">평균 영상 길이: <span class="highlight">{characteristics.get('avg_duration', 0):.0f}초</span></div>
                        <div class="metric">평균 제목 길이: <span class="highlight">{characteristics.get('avg_title_length', 0):.0f}자</span></div>
                        <div class="metric">평균 참여도: <span class="highlight">{characteristics.get('avg_engagement_rate', 0):.4f}</span></div>
                        """
            
            html += """
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            return f"<html><body><h1>보고서 생성 오류</h1><p>{str(e)}</p></body></html>"


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    
    # 애플리케이션 정보 설정
    app.setApplicationName("YouTube 트렌드 판별기")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("YouTube Trend Analyzer")
    
    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())