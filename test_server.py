"""서버 테스트 스크립트"""
import sys
import os

# 현재 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import server
    print("✓ 서버 모듈 로드 성공")
    
    # 도구 등록 확인
    if hasattr(server.mcp, 'tools'):
        tools = server.mcp.tools
        print(f"✓ 등록된 도구 개수: {len(tools)}")
        for tool_name in tools.keys():
            print(f"  - {tool_name}")
    else:
        print("⚠ 도구 정보를 확인할 수 없습니다")
    
    # 함수 확인
    if hasattr(server, 'get_photo_location'):
        print("✓ get_photo_location 함수 존재")
    if hasattr(server, 'batch_get_photo_locations'):
        print("✓ batch_get_photo_locations 함수 존재")
    if hasattr(server, 'extract_gps_from_exif'):
        print("✓ extract_gps_from_exif 함수 존재")
    
    print("\n✅ 서버 코드 검증 완료!")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

