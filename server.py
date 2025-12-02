"""
MCP Photo Location Server
사진 파일에서 GPS 위치 정보를 추출하는 MCP 서버
"""
from fastmcp import FastMCP
from pathlib import Path
import piexif
from typing import Optional, Dict, Any, List
import json
import math
import shutil
import base64
import tempfile
import io
import httpx

# MCP 서버 인스턴스 생성
mcp = FastMCP("Photo Location Server")


def reverse_geocode(latitude: float, longitude: float) -> Optional[str]:
    """
    위도/경도 좌표를 주소로 변환합니다 (역지오코딩).
    OpenStreetMap Nominatim API를 사용합니다.
    
    Args:
        latitude: 위도
        longitude: 경도
        
    Returns:
        주소 문자열 또는 None (오류 시)
    """
    try:
        # Nominatim API 호출 (무료, API 키 불필요)
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "addressdetails": 1,
            "accept-language": "ko"  # 한국어 주소
        }
        headers = {
            "User-Agent": "MCP-Photo-Location-Server/1.0"  # Nominatim 요구사항
        }
        
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "address" in data:
                address = data["address"]
                # 주소 구성 요소 추출
                address_parts = []
                
                # 한국 주소 형식
                if "road" in address:
                    address_parts.append(address["road"])
                if "building" in address:
                    address_parts.append(address["building"])
                if "neighbourhood" in address or "suburb" in address:
                    addr = address.get("neighbourhood") or address.get("suburb")
                    if addr:
                        address_parts.append(addr)
                if "city" in address or "town" in address or "village" in address:
                    addr = address.get("city") or address.get("town") or address.get("village")
                    if addr:
                        address_parts.append(addr)
                if "state" in address or "province" in address:
                    addr = address.get("state") or address.get("province")
                    if addr:
                        address_parts.append(addr)
                if "country" in address:
                    address_parts.append(address["country"])
                
                if address_parts:
                    return ", ".join(address_parts)
                else:
                    # 주소 구성 요소가 없으면 display_name 사용
                    return data.get("display_name", None)
            
            return data.get("display_name", None)
            
    except Exception as e:
        # 오류 발생 시 None 반환 (주소 없이도 동작하도록)
        return None


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    두 지점 간의 거리를 계산합니다 (Haversine 공식 사용).
    
    Args:
        lat1, lon1: 첫 번째 지점의 위도, 경도
        lat2, lon2: 두 번째 지점의 위도, 경도
        
    Returns:
        두 지점 간의 거리 (킬로미터)
    """
    # 지구 반경 (킬로미터)
    R = 6371.0
    
    # 라디안으로 변환
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # 차이 계산
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine 공식
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def extract_gps_from_exif(image_path: str) -> Optional[Dict[str, Any]]:
    """
    이미지 파일에서 EXIF GPS 데이터를 추출합니다.
    
    Args:
        image_path: 이미지 파일 경로
        
    Returns:
        GPS 정보가 담긴 딕셔너리 (위도, 경도 등) 또는 None
    """
    try:
        exif_dict = piexif.load(image_path)
        
        if "GPS" not in exif_dict or not exif_dict["GPS"]:
            return None
            
        gps_data = exif_dict["GPS"]
        
        # GPS 위도 추출
        if piexif.GPSIFD.GPSLatitude in gps_data and piexif.GPSIFD.GPSLatitudeRef in gps_data:
            lat_ref = gps_data[piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
            lat_tuple = gps_data[piexif.GPSIFD.GPSLatitude]
            latitude = lat_tuple[0][0] / lat_tuple[0][1] + \
                      lat_tuple[1][0] / lat_tuple[1][1] / 60.0 + \
                      lat_tuple[2][0] / lat_tuple[2][1] / 3600.0
            if lat_ref == 'S':
                latitude = -latitude
        else:
            latitude = None
            
        # GPS 경도 추출
        if piexif.GPSIFD.GPSLongitude in gps_data and piexif.GPSIFD.GPSLongitudeRef in gps_data:
            lon_ref = gps_data[piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
            lon_tuple = gps_data[piexif.GPSIFD.GPSLongitude]
            longitude = lon_tuple[0][0] / lon_tuple[0][1] + \
                       lon_tuple[1][0] / lon_tuple[1][1] / 60.0 + \
                       lon_tuple[2][0] / lon_tuple[2][1] / 3600.0
            if lon_ref == 'W':
                longitude = -longitude
        else:
            longitude = None
            
        # 고도 추출 (있는 경우)
        altitude = None
        if piexif.GPSIFD.GPSAltitude in gps_data:
            alt_tuple = gps_data[piexif.GPSIFD.GPSAltitude]
            altitude = alt_tuple[0] / alt_tuple[1]
            if piexif.GPSIFD.GPSAltitudeRef in gps_data and gps_data[piexif.GPSIFD.GPSAltitudeRef] == 1:
                altitude = -altitude
                
        result = {}
        if latitude is not None:
            result["latitude"] = latitude
        if longitude is not None:
            result["longitude"] = longitude
        if altitude is not None:
            result["altitude"] = altitude
            
        return result if result else None
        
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_photo_location(image_path: str) -> str:
    """
    사진 파일에서 GPS 위치 정보를 추출합니다.
    
    Args:
        image_path: 이미지 파일의 경로
        
    Returns:
        JSON 형식의 위치 정보 (위도, 경도, 고도)
    """
    path = Path(image_path)
    
    if not path.exists():
        return json.dumps({"error": f"파일을 찾을 수 없습니다: {image_path}"}, ensure_ascii=False)
    
    if not path.is_file():
        return json.dumps({"error": f"파일이 아닙니다: {image_path}"}, ensure_ascii=False)
    
    # 지원하는 이미지 형식 확인
    supported_formats = {'.jpg', '.jpeg', '.tiff', '.tif', '.png'}
    if path.suffix.lower() not in supported_formats:
        return json.dumps({
            "error": f"지원하지 않는 파일 형식입니다: {path.suffix}",
            "supported_formats": list(supported_formats)
        }, ensure_ascii=False)
    
    gps_data = extract_gps_from_exif(str(path))
    
    if gps_data is None:
        return json.dumps({
            "message": "이 이미지에는 GPS 위치 정보가 없습니다.",
            "image_path": str(path)
        }, ensure_ascii=False)
    
    if "error" in gps_data:
        return json.dumps(gps_data, ensure_ascii=False)
    
    # 주소 정보 가져오기
    address = None
    if "latitude" in gps_data and "longitude" in gps_data:
        address = reverse_geocode(gps_data["latitude"], gps_data["longitude"])
    
    result = {
        "image_path": str(path),
        "location": gps_data,
        "google_maps_url": f"https://www.google.com/maps?q={gps_data.get('latitude')},{gps_data.get('longitude')}"
    }
    
    if address:
        result["address"] = address
    
    return json.dumps(result, ensure_ascii=False, indent=2)


def _get_photo_location_from_base64_impl(image_base64: str, image_format: str = "jpg") -> str:
    """
    Base64로 인코딩된 이미지 데이터에서 GPS 위치 정보를 추출하는 내부 구현 함수.
    """
    try:
        # data URI 형식 처리 (data:image/jpeg;base64,...)
        if image_base64.startswith("data:"):
            # data URI에서 base64 부분만 추출
            header, encoded = image_base64.split(",", 1)
            # MIME 타입에서 형식 추출
            if "image/" in header:
                mime_type = header.split("image/")[1].split(";")[0]
                if mime_type in ["jpeg", "jpg"]:
                    image_format = "jpg"
                elif mime_type == "png":
                    image_format = "png"
                elif mime_type in ["tiff", "tif"]:
                    image_format = "tiff"
        else:
            encoded = image_base64
        
        # Base64 디코딩
        image_data = base64.b64decode(encoded)
        
        # 지원하는 이미지 형식 확인
        supported_formats = {'jpg', 'jpeg', 'tiff', 'tif', 'png'}
        if image_format.lower() not in supported_formats:
            return json.dumps({
                "error": f"지원하지 않는 이미지 형식입니다: {image_format}",
                "supported_formats": list(supported_formats)
            }, ensure_ascii=False)
        
        # 임시 파일로 저장
        suffix_map = {
            'jpg': '.jpg',
            'jpeg': '.jpg',
            'png': '.png',
            'tiff': '.tiff',
            'tif': '.tif'
        }
        suffix = suffix_map.get(image_format.lower(), '.jpg')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name
        
        try:
            # GPS 정보 추출
            gps_data = extract_gps_from_exif(temp_path)
            
            if gps_data is None:
                return json.dumps({
                    "message": "이 이미지에는 GPS 위치 정보가 없습니다.",
                    "image_format": image_format
                }, ensure_ascii=False)
            
            if "error" in gps_data:
                return json.dumps(gps_data, ensure_ascii=False)
            
            # 주소 정보 가져오기
            address = None
            if "latitude" in gps_data and "longitude" in gps_data:
                address = reverse_geocode(gps_data["latitude"], gps_data["longitude"])
            
            result = {
                "image_format": image_format,
                "image_size_bytes": len(image_data),
                "location": gps_data,
                "google_maps_url": f"https://www.google.com/maps?q={gps_data.get('latitude')},{gps_data.get('longitude')}"
            }
            
            if address:
                result["address"] = address
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        finally:
            # 임시 파일 삭제
            try:
                Path(temp_path).unlink()
            except:
                pass
                
    except base64.binascii.Error:
        return json.dumps({
            "error": "잘못된 Base64 인코딩입니다."
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": f"이미지 처리 중 오류 발생: {str(e)}"
        }, ensure_ascii=False)


@mcp.tool()
def get_photo_location_from_base64(image_base64: str, image_format: str = "jpg") -> str:
    """
    Base64로 인코딩된 이미지 데이터에서 GPS 위치 정보를 추출합니다.
    
    Args:
        image_base64: Base64로 인코딩된 이미지 데이터 (data URI 형식 또는 순수 base64 문자열)
        image_format: 이미지 형식 ("jpg", "jpeg", "png", "tiff", "tif"), 기본값: "jpg"
        
    Returns:
        JSON 형식의 위치 정보 (위도, 경도, 고도)
    """
    return _get_photo_location_from_base64_impl(image_base64, image_format)


@mcp.tool()
def batch_get_photo_locations(directory_path: str) -> str:
    """
    디렉토리 내의 모든 사진 파일에서 GPS 위치 정보를 일괄 추출합니다.
    
    Args:
        directory_path: 이미지 파일들이 있는 디렉토리 경로
        
    Returns:
        JSON 형식의 위치 정보 리스트
    """
    dir_path = Path(directory_path)
    
    if not dir_path.exists():
        return json.dumps({"error": f"디렉토리를 찾을 수 없습니다: {directory_path}"}, ensure_ascii=False)
    
    if not dir_path.is_dir():
        return json.dumps({"error": f"디렉토리가 아닙니다: {directory_path}"}, ensure_ascii=False)
    
    supported_formats = {'.jpg', '.jpeg', '.tiff', '.tif', '.png'}
    results = []
    
    for image_file in dir_path.iterdir():
        if image_file.is_file() and image_file.suffix.lower() in supported_formats:
            gps_data = extract_gps_from_exif(str(image_file))
            if gps_data and "error" not in gps_data:
                result_item = {
                    "filename": image_file.name,
                    "path": str(image_file),
                    "location": gps_data,
                    "google_maps_url": f"https://www.google.com/maps?q={gps_data.get('latitude')},{gps_data.get('longitude')}"
                }
                # 주소 정보 추가
                if "latitude" in gps_data and "longitude" in gps_data:
                    address = reverse_geocode(gps_data["latitude"], gps_data["longitude"])
                    if address:
                        result_item["address"] = address
                results.append(result_item)
    
    return json.dumps({
        "directory": str(dir_path),
        "total_images": len(results),
        "images_with_location": results
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def geofence_photos(
    directory_path: str,
    center_latitude: float,
    center_longitude: float,
    radius_km: float,
    filter_mode: str = "inside"
) -> str:
    """
    지오펜싱(Geofencing) 기능: 특정 위치를 중심으로 반경 내/외에 있는 사진을 필터링합니다.
    
    지오펜싱이란?
    - 특정 지리적 경계(geographic boundary)를 정의하는 기술
    - 지정한 중심점에서 반경 거리 내에 있는지 밖에 있는지 판단
    - 예: "서울시청에서 5km 반경 내 사진", "집 주변 1km 내 사진" 등
    
    Args:
        directory_path: 이미지 파일들이 있는 디렉토리 경로
        center_latitude: 중심점의 위도
        center_longitude: 중심점의 경도
        radius_km: 반경 (킬로미터)
        filter_mode: "inside" (반경 내) 또는 "outside" (반경 외)
        
    Returns:
        JSON 형식의 필터링된 사진 목록
    """
    dir_path = Path(directory_path)
    
    if not dir_path.exists():
        return json.dumps({"error": f"디렉토리를 찾을 수 없습니다: {directory_path}"}, ensure_ascii=False)
    
    if not dir_path.is_dir():
        return json.dumps({"error": f"디렉토리가 아닙니다: {directory_path}"}, ensure_ascii=False)
    
    if filter_mode not in ["inside", "outside"]:
        return json.dumps({
            "error": "filter_mode는 'inside' 또는 'outside'여야 합니다."
        }, ensure_ascii=False)
    
    supported_formats = {'.jpg', '.jpeg', '.tiff', '.tif', '.png'}
    results = []
    
    for image_file in dir_path.iterdir():
        if image_file.is_file() and image_file.suffix.lower() in supported_formats:
            gps_data = extract_gps_from_exif(str(image_file))
            if gps_data and "error" not in gps_data and "latitude" in gps_data and "longitude" in gps_data:
                distance = calculate_distance(
                    center_latitude,
                    center_longitude,
                    gps_data["latitude"],
                    gps_data["longitude"]
                )
                
                is_inside = distance <= radius_km
                
                if (filter_mode == "inside" and is_inside) or (filter_mode == "outside" and not is_inside):
                    result_item = {
                        "filename": image_file.name,
                        "path": str(image_file),
                        "location": gps_data,
                        "distance_km": round(distance, 2),
                        "google_maps_url": f"https://www.google.com/maps?q={gps_data.get('latitude')},{gps_data.get('longitude')}"
                    }
                    # 주소 정보 추가
                    address = reverse_geocode(gps_data["latitude"], gps_data["longitude"])
                    if address:
                        result_item["address"] = address
                    results.append(result_item)
    
    return json.dumps({
        "directory": str(dir_path),
        "center": {
            "latitude": center_latitude,
            "longitude": center_longitude
        },
        "radius_km": radius_km,
        "filter_mode": filter_mode,
        "total_matching_images": len(results),
        "images": results
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def remove_gps_from_photo(
    image_path: str,
    create_backup: bool = True,
    output_path: Optional[str] = None
) -> str:
    """
    사진 파일에서 GPS 위치 정보를 제거합니다. (사용자가 명시적으로 요청한 경우에만 실행)
    
    주의: 이 기능은 원본 파일을 수정할 수 있습니다. 백업을 생성하는 것을 권장합니다.
    
    Args:
        image_path: 이미지 파일 경로
        create_backup: True인 경우 원본 파일을 .bak 확장자로 백업
        output_path: 새 파일로 저장할 경로 (None이면 원본 파일 수정)
        
    Returns:
        작업 결과 JSON
    """
    path = Path(image_path)
    
    if not path.exists():
        return json.dumps({"error": f"파일을 찾을 수 없습니다: {image_path}"}, ensure_ascii=False)
    
    if not path.is_file():
        return json.dumps({"error": f"파일이 아닙니다: {image_path}"}, ensure_ascii=False)
    
    # 지원하는 이미지 형식 확인 (GPS 제거는 JPEG/TIFF만 지원)
    supported_formats = {'.jpg', '.jpeg', '.tiff', '.tif'}
    if path.suffix.lower() not in supported_formats:
        return json.dumps({
            "error": f"GPS 제거는 JPEG 또는 TIFF 파일만 지원합니다: {path.suffix}",
            "supported_formats": list(supported_formats)
        }, ensure_ascii=False)
    
    try:
        # EXIF 데이터 로드
        exif_dict = piexif.load(str(path))
        
        # GPS 정보가 있는지 확인
        if "GPS" not in exif_dict or not exif_dict["GPS"]:
            return json.dumps({
                "message": "이 이미지에는 GPS 위치 정보가 없습니다.",
                "image_path": str(path)
            }, ensure_ascii=False)
        
        # GPS 정보 제거
        exif_dict.pop("GPS", None)
        
        # 백업 생성
        backup_path = None
        if create_backup:
            backup_path = path.with_suffix(path.suffix + '.bak')
            shutil.copy2(path, backup_path)
        
        # 새 파일 경로 결정
        if output_path:
            output_file = Path(output_path)
        else:
            output_file = path
        
        # EXIF 데이터를 이미지에 다시 저장
        exif_bytes = piexif.dump(exif_dict)
        
        # Pillow를 사용하여 이미지 로드 및 EXIF 저장
        from PIL import Image
        img = Image.open(path)
        img.save(output_file, exif=exif_bytes)
        
        result = {
            "success": True,
            "original_path": str(path),
            "output_path": str(output_file),
            "gps_removed": True
        }
        
        if backup_path:
            result["backup_path"] = str(backup_path)
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"GPS 정보 제거 중 오류 발생: {str(e)}"
        }, ensure_ascii=False)


@mcp.tool()
def mask_location_in_photo(
    image_path: str,
    mask_latitude: float,
    mask_longitude: float,
    mask_radius_km: float,
    create_backup: bool = True,
    output_path: Optional[str] = None
) -> str:
    """
    특정 위치 정보를 마스킹합니다. (사용자가 명시적으로 요청한 경우에만 실행)
    
    지정한 좌표에서 반경 내에 있는 사진의 GPS 정보만 제거합니다.
    예: "집 주변 500m 내 사진의 위치 정보만 제거"
    
    Args:
        image_path: 이미지 파일 경로
        mask_latitude: 마스킹할 중심점의 위도
        mask_longitude: 마스킹할 중심점의 경도
        mask_radius_km: 마스킹할 반경 (킬로미터)
        create_backup: True인 경우 원본 파일을 .bak 확장자로 백업
        output_path: 새 파일로 저장할 경로 (None이면 원본 파일 수정)
        
    Returns:
        작업 결과 JSON
    """
    path = Path(image_path)
    
    if not path.exists():
        return json.dumps({"error": f"파일을 찾을 수 없습니다: {image_path}"}, ensure_ascii=False)
    
    if not path.is_file():
        return json.dumps({"error": f"파일이 아닙니다: {image_path}"}, ensure_ascii=False)
    
    # 지원하는 이미지 형식 확인
    supported_formats = {'.jpg', '.jpeg', '.tiff', '.tif'}
    if path.suffix.lower() not in supported_formats:
        return json.dumps({
            "error": f"위치 마스킹은 JPEG 또는 TIFF 파일만 지원합니다: {path.suffix}",
            "supported_formats": list(supported_formats)
        }, ensure_ascii=False)
    
    try:
        # GPS 정보 추출
        gps_data = extract_gps_from_exif(str(path))
        
        if not gps_data or "error" in gps_data:
            return json.dumps({
                "message": "이 이미지에는 GPS 위치 정보가 없습니다.",
                "image_path": str(path)
            }, ensure_ascii=False)
        
        if "latitude" not in gps_data or "longitude" not in gps_data:
            return json.dumps({
                "message": "이미지의 GPS 정보가 불완전합니다.",
                "image_path": str(path)
            }, ensure_ascii=False)
        
        # 거리 계산
        distance = calculate_distance(
            mask_latitude,
            mask_longitude,
            gps_data["latitude"],
            gps_data["longitude"]
        )
        
        # 마스킹 범위 내에 있는지 확인
        if distance > mask_radius_km:
            return json.dumps({
                "message": "이 이미지는 마스킹 범위 밖에 있습니다.",
                "image_path": str(path),
                "distance_km": round(distance, 2),
                "mask_radius_km": mask_radius_km
            }, ensure_ascii=False)
        
        # GPS 정보 제거 (remove_gps_from_photo 로직 재사용)
        exif_dict = piexif.load(str(path))
        exif_dict.pop("GPS", None)
        
        # 백업 생성
        backup_path = None
        if create_backup:
            backup_path = path.with_suffix(path.suffix + '.bak')
            shutil.copy2(path, backup_path)
        
        # 새 파일 경로 결정
        if output_path:
            output_file = Path(output_path)
        else:
            output_file = path
        
        # EXIF 데이터를 이미지에 다시 저장
        exif_bytes = piexif.dump(exif_dict)
        from PIL import Image
        img = Image.open(path)
        img.save(output_file, exif=exif_bytes)
        
        result = {
            "success": True,
            "original_path": str(path),
            "output_path": str(output_file),
            "location_masked": True,
            "original_location": gps_data,
            "mask_center": {
                "latitude": mask_latitude,
                "longitude": mask_longitude
            },
            "distance_km": round(distance, 2),
            "mask_radius_km": mask_radius_km
        }
        
        if backup_path:
            result["backup_path"] = str(backup_path)
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"위치 마스킹 중 오류 발생: {str(e)}"
        }, ensure_ascii=False)


if __name__ == "__main__":
    import sys
    import os
    
    # FastMCP Cloud 또는 HTTP/SSE transport 모드
    # 환경 변수나 명령줄 인자로 transport 선택
    transport_mode = os.getenv("MCP_TRANSPORT", "stdio")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        transport_mode = "sse"
    elif len(sys.argv) > 1 and sys.argv[1] == "--sse":
        transport_mode = "sse"
    
    if transport_mode == "sse":
        # HTTP/SSE transport 사용 (PlayMCP 등록용, FastMCP Cloud)
        # FastMCP Cloud는 자동으로 포트와 호스트를 설정합니다
        port = int(os.getenv("PORT", "8000"))
        host = os.getenv("HOST", "0.0.0.0")
        mcp.run(transport="sse", host=host, port=port)
    else:
        # 기본: stdio transport (로컬 사용)
        mcp.run()


