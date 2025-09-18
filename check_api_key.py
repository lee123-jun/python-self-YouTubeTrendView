#!/usr/bin/env python3
"""
YouTube API 키 사용 현황 확인 스크립트
"""

import sys
import os
import json

# 프로젝트 경로를 sys.path에 추가
project_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def check_config_file():
    """config.json 파일의 API 키 확인"""
    config_path = os.path.join(project_root, 'config', 'config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        api_key = config.get('youtube_api_key', '')
        print(f"📄 Config 파일의 API 키: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else api_key}")
        return api_key
    except FileNotFoundError:
        print("❌ config.json 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"❌ Config 파일 읽기 오류: {e}")
        return None

def test_youtube_api_initialization():
    """YouTubeAPI 클래스 초기화 테스트"""
    try:
        from youtube_api import YouTubeAPI
        
        # YouTubeAPI 초기화 (config 파일에서 API 키 로드)
        youtube_api = YouTubeAPI()
        
        print(f"🔑 YouTubeAPI에서 사용 중인 API 키: {youtube_api.api_key[:20]}...{youtube_api.api_key[-10:] if len(youtube_api.api_key) > 30 else youtube_api.api_key}")
        
        # 간단한 API 테스트
        print("🧪 API 연결 테스트 중...")
        result = youtube_api.search_videos("test", max_results=1)
        
        if result:
            print("✅ API 키가 정상적으로 작동합니다!")
            print(f"   테스트 결과: {len(result)}개 영상 검색됨")
            if result:
                print(f"   첫 번째 영상: {result[0].get('title', 'N/A')}")
        else:
            print("⚠️ 검색 결과가 없습니다.")
            
        return True
        
    except ValueError as e:
        print(f"❌ API 키 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ YouTubeAPI 초기화 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("=== YouTube API 키 사용 현황 확인 ===\n")
    
    # 1. Config 파일 확인
    print("1️⃣ Config 파일 API 키 확인:")
    config_api_key = check_config_file()
    
    print("\n" + "="*50 + "\n")
    
    # 2. YouTubeAPI 클래스 초기화 확인
    print("2️⃣ YouTubeAPI 클래스 초기화 확인:")
    api_success = test_youtube_api_initialization()
    
    print("\n" + "="*50 + "\n")
    
    # 3. 결론
    print("📋 결론:")
    if config_api_key and api_success:
        print("✅ 프로그램은 config.json 파일의 API 키를 사용하여 YouTube 데이터를 수집합니다.")
        print("📌 GUI에서 API 키를 변경하면 config.json 파일이 업데이트되고,")
        print("   이후 모든 검색에서 새로운 API 키가 사용됩니다.")
    else:
        print("❌ API 키 설정에 문제가 있습니다.")
        
    print(f"\n현재 사용 중인 API 키: {config_api_key[:20]}...{config_api_key[-10:] if config_api_key and len(config_api_key) > 30 else config_api_key}")

if __name__ == "__main__":
    main()