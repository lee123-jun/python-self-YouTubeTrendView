@echo off
setlocal EnableDelayedExpansion
chcp 65001 > nul

REM YouTube 트렌드 판별기 빌드 스크립트

echo =====================================
echo  YouTube 트렌드 판별기 빌드 시작
echo =====================================

REM 1. 가상환경 확인 및 활성화
echo.
echo [1/4] 가상환경 확인...
if exist "venv\Scripts\activate.bat" (
    echo 가상환경을 활성화합니다...
    call venv\Scripts\activate.bat
) else (
    echo 가상환경이 없습니다. 전역 Python을 사용합니다.
)

REM 2. 필요한 패키지 설치
echo.
echo [2/4] 필요한 패키지 설치...
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo 패키지 설치에 실패했습니다.
    echo 오류코드: !errorlevel!
    pause
    exit /b 1
)

REM 3. 이전 빌드 결과 정리
echo.
echo [3/4] 이전 빌드 결과 정리...
if exist "dist" (
    echo dist 폴더를 삭제합니다...
    rmdir /s /q dist
)
if exist "build" (
    echo build 폴더를 삭제합니다...
    rmdir /s /q build
)

REM 4. PyInstaller 빌드 실행
echo.
echo [4/4] PyInstaller 빌드 실행...
echo 빌드 진행 중... 잠시만 기다려주세요.
pyinstaller youtube_trend_analyzer.spec --noconfirm
if !errorlevel! neq 0 (
    echo 빌드에 실패했습니다.
    echo 오류코드: !errorlevel!
    echo.
    echo 가능한 해결방법:
    echo 1. requirements.txt 패키지가 모두 설치되었는지 확인
    echo 2. youtube_trend_analyzer.spec 파일이 존재하는지 확인
    echo 3. 충분한 디스크 공간이 있는지 확인
    pause
    exit /b 1
)

REM 5. 빌드 완료 확인
echo.
echo =====================================
if exist "dist\YouTube_트렌드_판별기.exe" (
    echo  빌드가 성공적으로 완료되었습니다!
    echo  실행 파일: dist\YouTube_트렌드_판별기.exe
    echo.
    echo  파일 크기:
    for %%A in ("dist\YouTube_트렌드_판별기.exe") do echo  - 실행파일: %%~zA bytes
    echo.
    echo  배포를 위해 다음 파일들을 함께 제공하세요:
    echo  - dist\YouTube_트렌드_판별기.exe
    echo  - config\config.json (API 키 설정)
    echo  - README.md (사용법 안내)
    echo.
    echo  실행파일 테스트를 위해 'dist\YouTube_트렌드_판별기.exe'를 실행해보세요.
) else (
    echo  빌드에 실패했습니다.
    echo  dist 폴더에 실행 파일이 생성되지 않았습니다.
    echo  오류 로그를 확인해주세요.
    echo.
    if exist "build\YouTube_트렌드_판별기\warn-YouTube_트렌드_판별기.txt" (
        echo  경고 로그가 발견되었습니다:
        echo  build\YouTube_트렌드_판별기\warn-YouTube_트렌드_판별기.txt
    )
)
echo =====================================

echo.
echo 아무 키나 눌러서 종료...
pause > nul