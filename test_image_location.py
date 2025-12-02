"""
이미지 GPS 정보 테스트 스크립트
이미지 파일을 드래그 앤 드롭하거나 경로를 입력하세요.
"""
import sys
import os
import json
from pathlib import Path

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 현재 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def find_recent_images():
    """최근 이미지 파일들을 찾습니다."""
    recent_images = []
    search_paths = [
        Path.home() / "Downloads",
        Path.home() / "Pictures",
        Path.home() / "Desktop",
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            try:
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.tif']:
                    images = list(search_path.glob(ext))
                    recent_images.extend(images)
            except:
                pass
    
    # 최근 수정 시간순으로 정렬
    recent_images.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return recent_images[:10]  # 최근 10개만

try:
    from server import extract_gps_from_exif
    import json
    import base64
    
    print("=" * 70)
    print("이미지 GPS 정보 테스트")
    print("=" * 70)
    
    # 이미지 파일 경로 입력 받기
    image_path = None
    
    if len(sys.argv) > 1:
        # 명령줄 인자로 경로 제공
        image_path = Path(sys.argv[1].strip().strip('"'))
    else:
        # 최근 이미지 파일 찾기
        print("\n최근 이미지 파일을 찾는 중...")
        recent_images = find_recent_images()
        
        if recent_images:
            print("\n최근 이미지 파일 목록:")
            for i, img in enumerate(recent_images, 1):
                print(f"  {i}. {img.name} ({img.parent})")
            print(f"  {len(recent_images) + 1}. 직접 경로 입력")
            
            choice = input(f"\n선택하세요 (1-{len(recent_images) + 1}): ").strip()
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(recent_images):
                    image_path = recent_images[choice_num - 1]
                else:
                    # 직접 경로 입력
                    image_path = Path(input("\n이미지 파일 경로를 입력하세요 (드래그 앤 드롭 가능): ").strip().strip('"'))
            except (ValueError, IndexError):
                # 직접 경로 입력
                image_path = Path(input("\n이미지 파일 경로를 입력하세요 (드래그 앤 드롭 가능): ").strip().strip('"'))
        else:
            # 직접 경로 입력
            image_path = Path(input("\n이미지 파일 경로를 입력하세요 (드래그 앤 드롭 가능): ").strip().strip('"'))
    
    if not image_path.exists():
        print(f"\n[ERROR] 파일을 찾을 수 없습니다: {image_path}")
        print("\n팁: 파일을 탐색기에서 이 창으로 드래그 앤 드롭하면 경로가 자동으로 입력됩니다.")
        sys.exit(1)
    
    print(f"\n[INFO] 이미지 파일: {image_path}")
    print(f"[INFO] 파일 크기: {image_path.stat().st_size / 1024:.2f} KB")
    print(f"[INFO] 전체 경로: {image_path.absolute()}")
    print("\n" + "-" * 70)
    print("이미지를 Base64로 변환 중...")
    print("-" * 70)
    
    # 이미지를 Base64로 변환
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # 이미지 형식 결정
    suffix = image_path.suffix.lower()
    format_map = {
        '.jpg': 'jpg',
        '.jpeg': 'jpg',
        '.png': 'png',
        '.tiff': 'tiff',
        '.tif': 'tiff'
    }
    image_format = format_map.get(suffix, 'jpg')
    
    print(f"[INFO] Base64 인코딩 완료 (길이: {len(image_base64)} 문자)")
    print(f"[INFO] 이미지 형식: {image_format}")
    print("\n" + "-" * 70)
    print("Base64 데이터로 GPS 정보 추출 중...")
    print("-" * 70)
    
    # Base64 데이터로 GPS 정보 추출 (내부 구현 함수 직접 호출)
    from server import _get_photo_location_from_base64_impl
    
    # Base64 데이터로 GPS 정보 추출
    result_json = _get_photo_location_from_base64_impl(image_base64, image_format)
    result_dict = json.loads(result_json)
    
    # 기존 방식으로도 추출 (비교용)
    print("\n" + "-" * 70)
    print("파일 경로로 GPS 정보 추출 중 (비교용)...")
    print("-" * 70)
    
    gps_data = extract_gps_from_exif(str(image_path))
    
    # Base64 방식 결과 출력
    print("\n" + "=" * 70)
    print("Base64 방식 결과")
    print("=" * 70)
    print(json.dumps(result_dict, ensure_ascii=False, indent=2))
    
    if "location" in result_dict:
        loc = result_dict["location"]
        print("\n" + "=" * 70)
        print("위치 정보 요약 (Base64 방식)")
        print("=" * 70)
        print(f"위도: {loc.get('latitude', 'N/A')}")
        print(f"경도: {loc.get('longitude', 'N/A')}")
        if 'altitude' in loc:
            print(f"고도: {loc.get('altitude', 'N/A')} m")
        if 'google_maps_url' in result_dict:
            print(f"\nGoogle Maps: {result_dict['google_maps_url']}")
    elif "message" in result_dict:
        print(f"\n[INFO] {result_dict['message']}")
    elif "error" in result_dict:
        print(f"\n[ERROR] {result_dict['error']}")
    
    # 파일 경로 방식 결과 (비교용)
    if gps_data is None:
        file_result = {
            "message": "이 이미지에는 GPS 위치 정보가 없습니다.",
            "image_path": str(image_path)
        }
    elif "error" in gps_data:
        file_result = gps_data
    else:
        file_result = {
            "image_path": str(image_path),
            "location": gps_data,
            "google_maps_url": f"https://www.google.com/maps?q={gps_data.get('latitude')},{gps_data.get('longitude')}"
        }
    
    print("\n" + "=" * 70)
    print("파일 경로 방식 결과 (비교용)")
    print("=" * 70)
    print(json.dumps(file_result, ensure_ascii=False, indent=2))
    
    # 결과 비교
    if "location" in result_dict and "location" in file_result:
        base64_loc = result_dict["location"]
        file_loc = file_result["location"]
        if (base64_loc.get('latitude') == file_loc.get('latitude') and 
            base64_loc.get('longitude') == file_loc.get('longitude')):
            print("\n" + "=" * 70)
            print("✅ 두 방식의 결과가 일치합니다!")
            print("=" * 70)
    
    print("\n" + "=" * 70)
    print("테스트 완료!")
    print("=" * 70)
    print("\n사용법:")
    print("  python test_image_location.py")
    print("  python test_image_location.py \"이미지경로\"")
    print("  (파일을 스크립트에 드래그 앤 드롭)")
    
except ImportError as e:
    print(f"[ERROR] 모듈을 가져올 수 없습니다: {e}")
    print("가상환경이 활성화되어 있고 필요한 패키지가 설치되어 있는지 확인하세요.")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

