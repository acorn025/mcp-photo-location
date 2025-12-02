"""
MCP Photo Location Server
사진 파일에서 GPS 위치 정보를 추출하는 MCP 서버
"""
from fastmcp import FastMCP
from pathlib import Path
import piexif
from typing import Optional, Dict, Any
import json

# MCP 서버 인스턴스 생성
mcp = FastMCP("Photo Location Server")


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
    
    result = {
        "image_path": str(path),
        "location": gps_data,
        "google_maps_url": f"https://www.google.com/maps?q={gps_data.get('latitude')},{gps_data.get('longitude')}"
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


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
                results.append({
                    "filename": image_file.name,
                    "path": str(image_file),
                    "location": gps_data,
                    "google_maps_url": f"https://www.google.com/maps?q={gps_data.get('latitude')},{gps_data.get('longitude')}"
                })
    
    return json.dumps({
        "directory": str(dir_path),
        "total_images": len(results),
        "images_with_location": results
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()


