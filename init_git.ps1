# Git 저장소 초기화 스크립트
Set-Location $PSScriptRoot

if (Test-Path .git) {
    Write-Host "Git 저장소가 이미 존재합니다."
    git status
} else {
    Write-Host "Git 저장소를 초기화합니다..."
    git init
    Write-Host "Git 저장소 초기화 완료!"
    git status
}

