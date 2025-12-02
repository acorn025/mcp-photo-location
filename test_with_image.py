"""
이미지 파일을 자동으로 찾아서 Base64로 변환하여 GPS 정보를 추출하는 스크립트
"""
import sys
import os
import json
import base64
from pathlib import Path
from datetime import datetime, timedelta

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def find_recent_images(minutes=30):
    """최근 N분 내에 수정된 이미지 파일들을 찾습니다."""
    recent_images = []
    search_paths = [
        Path.home() / "Downloads",
        Path.home() / "Pictures",
        Path.home() / "Desktop",
    ]
    
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    
    for search_path in search_paths:
        if search_path.exists():
            try:
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.tif']:
                    images = list(search_path.glob(ext))
                    for img in images:
                        try:
                            mtime = datetime.fromtimestamp(img.stat().st_mtime)
                            if mtime > cutoff_time:
                                recent_images.append((img, mtime))
                        except:
                            pass
            except:
                pass
    
    # 최근 수정 시간순으로 정렬
    recent_images.sort(key=lambda x: x[1], reverse=True)
    return [img for img, _ in recent_images[:5]]  # 최근 5개만

try:
    from server import _get_photo_location_from_base64_impl, extract_gps_from_exif
    
    print("=" * 70)
    print("최근 이미지 파일 자동 검색 및 Base64 변환 테스트")
    print("=" * 70)
    
    # 최근 30분 내 이미지 찾기
    print("\n최근 30분 내에 수정된 이미지 파일을 찾는 중...")
    recent_images = find_recent_images(30)
    
    if not recent_images:
        print("\n최근 이미지를 찾을 수 없습니다. 전체 검색을 시도합니다...")
        recent_images = find_recent_images(1440)  # 24시간
    
    if recent_images:
        print(f"\n발견된 이미지: {len(recent_images)}개")
        for i, img in enumerate(recent_images, 1):
            mtime = datetime.fromtimestamp(img.stat().st_mtime)
            print(f"  {i}. {img.name} ({img.parent}) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 가장 최근 이미지로 테스트
        test_image = recent_images[0]
        print(f"\n{'='*70}")
        print(f"테스트 대상: {test_image.name}")
        print(f"{'='*70}")
        
        print(f"\n[INFO] 이미지 파일: {test_image}")
        print(f"[INFO] 파일 크기: {test_image.stat().st_size / 1024:.2f} KB")
        
        # 이미지를 Base64로 변환
        print("\n" + "-" * 70)
        print("이미지를 Base64로 변환 중...")
        print("-" * 70)
        
        with open(test_image, 'rb') as f:
            image_bytes = f.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        suffix = test_image.suffix.lower()
        format_map = {
            '.jpg': 'jpg',
            '.jpeg': 'jpg',
            '.png': 'png',
            '.tiff': 'tiff',
            '.tif': 'tiff'
        }
        image_format = format_map.get(suffix, 'jpg')
        
        print(f"[INFO] Base64 인코딩 완료 (길이: {len(image_base64):,} 문자)")
        print(f"[INFO] 이미지 형식: {image_format}")
        
        # Base64 데이터로 GPS 정보 추출
        print("\n" + "-" * 70)
        print("Base64 데이터로 GPS 정보 추출 중...")
        print("-" * 70)
        
        result_json = _get_photo_location_from_base64_impl(image_base64, image_format)
        result_dict = json.loads(result_json)
        
        print("\n" + "=" * 70)
        print("Base64 방식 결과")
        print("=" * 70)
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))
        
        if "location" in result_dict:
            loc = result_dict["location"]
            print("\n" + "=" * 70)
            print("위치 정보 요약")
            print("=" * 70)
            print(f"위도: {loc.get('latitude', 'N/A')}")
            print(f"경도: {loc.get('longitude', 'N/A')}")
            if 'altitude' in loc:
                print(f"고도: {loc.get('altitude', 'N/A')} m")
            if 'address' in result_dict:
                print(f"\n주소: {result_dict['address']}")
            if 'google_maps_url' in result_dict:
                print(f"\nGoogle Maps: {result_dict['google_maps_url']}")
        elif "message" in result_dict:
            print(f"\n[INFO] {result_dict['message']}")
        elif "error" in result_dict:
            print(f"\n[ERROR] {result_dict['error']}")
        
        print("\n" + "=" * 70)
        print("테스트 완료!")
        print("=" * 70)
        
    else:
        print("\n[ERROR] 이미지 파일을 찾을 수 없습니다.")
        print("\n사용법:")
        print("  1. 이미지 파일을 다운로드 폴더에 저장하세요")
        print("  2. 또는 다음 명령으로 직접 테스트:")
        print('     python test_image_location.py "이미지경로"')
        
except Exception as e:
    print(f"[ERROR] 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

