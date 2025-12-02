# MCP Photo Location Server

사진 파일에서 GPS 위치 정보를 추출, 분석, 관리하는 MCP (Model Context Protocol) 서버입니다.

## 🎯 왜 MCP인가? LLM과의 차별점

**일반 LLM이 할 수 없는 것:**
- ❌ 실제 파일 시스템에서 EXIF 데이터 직접 읽기
- ❌ 바이너리 이미지 파일의 메타데이터 정확히 파싱
- ❌ 원본 파일 수정 (GPS 정보 제거/마스킹)
- ❌ 폴더 내 수백 개 파일 일괄 처리
- ❌ 지오펜싱 알고리즘으로 거리 계산
- ❌ 외부 API(역지오코딩)와 통합

**이 MCP 서버가 제공하는 것:**
- ✅ **실제 파일 접근**: 로컬 파일 시스템의 사진 직접 처리
- ✅ **정확한 EXIF 파싱**: piexif 라이브러리로 GPS 데이터 정밀 추출
- ✅ **원본 파일 수정**: 프라이버시 보호를 위한 GPS 정보 제거
- ✅ **대규모 일괄 처리**: 수백~수천 개 사진 효율적 처리
- ✅ **수학적 정확성**: Haversine 공식으로 거리 계산 (오차 < 0.5%)
- ✅ **실시간 API 통합**: OpenStreetMap Nominatim으로 주소 변환

## ✨ 핵심 기능

### 📍 위치 정보 추출
- 단일 사진 파일에서 GPS 위치 정보 추출 (위도, 경도, 고도)
- 디렉토리 내 모든 사진 파일 일괄 처리
- Base64 인코딩된 이미지 데이터 처리
- **역지오코딩**: GPS 좌표를 한국어 주소로 자동 변환
- Google Maps 링크 자동 생성

### 🗺️ 지오펜싱 (Geofencing)
- 특정 위치 반경 내/외 사진 필터링
- Haversine 공식 기반 정확한 거리 계산
- 사용 사례: "집 주변 1km 사진 찾기", "특정 지역 여행 사진 분류"

### 🔒 프라이버시 보호
- **GPS 정보 완전 제거**: 사진에서 모든 위치 정보 제거
- **선택적 마스킹**: 특정 위치 주변만 GPS 정보 제거
- **자동 백업**: 원본 파일 안전 보관 (.bak 파일)
- **원본 보호**: 읽기 작업은 절대 파일 수정하지 않음

## 🚀 실용적 사용 사례

### 1. 여행 사진 자동 분류
```
"제주도에서 찍은 사진만 골라줘"
→ 지오펜싱으로 제주도 좌표 범위 내 사진 필터링
```

### 2. SNS 업로드 전 프라이버시 체크
```
"집 주소가 들어간 사진 찾아서 GPS 제거해줘"
→ 집 좌표 기준 지오펜싱 후 선택적 마스킹
```

### 3. 위치 기반 추억 찾기
```
"명동에서 찍은 모든 사진 보여줘"
→ 명동 좌표 반경 내 사진 검색
```

### 4. 대량 사진 메타데이터 분석
```
"휴가 폴더의 모든 사진이 어디서 찍혔는지 정리해줘"
→ 일괄 처리로 전체 위치 정보 추출 및 주소 변환
```

## ⚙️ 설치 및 실행

### 필수 요구사항
- Python 3.8 이상
- pip 패키지 관리자

### 설치 방법

```bash
# 1. 저장소 클론 (또는 프로젝트 디렉토리로 이동)
cd mcp-photo-location

# 2. 가상환경 생성 (권장)
python -m venv venv

# 3. 가상환경 활성화
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# 4. 패키지 설치
pip install -r requirements.txt
```

### MCP 서버 실행

```bash
# 서버 실행
python server.py
```

서버가 실행되면 MCP 클라이언트(예: Claude Desktop, Cursor)에서 이 서버를 연결하여 사용할 수 있습니다.

### 의존성 패키지
- `fastmcp>=2.13.1`: MCP 서버 프레임워크
- `mcp>=1.22.0`: Model Context Protocol 라이브러리
- `Pillow>=10.0.0`: 이미지 파일 처리
- `piexif>=1.1.3`: EXIF 데이터 파싱/수정
- `httpx>=0.28.0`: HTTP 클라이언트 (역지오코딩 API)
- `uvicorn>=0.38.0`: ASGI 서버

## 🔌 MCP 서버 Endpoint 설정

다음 설정을 복사하여 MCP 클라이언트(Cursor, Claude Desktop 등) 설정 파일에 붙여넣으세요.

### 가상환경 Python 사용 (권장)

```json
{
  "mcpServers": {
    "photo-location": {
      "command": "C:\\AIproject\\mcp-photo-location\\mcp-photo-location\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\AIproject\\mcp-photo-location\\mcp-photo-location\\server.py"
      ],
      "cwd": "C:\\AIproject\\mcp-photo-location\\mcp-photo-location"
    }
  }
}
```

### 시스템 Python 사용

```json
{
  "mcpServers": {
    "photo-location": {
      "command": "python",
      "args": [
        "C:\\AIproject\\mcp-photo-location\\mcp-photo-location\\server.py"
      ],
      "cwd": "C:\\AIproject\\mcp-photo-location\\mcp-photo-location"
    }
  }
}
```

**설정 파일 위치:**
- **Cursor**: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- **Claude Desktop**: `%APPDATA%\Claude\claude_desktop_config.json`

> ⚠️ **참고**: 프로젝트 경로가 다르면 `C:\\AIproject\\mcp-photo-location\\mcp-photo-location` 부분을 실제 프로젝트 경로로 변경하세요.

## 🛠️ 사용 가능한 도구 (MCP Tools)

모든 도구는 **실제 파일 시스템**에서 작동하며, **바이너리 EXIF 데이터**를 직접 파싱합니다.

### 1. `get_photo_location`
단일 사진 파일에서 GPS 위치 정보를 추출합니다.

**기술적 특징:**
- piexif 라이브러리로 EXIF 데이터 직접 파싱
- GPS 위도/경도를 십진법 좌표로 정확히 변환
- OpenStreetMap Nominatim API로 역지오코딩 (한국어 주소)
- Google Maps 링크 자동 생성

**매개변수:**
- `image_path` (string): 이미지 파일 경로

**반환값:**
- JSON 형식의 위치 정보 (위도, 경도, 고도, 주소, Google Maps 링크)

**LLM과의 차이점:** LLM은 파일을 읽을 수 없지만, 이 도구는 실제 파일에서 EXIF 메타데이터를 추출합니다.

### 2. `get_photo_location_from_base64`
Base64 인코딩된 이미지 데이터에서 GPS 위치 정보를 추출합니다.

**기술적 특징:**
- Base64 디코딩 후 임시 파일 생성
- EXIF 데이터 추출 후 임시 파일 자동 정리
- data URI 형식 지원 (data:image/jpeg;base64,...)

**매개변수:**
- `image_base64` (string): Base64 인코딩된 이미지 데이터
- `image_format` (string): 이미지 형식 ("jpg", "png", "tiff"), 기본값: "jpg"

**반환값:**
- JSON 형식의 위치 정보 (위도, 경도, 주소, Google Maps 링크)

**LLM과의 차이점:** LLM은 이미지 내용을 "보는" 것만 가능하지만, 이 도구는 실제 EXIF 메타데이터를 파싱합니다.

### 3. `batch_get_photo_locations`
디렉토리 내의 모든 사진 파일에서 GPS 위치 정보를 일괄 추출합니다.

**기술적 특징:**
- Path.iterdir()로 디렉토리 순회
- 지원 형식 필터링 (.jpg, .jpeg, .png, .tiff, .tif)
- 각 파일별 EXIF 데이터 독립 파싱
- 대량 파일 처리 최적화

**매개변수:**
- `directory_path` (string): 이미지 파일들이 있는 디렉토리 경로

**반환값:**
- JSON 형식의 위치 정보 리스트 (각 사진의 파일명, 경로, 위치, 주소 포함)

**LLM과의 차이점:** LLM은 폴더 구조를 인식할 수 없지만, 이 도구는 실제 디렉토리를 탐색합니다.

### 4. `geofence_photos`
지오펜싱 기능: 특정 위치를 중심으로 반경 내/외에 있는 사진을 필터링합니다.

**기술적 특징:**
- **Haversine 공식** 사용: 지구 곡률을 고려한 정확한 거리 계산
- 거리 계산 오차 < 0.5% (구면 삼각법 기반)
- 각 사진의 GPS 좌표와 중심점 간 거리 실시간 계산
- 반경 내(inside)/외(outside) 필터링 지원

**지오펜싱(Geofencing)이란?**
- 특정 지리적 경계(geographic boundary)를 정의하는 기술
- 지정한 중심점에서 반경 거리 내에 있는지 밖에 있는지 판단
- 예: "서울시청에서 5km 반경 내 사진", "집 주변 1km 내 사진" 등

**LLM과의 차이점:** LLM은 수학적 거리 계산을 할 수 없지만, 이 도구는 정확한 지구 좌표계 계산을 수행합니다.

**매개변수:**
- `directory_path` (string): 이미지 파일들이 있는 디렉토리 경로
- `center_latitude` (float): 중심점의 위도
- `center_longitude` (float): 중심점의 경도
- `radius_km` (float): 반경 (킬로미터)
- `filter_mode` (string): "inside" (반경 내) 또는 "outside" (반경 외), 기본값: "inside"

**반환값:**
- JSON 형식의 필터링된 사진 목록 (각 사진의 중심점으로부터의 거리 포함)

**예제:**
```python
# 서울시청(37.5665, 126.9780)에서 5km 반경 내 사진 찾기
geofence_photos(
    "C:/Users/username/Pictures",
    center_latitude=37.5665,
    center_longitude=126.9780,
    radius_km=5.0,
    filter_mode="inside"
)
```

### 5. `remove_gps_from_photo`
사진 파일에서 GPS 위치 정보를 제거합니다. (사용자가 명시적으로 요청한 경우에만 실행)

**기술적 특징:**
- piexif로 EXIF 데이터 로드
- GPS 섹션만 선택적으로 제거 (다른 EXIF 데이터 보존)
- Pillow로 이미지 재저장 (품질 손실 없음)
- 원본 파일 백업 자동 생성 (.bak 파일)
- 출력 경로 지정 가능 (원본 수정 또는 새 파일 생성)

**주의:** 이 기능은 원본 파일을 수정할 수 있습니다. 기본적으로 백업을 생성합니다.

**LLM과의 차이점:** LLM은 파일을 수정할 수 없지만, 이 도구는 실제 바이너리 파일의 EXIF 데이터를 조작합니다.

**매개변수:**
- `image_path` (string): 이미지 파일 경로
- `create_backup` (bool): True인 경우 원본 파일을 .bak 확장자로 백업, 기본값: True
- `output_path` (string, optional): 새 파일로 저장할 경로 (None이면 원본 파일 수정)

**반환값:**
- JSON 형식의 작업 결과

**예제:**
```python
# GPS 정보 제거 (백업 생성)
remove_gps_from_photo("C:/Users/username/Pictures/photo.jpg", create_backup=True)

# 새 파일로 저장
remove_gps_from_photo(
    "C:/Users/username/Pictures/photo.jpg",
    create_backup=False,
    output_path="C:/Users/username/Pictures/photo_no_gps.jpg"
)
```

### 6. `mask_location_in_photo`
특정 위치 정보를 선택적으로 마스킹합니다. (사용자가 명시적으로 요청한 경우에만 실행)

**기술적 특징:**
- 먼저 사진의 GPS 좌표 추출
- Haversine 공식으로 마스크 중심점과의 거리 계산
- 거리가 반경 내일 때만 GPS 정보 제거 (스마트 필터링)
- 원본 위치 정보 및 거리 정보 반환 (투명성)

**사용 사례:**
- "집 주변 500m 내 사진의 위치 정보만 제거"
- "회사 주변 1km 사진만 프라이버시 보호"
- 특정 지역 사진만 선택적으로 GPS 제거

**LLM과의 차이점:** LLM은 조건부 파일 수정을 할 수 없지만, 이 도구는 위치 기반 조건부 GPS 제거를 수행합니다.

**매개변수:**
- `image_path` (string): 이미지 파일 경로
- `mask_latitude` (float): 마스킹할 중심점의 위도
- `mask_longitude` (float): 마스킹할 중심점의 경도
- `mask_radius_km` (float): 마스킹할 반경 (킬로미터)
- `create_backup` (bool): True인 경우 원본 파일을 .bak 확장자로 백업, 기본값: True
- `output_path` (string, optional): 새 파일로 저장할 경로 (None이면 원본 파일 수정)

**반환값:**
- JSON 형식의 작업 결과 (원본 위치 정보 및 거리 포함)

**예제:**
```python
# 집 주변 500m 내 사진의 GPS 정보만 제거
mask_location_in_photo(
    "C:/Users/username/Pictures/photo.jpg",
    mask_latitude=37.5665,
    mask_longitude=126.9780,
    mask_radius_km=0.5,
    create_backup=True
)
```

## 📋 지원 형식

### GPS 정보 추출
- ✅ JPEG (.jpg, .jpeg) - EXIF 메타데이터 완전 지원
- ✅ TIFF (.tiff, .tif) - EXIF 메타데이터 완전 지원
- ✅ PNG (.png) - EXIF 읽기 지원 (제한적)

### GPS 정보 제거/마스킹
- ✅ JPEG (.jpg, .jpeg) - EXIF 수정 완전 지원
- ✅ TIFF (.tiff, .tif) - EXIF 수정 완전 지원
- ❌ PNG (.png) - EXIF 데이터 구조 미지원 (읽기만 가능)

**기술적 배경:**
- EXIF(Exchangeable Image File Format)는 JPEG/TIFF 전용 메타데이터 포맷
- PNG는 다른 메타데이터 구조를 사용하여 GPS 정보 저장 불가
- piexif 라이브러리가 JPEG/TIFF EXIF 데이터를 정확히 파싱/수정

## 💡 실제 사용 예제

### 예제 1: 단일 사진 위치 확인
```python
# 실제 파일에서 GPS 정보 추출
get_photo_location("C:/Users/username/Pictures/vacation/IMG_001.jpg")

# 반환 예시:
# {
#   "image_path": "C:/Users/username/Pictures/vacation/IMG_001.jpg",
#   "location": {
#     "latitude": 33.4996,
#     "longitude": 126.5312,
#     "altitude": 150.5
#   },
#   "address": "제주특별자치도 제주시 해안로, 첨단동",
#   "google_maps_url": "https://www.google.com/maps?q=33.4996,126.5312"
# }
```

### 예제 2: 디렉토리 전체 사진 일괄 처리
```python
# 폴더 내 모든 사진 위치 정보 추출
batch_get_photo_locations("C:/Users/username/Pictures/Korea_Trip_2024")

# 반환: 수백 개 사진의 위치 정보 리스트
```

### 예제 3: 지오펜싱 - 특정 지역 사진 필터링
```python
# 서울시청에서 5km 반경 내 사진만 찾기
geofence_photos(
    directory_path="C:/Users/username/Pictures",
    center_latitude=37.5665,      # 서울시청 위도
    center_longitude=126.9780,     # 서울시청 경도
    radius_km=5.0,                 # 5km 반경
    filter_mode="inside"           # 반경 내만
)

# 반환: 각 사진의 중심점으로부터의 거리(km) 포함
```

### 예제 4: 프라이버시 보호 - GPS 정보 완전 제거
```python
# 사진에서 GPS 정보 제거 (백업 자동 생성)
remove_gps_from_photo(
    image_path="C:/Users/username/Pictures/photo.jpg",
    create_backup=True  # photo.jpg.bak 자동 생성
)

# 반환: 작업 성공 여부 및 백업 경로
```

### 예제 5: 선택적 마스킹 - 집 주변 사진만 GPS 제거
```python
# 집 주변 500m 내 사진의 GPS 정보만 제거
mask_location_in_photo(
    image_path="C:/Users/username/Pictures/photo.jpg",
    mask_latitude=37.5665,      # 집 위도
    mask_longitude=126.9780,     # 집 경도
    mask_radius_km=0.5,          # 500m 반경
    create_backup=True
)

# 반환: 원본 위치 정보 및 거리 정보 포함
```

### 예제 6: Base64 이미지 처리
```python
# Base64 인코딩된 이미지 데이터 처리
get_photo_location_from_base64(
    image_base64="data:image/jpeg;base64,/9j/4AAQ...",
    image_format="jpg"
)

# 반환: 일반 get_photo_location과 동일한 형식
```

## 🔒 프라이버시 보호 기능

이 서버는 사용자가 **명시적으로 요청한 경우에만** GPS 정보를 제거하거나 마스킹합니다:
- `remove_gps_from_photo`: 전체 GPS 정보 제거
- `mask_location_in_photo`: 특정 위치 주변의 GPS 정보만 선택적 제거

**안전한 기본 동작:**
- ✅ 모든 읽기 기능은 원본 파일을 **절대 수정하지 않습니다**
- ✅ GPS 제거/마스킹 기능은 **기본적으로 백업을 생성**합니다
- ✅ 사용자가 **명시적으로 요청하지 않으면** 위치 정보를 제거하지 않습니다
- ✅ 원본 파일 안전성 최우선 (백업 생성 후 처리)

## 🎯 MCP로서의 기술적 우수성

### 정확성 (Accuracy)
- **Haversine 공식**: 지구 곡률을 고려한 정확한 거리 계산 (오차 < 0.5%)
- **EXIF 파싱**: piexif 라이브러리로 GPS 데이터 정밀 추출
- **좌표 변환**: 도/분/초(DMS) 형식을 십진법 좌표로 정확히 변환

### 신뢰성 (Reliability)
- **오류 처리**: 파일 없음, 형식 오류, EXIF 누락 등 모든 예외 상황 처리
- **백업 시스템**: 파일 수정 전 자동 백업으로 데이터 손실 방지
- **검증**: 파일 존재 여부, 형식 지원 여부 사전 검증

### 효율성 (Efficiency)
- **일괄 처리**: 수백~수천 개 파일 효율적 처리
- **임시 파일 관리**: Base64 처리 시 자동 정리
- **API 최적화**: 역지오코딩 API 호출 최소화 및 타임아웃 설정

### 확장성 (Scalability)
- **대규모 처리**: 디렉토리 내 무제한 파일 처리 가능
- **메모리 효율**: 파일 스트림 처리로 메모리 사용 최적화
- **외부 API 통합**: OpenStreetMap Nominatim 무료 API 활용

## 🔄 LLM 대비 MCP의 명확한 차별점

| 기능 | 일반 LLM | 이 MCP 서버 |
|------|---------|------------|
| 파일 시스템 접근 | ❌ 불가능 | ✅ 실제 파일 읽기/쓰기 |
| EXIF 메타데이터 파싱 | ❌ 불가능 | ✅ 바이너리 데이터 직접 파싱 |
| 파일 수정 | ❌ 불가능 | ✅ EXIF 데이터 선택적 제거 |
| 거리 계산 | ⚠️ 근사치만 가능 | ✅ Haversine 공식 (오차 < 0.5%) |
| 대량 파일 처리 | ❌ 불가능 | ✅ 일괄 처리 최적화 |
| 외부 API 통합 | ⚠️ 제한적 | ✅ 역지오코딩 API 통합 |
| 안전성 (백업) | ❌ 없음 | ✅ 자동 백업 시스템 |

## 📚 기술 스택

- **FastMCP**: MCP 서버 프레임워크
- **piexif**: EXIF 데이터 파싱 및 수정
- **Pillow (PIL)**: 이미지 파일 I/O
- **httpx**: 역지오코딩 API 호출
- **OpenStreetMap Nominatim**: 무료 역지오코딩 서비스

## 🎓 알고리즘 상세

### Haversine 공식
두 지점 간의 거리를 계산하는 공식:
```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
c = 2 × atan2(√a, √(1−a))
distance = R × c  (R = 지구 반경 6,371km)
```

### EXIF GPS 데이터 구조
- **위도/경도**: 도/분/초 튜플 형식 → 십진법 변환
- **고도**: 분수 튜플 형식 → 미터 단위 변환
- **방향 참조**: N/S, E/W 방향 반영

## 💬 실제 사용 예시 (사용자가 보낼 한 문장)

사용자가 MCP를 통해 이 도구를 사용할 때 다음과 같은 간단한 요청을 보낼 수 있습니다:

- **"이 사진 어디서 찍었더라?"** → `get_photo_location` 호출
- **"작년에 찍은 명동 사진들 찾아줘"** → `geofence_photos` 호출
- **"SNS에 올리기 전에 집 주소가 들어간 사진 체크해서 주소 정보 지워줘"** → `mask_location_in_photo` 호출

---

**이 MCP 서버는 단순한 정보 조회가 아닌, 실제 파일 시스템 작업과 정확한 데이터 처리를 수행하는 실용적인 도구입니다. LLM이 할 수 없는 실제 파일 접근, 바이너리 데이터 파싱, 수학적 정확한 계산을 통해 사용자의 사진 위치 정보를 안전하고 효율적으로 관리합니다.**


