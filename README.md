# YouTube 트렌드 분석기

🎯 **Python 기반 YouTube Data API를 활용한 영상 데이터 수집 및 트렌드 분석 도구**

YouTube Data API v3를 통해 영상 데이터를 수집하고, PyQt5 기반 GUI로 분석할 수 있는 트렌드 분석 프로그램입니다. 영상 데이터를 수집해 트렌드 주제, 인기 지표, 참여도 분석이 가능합니다.

## ✨ 주요 기능

### 🔍 강력한 검색 기능
- **키워드 기반 검색**: 원하는 주제의 영상 검색
- **고급 필터링**: 영상 길이, 업로드 기간, 정렬 방식, 최대 수집 개수 설정
- **인기 급상승**: 현재 트렌딩 영상 실시간 확인

### 📈 상세 데이터 분석
- **핵심 지표**: 조회수, 좋아요, 댓글 수, 참여율
- **영상 분류**: 숏폼(60초 이하) vs 롱폼 자동 구분
- **트렌드 점수**: 독자적인 알고리즘으로 트렌드 점수 계산

### 📊 통계 분석
- **기본 통계**: 평균, 중간값, 최댓값 등 기본 통계
- **상위 성과**: Top 10 영상 자동 추출
- **카테고리 분석**: 숏폼/롱폼 비율 및 성과 비교

### 💾 데이터 내보내기
- **Excel 형식**: 통계 시트 포함 완전한 분석 리포트
- **원클릭 저장**: 타임스탬프 자동 포함

### 🖱️ 사용자 친화적 GUI
- **직관적 인터페이스**: 복잡한 설정 없이 바로 사용
- **실시간 미리보기**: 검색 진행상황 표시
- **YouTube 연동**: 영상 더블클릭으로 바로 재생

##  빠른 시작

### 1️⃣ 실행 파일 사용 (권장)
```
1. dist/YouTube트렌드분석기.exe 실행
2. API 키 설정 후 바로 사용
```

### 2️⃣ 소스 코드 실행
```bash
# 저장소 클론
git clone https://github.com/lee123-jun/python-self-YouTubeTrendView.git
cd python-self-YouTubeTrendView

# 가상환경 생성 (권장)
conda create -n youtubepy python=3.12
conda activate youtubepy

# 의존성 설치
pip install -r requirements.txt

# 프로그램 실행
python main.py
```

## 🔑 API 키 설정

### 1. Google Cloud Console 설정
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. **YouTube Data API v3** 활성화
4. **API 키** 생성

### 2. 프로그램에서 설정
1. 프로그램 실행 후 설정 버튼 클릭
2. 발급받은 API 키 입력
3. 저장 후 재시작

> 💡 **자세한 설정 방법**: [INSTALLATION.md](INSTALLATION.md) 참조

## 📖 사용법

### 기본 검색
1. **검색어 입력** (예: "파이썬 강의", "요리 레시피")
2. **조건 설정**: 
   - 영상 길이 (전체/숏폼/롱폼)
   - 발행 기간 (오늘/이번 주/이번 달/올해)
   - 정렬 방식 (관련도/최신순/조회수/평점)
   - 최대 수집 개수 (1~50개)
3. **검색 실행** 버튼 클릭
4. **결과 분석**: 테이블에서 데이터 확인

### 고급 활용
- **필터링**: 검색 후 추가 조건으로 세부 분석
- **정렬**: 컬럼 헤더 클릭으로 원하는 기준 정렬
- **내보내기**: Excel로 데이터 저장
- **YouTube 연동**: 영상 제목 더블클릭으로 바로 재생

## 🛠️ 빌드 방법

### PyInstaller로 실행 파일 생성
```bash
# 가상환경 활성화
conda activate youtubepy

# 빌드 실행
pyinstaller YouTube트렌드분석기.spec

# 결과물: dist/YouTube트렌드분석기.exe
```

## 📁 프로젝트 구조
```
python-self-YouTubeTrendView/
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
│   └── config_template.json       # 설정 템플릿
├── dist/
│   └── YouTube트렌드분석기.exe    # 실행 파일
├── main.py                        # 프로그램 진입점
├── requirements.txt               # 패키지 의존성
├── YouTube트렌드분석기.spec       # PyInstaller 설정
├── README.md                      # 프로젝트 문서
├── INSTALLATION.md                # 설치 가이드
└── .gitignore                     # Git 무시 파일
```

## 🔧 기술 스택

### 코어 라이브러리
- **Python 3.12**: 메인 프로그래밍 언어
- **PyQt5**: GUI 프레임워크
- **google-api-python-client**: YouTube Data API v3 연동
- **pandas**: 데이터 처리 및 분석
- **numpy**: 수치 계산
- **openpyxl**: Excel 파일 생성
- **requests**: HTTP 통신
- **python-dateutil**: 날짜 처리

### 배포
- **PyInstaller**: 독립 실행 파일 생성
- **Hidden Imports**: googleapiclient, pandas, numpy 등 포함

## 📊 분석 지표 설명

### 기본 지표
- **조회수**: 영상 재생 횟수
- **좋아요**: 긍정적 반응 수
- **댓글수**: 사용자 참여도
- **게시일**: 영상 업로드 날짜
- **채널명**: 영상 제작자

### 계산 지표
- **좋아요율**: (좋아요 / 조회수) × 100
- **댓글율**: (댓글수 / 조회수) × 100
- **트렌드 점수**: 조회수, 좋아요, 댓글을 종합한 점수

### 카테고리 분류
- **숏폼**: 60초 이하 영상
- **롱폼**: 60초 초과 영상

## 🐛 문제 해결

### 일반적인 문제
1. **API 키 오류**: Google Cloud Console에서 YouTube Data API v3 활성화 확인
2. **모듈 임포트 오류**: `pip install -r requirements.txt`로 의존성 재설치
3. **실행 파일 오류**: `youtube-api` 환경에서 빌드했는지 확인

### 디버깅
- 콘솔 버전 실행: `dist/YouTube트렌드분석기_최종.exe`
- 개발 환경 실행: `python main.py`
- 로그 확인: 프로그램 실행 시 터미널 출력 확인

## 🤝 기여하기

### 개발 환경 설정
```bash
# 저장소 클론
git clone https://github.com/lee123-jun/python-self-YouTubeTrendView.git
cd python-self-YouTubeTrendView

# 가상환경 생성
conda create -n youtubepy python=3.12
conda activate youtubepy

# 개발 의존성 설치
pip install -r requirements.txt
```

### 코드 스타일
- **PEP 8** 준수
- **타입 힌트** 사용 권장
- **독스트링** 작성
- **에러 핸들링** 필수

### Pull Request 가이드
1. Feature 브랜치 생성 (`feature/new-feature`)
2. 변경사항 구현 및 테스트
3. 커밋 메시지는 명확하게 작성
4. Pull Request 생성

## 📝 할일 (TODO)

### 🎯 단기 목표
- [ ] 다국어 지원 (영어, 일본어)
- [ ] 차트 시각화 기능 추가
- [ ] 키워드 트렌드 분석
- [ ] 데이터 캐싱 기능

### 🚀 장기 목표
- [ ] 웹 버전 개발
- [ ] 실시간 트렌드 모니터링
- [ ] AI 기반 콘텐츠 추천
- [ ] 대용량 데이터 처리 최적화

## 📞 지원

### 문의사항
- **GitHub Issues**: 기술적 문제 및 버그 리포트
- **Discussions**: 일반적인 질문 및 아이디어 공유

### 참고 문서
- [INSTALLATION.md](INSTALLATION.md): 상세 설치 가이드
- [YouTube API 문서](https://developers.google.com/youtube/v3): API 참조
- [PyQt5 문서](https://doc.qt.io/qtforpython/): GUI 개발 참조

## 📜 라이선스

이 프로젝트는 [MIT License](LICENSE)를 따릅니다.

## ⚠️ 주의사항

- YouTube Data API v3의 [사용 정책](https://developers.google.com/youtube/terms/api-services-terms-of-service) 준수
- API 할당량 제한 (일일 10,000 units)
- 개인정보 및 저작권 존중

---

⭐ **이 프로젝트가 도움이 되었다면 스타를 눌러주세요!**

Made with ❤️ for YouTube content creators and data analysts

