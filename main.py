"""
YouTube 트렌드 판별기 메인 실행 파일
"""

import sys
import os

# PyInstaller와 일반 실행 모두 지원하는 경로 설정
def get_resource_path():
    """리소스 파일의 절대 경로를 반환 (PyInstaller 호환)"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller로 빌드된 경우
        return sys._MEIPASS
    else:
        # 일반 Python 실행의 경우
        return os.path.dirname(os.path.abspath(__file__))

def get_src_path():
    """src 디렉토리 경로를 반환"""
    base_dir = get_resource_path()
    
    # PyInstaller 빌드된 경우와 일반 실행 구분
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller로 빌드된 경우 - src 폴더가 _MEIPASS 안에 있음
        src_path = os.path.join(base_dir, 'src')
        if not os.path.exists(src_path):
            # src가 _MEIPASS 루트에 직접 있을 수도 있음
            src_path = base_dir
    else:
        # 일반 실행의 경우
        src_path = os.path.join(base_dir, 'src')
    
    return src_path

# src 디렉토리를 Python 경로에 추가
src_dir = get_src_path()
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
        
        # GUI 모듈 import (디버깅 정보 추가)
        try:
            # 디버깅 정보 출력
            print(f"디버깅 정보:")
            print(f"- PyInstaller 빌드 여부: {hasattr(sys, '_MEIPASS')}")
            print(f"- 리소스 경로: {get_resource_path()}")
            print(f"- src 경로: {src_dir}")
            print(f"- src 경로 존재 여부: {os.path.exists(src_dir)}")
            print(f"- 현재 Python 경로: {sys.path[:3]}...")  # 처음 3개만 출력
            
            if os.path.exists(src_dir):
                print(f"- src 디렉토리 내용: {os.listdir(src_dir)}")
                gui_path = os.path.join(src_dir, 'gui')
                if os.path.exists(gui_path):
                    print(f"- gui 디렉토리 내용: {os.listdir(gui_path)}")
            
            from gui.main_window import MainWindow
            print("✅ GUI 모듈 import 성공")
            
        except ImportError as import_error:
            error_msg = f"GUI 모듈 import 오류: {import_error}"
            print(error_msg)
            
            # 자세한 디버깅 정보
            print(f"\n상세 디버깅 정보:")
            print(f"- 현재 작업 디렉토리: {os.getcwd()}")
            print(f"- __file__ 경로: {__file__ if '__file__' in globals() else 'N/A'}")
            print(f"- sys.executable: {sys.executable}")
            
            # 오류 메시지 박스로 표시
            if 'app' in locals():
                QMessageBox.critical(None, "Import 오류", error_msg)
            
            sys.exit(1)
        
        # 애플리케이션 정보 설정
        app.setApplicationName("YouTube 트렌드 판별기")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("YouTube Trend Analyzer")
        app.setOrganizationDomain("youtube-trend-analyzer.com")
        
        # 애플리케이션 스타일 설정
        app.setStyle('Fusion')  # 모던한 스타일
        
        # 메인 윈도우 생성
        try:
            print("🔄 MainWindow 객체 생성 중...")
            window = MainWindow()
            print("✅ MainWindow 객체 생성 완료")
            
            print("🔄 윈도우 표시 중...")
            window.show()
            print("✅ 윈도우 표시 완료")
            
            print("🔄 메시지 루프 시작...")
            # 메시지 루프 시작
            sys.exit(app.exec_())
            
        except Exception as e:
            # GUI 생성 오류
            import traceback
            error_msg = f"GUI 초기화 중 오류가 발생했습니다:\n{str(e)}\n\n상세 오류:\n{traceback.format_exc()}"
            print(f"❌ GUI 오류: {error_msg}")
            
            if 'app' in locals():
                QMessageBox.critical(None, "초기화 오류", error_msg)
            
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