"""
YouTube 트렌드 판별기 메인 실행 파일
"""

import sys
import os

# src 디렉토리를 Python 경로에 추가
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

def main():
    """메인 함수"""
    try:
        # PyQt5 import 확인
        from PyQt5.QtWidgets import QApplication, QMessageBox
        from PyQt5.QtCore import Qt
        
        # 고해상도 디스플레이 지원 (QApplication 생성 전에 설정)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Qt 애플리케이션 생성
        app = QApplication(sys.argv)
        
        # GUI 모듈 import
        from gui.main_window import MainWindow
        
        # 애플리케이션 정보 설정
        app.setApplicationName("YouTube 트렌드 판별기")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("YouTube Trend Analyzer")
        app.setOrganizationDomain("youtube-trend-analyzer.com")
        
        # 애플리케이션 스타일 설정
        app.setStyle('Fusion')  # 모던한 스타일
        
        # 메인 윈도우 생성
        try:
            window = MainWindow()
            window.show()
            
            # 메시지 루프 시작
            sys.exit(app.exec_())
            
        except Exception as e:
            # GUI 생성 오류
            error_msg = f"GUI 초기화 중 오류가 발생했습니다:\n{str(e)}"
            
            if 'app' in locals():
                QMessageBox.critical(None, "초기화 오류", error_msg)
            else:
                print(f"오류: {error_msg}")
            
            sys.exit(1)
            
    except ImportError as e:
        # PyQt5 import 오류
        error_msg = f"""
필요한 패키지가 설치되지 않았습니다:
{str(e)}

다음 명령어로 필요한 패키지를 설치해주세요:
pip install -r requirements.txt
        """
        print(error_msg)
        sys.exit(1)
        
    except Exception as e:
        # 기타 오류
        error_msg = f"프로그램 실행 중 오류가 발생했습니다:\n{str(e)}"
        print(f"오류: {error_msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()