# YouTube 트렌드 판별기 설치 및 실행 가이드

## 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [설치 방법](#설치-방법)
3. [API 키 설정](#api-키-설정)
4. [실행 방법](#실행-방법)
5. [사용법](#사용법)
6. [문제 해결](#문제-해결)
7. [빌드 방법](#빌드-방법)

## 🖥️ 시스템 요구사항

### 최소 요구사항
- **운영체제**: Windows 10 이상, macOS 10.14 이상, Ubuntu 18.04 이상
- **Python**: 3.8 이상 (소스 코드 실행 시)
- **메모리**: 4GB RAM 이상
- **저장공간**: 500MB 이상 여유 공간
- **인터넷 연결**: YouTube API 호출을 위해 필요

### 권장 사양
- **Python**: 3.9 또는 3.10
- **메모리**: 8GB RAM 이상
- **인터넷**: 안정적인 브로드밴드 연결

## 🚀 설치 방법

### 방법 1: 실행 파일 사용 (권장)
1. [Releases](https://github.com/your-repo/releases) 페이지에서 최신 버전 다운로드
2. 압축 해제 후 `YouTube_트렌드_판별기.exe` 실행
3. [API 키 설정](#api-키-설정) 진행

### 방법 2: 소스 코드 실행

#### Windows
```bash
# 1. 저장소 클론
git clone https://github.com/your-repo/youtubepy.git
cd youtubepy

# 2. 가상환경 생성 (권장)
python -m venv venv
venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 실행
python src/main.py
```

#### macOS/Linux
```bash
# 1. 저장소 클론
git clone https://github.com/your-repo/youtubepy.git
cd youtubepy

# 2. 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 실행
python src/main.py
```

## 🔑 API 키 설정

### 1. Google Cloud Console에서 API 키 발급

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스** → **라이브러리** 이동
4. **YouTube Data API v3** 검색 후 활성화
5. **API 및 서비스** → **사용자 인증 정보** 이동
6. **사용자 인증 정보 만들기** → **API 키** 선택
7. 생성된 API 키 복사

### 2. 설정 파일에 API 키 입력

`config/config.json` 파일을 열고 API 키를 입력:

```json
{
    "youtube_api_key": "여기에_발급받은_API_키_입력",
    "default_max_results": 50,
    "default_video_duration": "any",
    "default_published_after": "",
    "default_published_before": ""
}
```

⚠️ **주의사항**:
- API 키는 절대 공개하지 마세요
- 일일 할당량이 있으므로 과도한 요청은 피하세요
- API 키에 적절한 제한사항을 설정하세요

## ▶️ 실행 방법

### 실행 파일 사용
1. `YouTube_트렌드_판별기.exe` 더블클릭
2. 또는 명령 프롬프트에서:
   ```cmd
   YouTube_트렌드_판별기.exe
   ```

### 소스 코드 실행
```bash
# 가상환경 활성화 (가상환경 사용 시)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 프로그램 실행
python src/main.py
```

## 📖 사용법

### 1. 기본 검색
1. **검색어** 입력 (예: "파이썬", "요리", "게임")
2. **검색 조건** 설정:
   - 최대 결과 수 (1-50)
   - 영상 길이 (전체/숏폼/미디엄/롱폼)
   - 정렬 방식 (관련성/최신순/조회수/평점/제목)
   - 검색 기간 설정
3. **검색 실행** 버튼 클릭

### 2. 인기 급상승 영상
- **인기 급상승 영상** 버튼으로 현재 트렌딩 영상 확인

### 3. 결과 분석
- **검색 결과** 탭: 상세 데이터 테이블
- **통계 분석** 탭: 요약 통계 및 상위 성과 영상

### 4. 필터링
검색 결과에서 추가 필터링:
- 키워드로 제목/태그 검색
- 최소 조회수 설정
- 숏폼/롱폼만 보기

### 5. 데이터 내보내기
- **CSV로 내보내기**: 스프레드시트 프로그램에서 열기
- **Excel로 내보내기**: Microsoft Excel에서 바로 열기

### 6. 영상 바로가기
- 테이블의 영상 제목 더블클릭으로 YouTube에서 바로 열기

## 🔧 문제 해결

### 자주 발생하는 문제

#### 1. "API 키가 설정되지 않았습니다" 오류
**해결책**:
- `config/config.json` 파일에서 API 키 확인
- API 키가 올바르게 입력되었는지 확인
- YouTube Data API v3가 활성화되었는지 확인

#### 2. "YouTube API 오류" 메시지
**원인 및 해결책**:
- **할당량 초과**: 24시간 후 재시도 또는 할당량 증가 요청
- **API 키 제한**: Google Cloud Console에서 API 키 제한사항 확인
- **네트워크 오류**: 인터넷 연결 확인

#### 3. 프로그램이 실행되지 않음 (실행 파일)
**해결책**:
- Windows Defender나 백신 프로그램에서 차단 여부 확인
- 관리자 권한으로 실행
- Visual C++ 재배포 패키지 설치

#### 4. 패키지 설치 오류 (소스 코드)
**해결책**:
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 개별 패키지 설치
pip install PyQt5
pip install google-api-python-client
pip install pandas
pip install openpyxl
```

#### 5. 한글 깨짐 현상
**해결책**:
- 시스템 로케일을 한국어로 설정
- CSV 파일을 Excel에서 열 때 UTF-8 인코딩 선택

### 로그 확인
문제 발생 시 다음 위치에서 로그 확인:
- Windows: `%APPDATA%\YouTube_트렌드_판별기\logs\`
- macOS: `~/Library/Application Support/YouTube_트렌드_판별기/logs/`
- Linux: `~/.local/share/YouTube_트렌드_판별기/logs/`

## 🛠️ 빌드 방법

### 개발 환경 설정
```bash
# 저장소 클론
git clone https://github.com/your-repo/youtubepy.git
cd youtubepy

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 개발 의존성 설치
pip install -r requirements.txt
pip install pyinstaller
```

### 실행 파일 빌드

#### Windows
```cmd
# 자동 빌드 스크립트 실행
build.bat

# 또는 수동 빌드
pyinstaller youtube_trend_analyzer.spec
```

#### macOS/Linux
```bash
# 자동 빌드 스크립트 실행 (실행 권한 부여 후)
chmod +x build.sh
./build.sh

# 또는 수동 빌드
pyinstaller youtube_trend_analyzer.spec
```

### 빌드 결과
- 실행 파일: `dist/YouTube_트렌드_판별기.exe` (Windows)
- 실행 파일: `dist/YouTube_트렌드_판별기` (macOS/Linux)

## 📞 지원

### 도움이 필요한 경우
1. [Issues](https://github.com/your-repo/issues) 페이지에서 기존 문제 검색
2. 새로운 이슈 생성 시 다음 정보 포함:
   - 운영체제 및 버전
   - Python 버전 (소스 코드 실행 시)
   - 오류 메시지 전문
   - 재현 단계

### 기능 요청
- [Issues](https://github.com/your-repo/issues) 페이지에서 `enhancement` 라벨로 요청

### 기여하기
1. 저장소 포크
2. 기능 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

---

**📌 참고**: 이 프로그램은 YouTube Data API v3를 사용하므로 Google의 [API 사용 정책](https://developers.google.com/youtube/terms/api-services-terms-of-service)을 준수해야 합니다.