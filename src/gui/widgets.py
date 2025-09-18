"""
커스텀 위젯 모듈
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QLineEdit, QComboBox, QSpinBox,
                           QCheckBox, QGroupBox, QFrame, QDialog, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QPixmap
from typing import Dict, Any
import requests


class ThumbnailViewer(QDialog):
    """썸네일 뷰어 다이얼로그"""
    
    def __init__(self, video_data: Dict, parent=None):
        super().__init__(parent)
        self.video_data = video_data
        self.init_ui()
        self.load_thumbnail()
    
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle(f"썸네일 미리보기 - {self.video_data.get('title', '알 수 없음')}")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout(self)
        
        # 영상 정보
        info_group = QGroupBox("영상 정보")
        info_layout = QVBoxLayout(info_group)
        
        title_label = QLabel(f"제목: {self.video_data.get('title', '알 수 없음')}")
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(title_label)
        
        channel_label = QLabel(f"채널: {self.video_data.get('channel_title', '알 수 없음')}")
        info_layout.addWidget(channel_label)
        
        views_label = QLabel(f"조회수: {self.video_data.get('view_count', 0):,}회")
        info_layout.addWidget(views_label)
        
        likes_label = QLabel(f"좋아요: {self.video_data.get('like_count', 0):,}개")
        info_layout.addWidget(likes_label)
        
        layout.addWidget(info_group)
        
        # 썸네일 표시 영역
        thumbnail_group = QGroupBox("썸네일")
        thumbnail_layout = QVBoxLayout(thumbnail_group)
        
        self.thumbnail_label = QLabel("썸네일 로딩 중...")
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setMinimumSize(480, 360)
        self.thumbnail_label.setStyleSheet("border: 1px solid gray;")
        thumbnail_layout.addWidget(self.thumbnail_label)
        
        layout.addWidget(thumbnail_group)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        
        youtube_button = QPushButton("YouTube에서 보기")
        youtube_button.clicked.connect(self.open_youtube)
        youtube_button.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #CC0000;
            }
        """)
        button_layout.addWidget(youtube_button)
        
        close_button = QPushButton("닫기")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def load_thumbnail(self):
        """썸네일 로드"""
        thumbnail_url = self.video_data.get('thumbnail_url', '')
        
        if thumbnail_url:
            # 고화질 썸네일 URL로 변경 시도
            video_id = self.video_data.get('video_id', '')
            if video_id:
                # YouTube 고화질 썸네일 URL들
                hq_urls = [
                    f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                    f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                    thumbnail_url  # 원본 URL
                ]
                
                for url in hq_urls:
                    try:
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            pixmap = QPixmap()
                            pixmap.loadFromData(response.content)
                            
                            if not pixmap.isNull():
                                # 적절한 크기로 스케일링
                                scaled_pixmap = pixmap.scaled(480, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                self.thumbnail_label.setPixmap(scaled_pixmap)
                                return
                    except:
                        continue
            
            # 모든 시도 실패시
            self.thumbnail_label.setText("썸네일을 불러올 수 없습니다.")
        else:
            self.thumbnail_label.setText("썸네일 URL이 없습니다.")
    
    def open_youtube(self):
        """YouTube에서 영상 열기"""
        video_url = self.video_data.get('video_url', '')
        if video_url:
            import webbrowser
            webbrowser.open(video_url)


class ApiKeyDialog(QDialog):
    """API 키 설정 다이얼로그"""
    
    api_key_changed = pyqtSignal(str)  # API 키 변경 시그널
    
    def __init__(self, current_api_key: str = "", parent=None):
        super().__init__(parent)
        self.current_api_key = current_api_key
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("YouTube API 키 설정")
        self.setGeometry(300, 300, 500, 200)
        
        layout = QVBoxLayout(self)
        
        # 설명
        desc_label = QLabel("""
YouTube Data API v3 키를 설정해주세요.

API 키 발급 방법:
1. Google Cloud Console (https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. YouTube Data API v3 활성화
4. 사용자 인증 정보에서 API 키 생성
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # API 키 입력
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API 키:"))
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.current_api_key)
        self.api_key_input.setPlaceholderText("여기에 YouTube Data API v3 키를 입력하세요")
        api_key_layout.addWidget(self.api_key_input)
        
        layout.addLayout(api_key_layout)
        
        # 버튼
        button_layout = QHBoxLayout()
        
        test_button = QPushButton("연결 테스트")
        test_button.clicked.connect(self.test_api_key)
        button_layout.addWidget(test_button)
        
        save_button = QPushButton("저장")
        save_button.clicked.connect(self.save_api_key)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("취소")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 상태 라벨
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
    
    def test_api_key(self):
        """API 키 연결 테스트"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            self.status_label.setText("❌ API 키를 입력해주세요.")
            self.status_label.setStyleSheet("color: red;")
            return
        
        self.status_label.setText("🔄 연결 테스트 중...")
        self.status_label.setStyleSheet("color: blue;")
        
        try:
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # 간단한 테스트 요청
            response = youtube.search().list(
                part='snippet',
                q='test',
                maxResults=1,
                type='video'
            ).execute()
            
            self.status_label.setText("✅ API 키가 정상적으로 작동합니다!")
            self.status_label.setStyleSheet("color: green;")
            
        except Exception as e:
            self.status_label.setText(f"❌ API 키 오류: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
    
    def save_api_key(self):
        """API 키 저장"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            self.status_label.setText("❌ API 키를 입력해주세요.")
            self.status_label.setStyleSheet("color: red;")
            return
        
        # 시그널 발송
        self.api_key_changed.emit(api_key)
        self.accept()


class CountrySelector(QComboBox):
    """국가 선택 콤보박스"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_countries()
    
    def init_countries(self):
        """국가 목록 초기화"""
        countries = [
            ("전 세계", ""),
            ("한국", "KR"),
            ("미국", "US"),
            ("일본", "JP"),
            ("중국", "CN"),
            ("영국", "GB"),
            ("독일", "DE"),
            ("프랑스", "FR"),
            ("캐나다", "CA"),
            ("호주", "AU"),
            ("브라질", "BR"),
            ("인도", "IN"),
            ("러시아", "RU"),
            ("이탈리아", "IT"),
            ("스페인", "ES"),
            ("네덜란드", "NL"),
            ("스웨덴", "SE"),
            ("노르웨이", "NO"),
            ("태국", "TH"),
            ("베트남", "VN"),
            ("필리핀", "PH"),
            ("인도네시아", "ID"),
            ("말레이시아", "MY"),
            ("싱가포르", "SG"),
            ("터키", "TR"),
            ("멕시코", "MX"),
            ("아르헨티나", "AR"),
        ]
        
        for name, code in countries:
            self.addItem(name, code)


class FilterWidget(QWidget):
    """필터링을 위한 커스텀 위젯"""
    
    filters_changed = pyqtSignal(dict)  # 필터 변경 시그널
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 필터 그룹박스
        filter_group = QGroupBox("필터 조건")
        filter_layout = QVBoxLayout(filter_group)
        
        # 키워드 필터
        keyword_layout = QHBoxLayout()
        keyword_layout.addWidget(QLabel("키워드:"))
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText("제목이나 태그에서 검색...")
        keyword_layout.addWidget(self.keyword_edit)
        filter_layout.addLayout(keyword_layout)
        
        # 조회수 범위
        views_layout = QHBoxLayout()
        views_layout.addWidget(QLabel("조회수 범위:"))
        
        self.min_views = QSpinBox()
        self.min_views.setRange(0, 999999999)
        self.min_views.setSuffix(" 회")
        views_layout.addWidget(QLabel("최소:"))
        views_layout.addWidget(self.min_views)
        
        self.max_views = QSpinBox()
        self.max_views.setRange(0, 999999999)
        self.max_views.setValue(999999999)
        self.max_views.setSuffix(" 회")
        views_layout.addWidget(QLabel("최대:"))
        views_layout.addWidget(self.max_views)
        
        filter_layout.addLayout(views_layout)
        
        # 영상 길이 필터
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("영상 길이:"))
        
        self.short_only = QCheckBox("숏폼만 (60초 이하)")
        self.long_only = QCheckBox("롱폼만 (60초 초과)")
        duration_layout.addWidget(self.short_only)
        duration_layout.addWidget(self.long_only)
        
        filter_layout.addLayout(duration_layout)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        
        apply_button = QPushButton("필터 적용")
        apply_button.clicked.connect(self.apply_filters)
        button_layout.addWidget(apply_button)
        
        clear_button = QPushButton("초기화")
        clear_button.clicked.connect(self.clear_filters)
        button_layout.addWidget(clear_button)
        
        filter_layout.addLayout(button_layout)
        
        layout.addWidget(filter_group)
        
        # 이벤트 연결
        self.keyword_edit.textChanged.connect(self.on_filter_changed)
        self.min_views.valueChanged.connect(self.on_filter_changed)
        self.max_views.valueChanged.connect(self.on_filter_changed)
        self.short_only.toggled.connect(self.on_duration_filter_changed)
        self.long_only.toggled.connect(self.on_duration_filter_changed)
    
    def on_duration_filter_changed(self):
        """영상 길이 필터 상호 배타적 처리"""
        sender = self.sender()
        
        if sender == self.short_only and self.short_only.isChecked():
            self.long_only.setChecked(False)
        elif sender == self.long_only and self.long_only.isChecked():
            self.short_only.setChecked(False)
        
        self.on_filter_changed()
    
    def on_filter_changed(self):
        """필터 변경 시 자동 적용 (옵션)"""
        pass  # 실시간 필터링을 원하지 않으므로 비워둠
    
    def apply_filters(self):
        """필터 적용"""
        filters = self.get_filter_values()
        self.filters_changed.emit(filters)
    
    def clear_filters(self):
        """필터 초기화"""
        self.keyword_edit.clear()
        self.min_views.setValue(0)
        self.max_views.setValue(999999999)
        self.short_only.setChecked(False)
        self.long_only.setChecked(False)
        
        # 빈 필터로 시그널 발송
        self.filters_changed.emit({})
    
    def get_filter_values(self) -> Dict[str, Any]:
        """현재 필터 값 반환"""
        filters = {}
        
        if self.keyword_edit.text().strip():
            filters['keyword'] = self.keyword_edit.text().strip()
        
        if self.min_views.value() > 0:
            filters['min_views'] = self.min_views.value()
        
        if self.max_views.value() < 999999999:
            filters['max_views'] = self.max_views.value()
        
        if self.short_only.isChecked():
            filters['short_form_only'] = True
        elif self.long_only.isChecked():
            filters['long_form_only'] = True
        
        return filters


class SearchStatsWidget(QWidget):
    """검색 통계 표시 위젯"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 통계 그룹박스
        stats_group = QGroupBox("검색 통계")
        stats_layout = QVBoxLayout(stats_group)
        
        # 통계 레이블들
        self.total_label = QLabel("총 영상 수: 0개")
        self.short_label = QLabel("숏폼: 0개")
        self.long_label = QLabel("롱폼: 0개")
        self.avg_views_label = QLabel("평균 조회수: 0회")
        self.max_views_label = QLabel("최대 조회수: 0회")
        
        # 폰트 설정
        font = QFont()
        font.setPointSize(10)
        
        for label in [self.total_label, self.short_label, self.long_label, 
                     self.avg_views_label, self.max_views_label]:
            label.setFont(font)
            stats_layout.addWidget(label)
        
        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        stats_layout.addWidget(line)
        
        layout.addWidget(stats_group)
    
    def update_stats(self, stats: Dict[str, Any]):
        """통계 정보 업데이트"""
        self.total_label.setText(f"총 영상 수: {stats.get('total_videos', 0):,}개")
        self.short_label.setText(f"숏폼: {stats.get('short_form_count', 0):,}개")
        self.long_label.setText(f"롱폼: {stats.get('long_form_count', 0):,}개")
        self.avg_views_label.setText(f"평균 조회수: {stats.get('avg_views', 0):,.0f}회")
        self.max_views_label.setText(f"최대 조회수: {stats.get('max_views', 0):,}회")
    
    def clear_stats(self):
        """통계 정보 초기화"""
        self.total_label.setText("총 영상 수: 0개")
        self.short_label.setText("숏폼: 0개")
        self.long_label.setText("롱폼: 0개")
        self.avg_views_label.setText("평균 조회수: 0회")
        self.max_views_label.setText("최대 조회수: 0회")


class QuickSearchWidget(QWidget):
    """빠른 검색을 위한 위젯"""
    
    search_requested = pyqtSignal(str, dict)  # 검색 요청 시그널
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 빠른 검색 그룹박스
        quick_group = QGroupBox("빠른 검색")
        quick_layout = QVBoxLayout(quick_group)
        
        # 인기 키워드 버튼들
        keywords = [
            "shorts", "음악", "게임", "먹방", "브이로그", 
            "리뷰", "튜토리얼", "뉴스", "스포츠", "코미디"
        ]
        
        button_layout = QHBoxLayout()
        for i, keyword in enumerate(keywords):
            if i % 5 == 0 and i > 0:  # 5개씩 한 줄
                quick_layout.addLayout(button_layout)
                button_layout = QHBoxLayout()
            
            button = QPushButton(keyword)
            button.clicked.connect(lambda checked, k=keyword: self.quick_search(k))
            button_layout.addWidget(button)
        
        quick_layout.addLayout(button_layout)
        
        layout.addWidget(quick_group)
    
    def quick_search(self, keyword: str):
        """빠른 검색 실행"""
        # 기본 검색 옵션
        options = {
            'max_results': 20,
            'video_duration': 'any',
            'order': 'relevance'
        }
        
        self.search_requested.emit(keyword, options)