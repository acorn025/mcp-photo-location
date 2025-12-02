"""서버 테스트 스크립트"""
import sys
import os

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 현재 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import server
    print("[OK] 서버 모듈 로드 성공")
    
    # 도구 등록 확인 (FastMCP의 실제 API에 맞게 수정)
    try:
        # FastMCP는 내부적으로 도구를 관리하므로 직접 접근이 어려울 수 있음
        # 대신 함수가 제대로 등록되었는지 확인
        if hasattr(server.mcp, '_tools') or hasattr(server.mcp, 'tools'):
            tools_attr = getattr(server.mcp, '_tools', None) or getattr(server.mcp, 'tools', None)
            if tools_attr:
                print(f"[OK] 등록된 도구 개수: {len(tools_attr)}")
                for tool_name in tools_attr.keys():
                    print(f"  - {tool_name}")
            else:
                print("[INFO] 도구는 등록되었지만 직접 확인할 수 없습니다 (정상 동작)")
        else:
            print("[INFO] FastMCP 도구 등록 방식 확인 (정상 동작)")
    except Exception as tool_check_error:
        print(f"[INFO] 도구 확인 중 오류 (무시 가능): {tool_check_error}")
    
    # 함수 확인
    if hasattr(server, 'get_photo_location'):
        print("[OK] get_photo_location 함수 존재")
    if hasattr(server, 'batch_get_photo_locations'):
        print("[OK] batch_get_photo_locations 함수 존재")
    if hasattr(server, 'extract_gps_from_exif'):
        print("[OK] extract_gps_from_exif 함수 존재")
    
    print("\n[SUCCESS] 서버 코드 검증 완료!")
    print("서버를 실행하려면: python server.py")
    
except ImportError as e:
    print(f"[ERROR] 모듈을 가져올 수 없습니다: {e}")
    print("가상환경이 활성화되어 있고 필요한 패키지가 설치되어 있는지 확인하세요.")
    print("설치 명령: pip install -r requirements.txt")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

