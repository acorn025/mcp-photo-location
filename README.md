# MCP Photo Location Server

사진 파일에서 GPS 위치 정보를 추출하는 MCP (Model Context Protocol) 서버입니다.

## 기능

- 단일 사진 파일에서 GPS 위치 정보 추출
- 디렉토리 내 모든 사진 파일 일괄 처리
- Google Maps 링크 자동 생성

## 설치

```bash
# 가상환경 활성화
.\venv\Scripts\Activate.ps1

# 패키지 설치
pip install -r requirements.txt
```

## 실행

```bash
# MCP 서버 실행
python server.py
```

## 사용 가능한 도구

### 1. `get_photo_location`
단일 사진 파일에서 GPS 위치 정보를 추출합니다.

**매개변수:**
- `image_path` (string): 이미지 파일 경로

**반환값:**
- JSON 형식의 위치 정보 (위도, 경도, 고도, Google Maps 링크)

### 2. `batch_get_photo_locations`
디렉토리 내의 모든 사진 파일에서 GPS 위치 정보를 일괄 추출합니다.

**매개변수:**
- `directory_path` (string): 이미지 파일들이 있는 디렉토리 경로

**반환값:**
- JSON 형식의 위치 정보 리스트

## 지원 형식

- JPEG (.jpg, .jpeg)
- TIFF (.tiff, .tif)
- PNG (.png)

## 예제

```python
# 단일 파일 처리
get_photo_location("C:/Users/username/Pictures/photo.jpg")

# 디렉토리 일괄 처리
batch_get_photo_locations("C:/Users/username/Pictures")
```


