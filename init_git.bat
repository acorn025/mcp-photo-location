@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 현재 디렉토리: %CD%
if exist .git (
    echo Git 저장소가 이미 존재합니다.
    git status
) else (
    echo Git 저장소를 초기화합니다...
    git init
    echo Git 저장소 초기화 완료!
    git status
)
pause

