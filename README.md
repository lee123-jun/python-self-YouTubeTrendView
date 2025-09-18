# YouTube 트렌드 판별기

**Python 기반 YouTube Data API를 활용한 영상 데이터 수집 및 트렌드 분석 도구**

YouTube Data API v3를 통해 영상 데이터를 수집하고, PyQt 기반 GUI로 분석할 수 있는 트렌드 분석 프로그램입니다. 영상 데이터를 수집해 트렌드 주제, 인기 지표, 참여도(좋아요·댓글 등)에 대한 빠른 분석이 가능합니다!

## ✨ 주요 기능

### 🔍 강력한 검색 기능
- **키워드 기반 검색**: 원하는 주제의 영상 검색
- **연령층 타겟팅**: 어린이부터 장년층까지 7단계 연령별 맞춤 검색
- **고급 필터링**: 영상 길이(숏폼/롱폼), 업로드 기간, 정렬 방식, 국가별 검색
- **대용량 수집**: 최대 100개 영상 수집 지원 (페이지네이션 자동 처리)
- **인기 급상승**: 현재 트렌딩 영상 실시간 확인

### 📈 상세 데이터 분석
- **핵심 지표**: 조회수, 좋아요, 댓글 수, 참여율
- **영상 분류**: 숏폼(60초 이하) vs 롱폼 자동 구분

### 🎯 스마트 필터링
- **실시간 필터**: 검색 결과에서 추가 조건으로 필터링
- **연령층 기반 필터링**: AI 기반 콘텐츠 적합성 분석
- **조회수 범위**: 최소/최대 조회수로 구간 설정
- **키워드 매칭**: 제목, 태그에서 특정 키워드 검색
- **국가별 검색**: 전 세계 주요 국가별 트렌드 분석

### 📊 통계 분석
- **기본 통계**: 평균, 중간값, 최댓값 등 기본 통계
- **상위 성과**: Top 10 영상 자동 추출
- **카테고리 분석**: 숏폼/롱폼 비율 및 성과 비교
- **실용적 분석**:
  - � **상관관계 분석**: 조회수↔좋아요, 조회수↔댓글 상관관계 분석
  - � **그룹 비교 분석**: 요일별, 영상 길이별 성과 비교
  - � **상위 성과 분석**: 파레토 법칙(80/20) 적용한 핵심 콘텐츠 식별

### 💾 데이터 내보내기
- **CSV 형식**: 스프레드시트 프로그램에서 활용

### 🖱️ 사용자 친화적 GUI
- **직관적 인터페이스**: 복잡한 설정 없이 바로 사용
- **실시간 미리보기**: 검색 진행상황 표시
- **YouTube 연동**: 영상 더블클릭으로 바로 재생
- **썸네일 뷰어**: 영상 썸네일 미리보기 기능
- **API 키 관리**: GUI 내에서 API 키 설정 및 관리
- **다국가 지원**: 전 세계 주요 국가 선택 가능

## 🚀 빠른 시작

### 1️⃣ 실행 파일 다운로드 (권장)
```
1. Releases 페이지에서 최신 버전 다운로드
2. 압축 해제 후 YouTube_트렌드_판별기.exe 실행
3. API 키 설정 후 바로 사용
```

### 2️⃣ 소스 코드 실행
```bash
# 저장소 클론
git clone https://github.com/your-username/youtubepy.git
cd youtubepy

# 의존성 설치
pip install -r requirements.txt

# 프로그램 실행
python src/main.py
```

## 🔑 API 키 설정

### 1. Google Cloud Console 설정
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. **YouTube Data API v3** 활성화
4. **API 키** 생성

### 2. 설정 파일 수정
`config/config.json` 파일의 API 키 변경:
```json
{
    "youtube_api_key": "여기에_발급받은_API_키_입력"
}
```

## 📖 사용법

### 기본 검색
1. **검색어 입력** (예: "파이썬 강의", "요리 레시피")
2. **조건 설정**: 
   - 영상 길이 (숏폼/롱폼)
   - 발행 기간
   - 정렬 방식 
   - 연령층 타겟 (어린이/청소년/청년/성인/중년/장년)
   - 국가 선택
   - 최대 수집 개수 (1~100개)
3. **검색 실행** 버튼 클릭
4. **결과 분석**: 테이블에서 데이터 확인

### 고급 활용
- **필터링**: 검색 후 추가 조건으로 세부 분석
- **정렬**: 컬럼 헤더 클릭으로 원하는 기준 정렬
- **내보내기**: CSV로 데이터 저장
- **YouTube 연동**: 영상 제목 더블클릭으로 바로 재생
- **썸네일 미리보기**: 영상 썸네일 확인
- **고급 통계 분석**: AI 기반 트렌드 예측 및 성과 분석 리포트

## 🛠️ 빌드 방법

### Windows
```cmd
# 자동 빌드
build.bat

# 수동 빌드
pip install pyinstaller
pyinstaller youtube_trend_analyzer.spec
```

## 📁 프로젝트 구조
```
youtubepy/
├── src/
│   ├── gui/
│   │   ├── main_window.py         # 메인 GUI 클래스
│   │   ├── widgets.py             # 커스텀 위젯들
│   │   └── __init__.py
│   ├── data_processor.py          # 데이터 처리 모듈
│   ├── statistical_analysis.py   # 통계 분석 모듈
│   ├── youtube_api.py             # YouTube API 연동
│   ├── utils.py                   # 유틸리티 함수들
│   └── __init__.py
├── config/
│   ├── config.json                # 사용자 설정 (생성됨)
│   └── config_template.json       # 설정 템플릿
├── main.py                        # 프로그램 진입점
├── requirements.txt               # 패키지 의존성
├── build.bat                      # Windows 빌드 스크립트
├── youtube_trend_analyzer.spec    # PyInstaller 설정
├── README.md                      # 프로젝트 문서
├── INSTALLATION.md                # 설치 가이드
└── .gitignore                     # Git 무시 파일
│   ├── main.py              # 메인 실행 파일
│   ├── youtube_api.py       # YouTube API 연동
│   ├── data_processor.py    # 데이터 처리 및 분석
│   ├── statistical_analysis.py # 고급 통계 분석 모듈
│   ├── utils.py            # 유틸리티 함수
│   └── gui/
│       ├── main_window.py   # 메인 GUI
│       └── widgets.py       # 커스텀 위젯 (썸네일뷰어, API키관리, 국가선택)
├── config/
│   ├── config.json          # 설정 파일
│   └── config_template.json # 설정 템플릿
├── output/                  # 내보내기 파일 저장
├── build.bat               # Windows 빌드 스크립트
├── build.sh                # Linux/macOS 빌드 스크립트
├── requirements.txt        # Python 의존성
├── youtube_trend_analyzer.spec # PyInstaller 설정
├── README.md               # 프로젝트 소개
└── INSTALLATION.md         # 상세 설치 가이드
```

## 🔧 기술 스택

### 백엔드
- **Python 3.8+**: 메인 프로그래밍 언어
- **Google API Client**: YouTube Data API v3 연동
- **Pandas**: 데이터 처리 및 분석
- **OpenPyXL**: Excel 파일 생성
- **NumPy**: 수치 계산
- **Matplotlib**: 데이터 시각화
- **Scikit-learn**: 머신러닝 (클러스터링, 회귀분석)
- **SciPy**: 고급 통계 분석
- **Seaborn**: 통계 시각화

### 프론트엔드
- **PyQt5**: 크로스플랫폼 GUI 프레임워크
- **QThread**: 백그라운드 작업 처리
- **Custom Widgets**: 사용자 정의 UI 컴포넌트 (썸네일뷰어, API키관리)
- **Requests**: HTTP 이미지 다운로드

### 배포
- **PyInstaller**: 독립 실행 파일 생성
- **UPX**: 실행 파일 압축
- **Auto-build Scripts**: 원클릭 빌드 지원

## 📊 분석 지표 설명

### 기본 지표
- **조회수**: 영상 재생 횟수
- **좋아요**: 긍정적 반응 수
- **댓글수**: 사용자 참여도

### 계산 지표
- **좋아요율**: (좋아요 / 조회수) × 100
- **댓글율**: (댓글수 / 조회수) × 100
- **참여도 점수**: 좋아요 + 댓글수

## ⚠️ 주의사항

- YouTube Data API v3의 [사용 정책](https://developers.google.com/youtube/terms/api-services-terms-of-service) 준수
- API 할당량 제한 (일일 10,000 units)
- 개인정보 및 저작권 존중

### 도움말
- [INSTALLATION.md](INSTALLATION.md): 상세 설치 가이드
- [API 문서](https://developers.google.com/youtube/v3): YouTube API 참조
- [PyQt5 문서](https://doc.qt.io/qtforpython/): GUI 개발 참조

---

⭐ **이 프로젝트가 도움이 되었다면 스타를 눌러주세요!**

Made with ❤️ for YouTube content creators and data analysts

