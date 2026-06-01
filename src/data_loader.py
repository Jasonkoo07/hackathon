# src/data_loader.py
import json
import os

def load_json_file(file_path):
    """지정한 경로의 JSON 파일을 안전하게 읽어오는 공통 함수"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ [에러] 파일이 누락되었습니다: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_user_schedule(base_dir="."):
    """
    사용자가 선택한 과목을 기반으로 가상 데이터 매칭 및 
    캠퍼스 건물/거리 맵 데이터를 함께 바인딩하여 딕셔너리로 반환합니다.
    """
    input_path = os.path.join(base_dir, "sample_input.json")
    course_path = os.path.join(base_dir, "data", "course_data.json")
    distance_path = os.path.join(base_dir, "data", "campus_distance.json")
    
    # 데이터 로드
    user_input = load_json_file(input_path)
    all_courses = load_json_file(course_path)
    campus_map_data = load_json_file(distance_path)
    
    selected_ids = user_input.get("selected_courses", [])
    my_courses_info = {}
    
    # 입력 과목 검증 및 매칭
    for c_id in selected_ids:
        if c_id in all_courses:
            my_courses_info[c_id] = all_courses[c_id]
        else:
            print(f"⚠️ [경고] 데이터베이스에 없는 과목 번호 식별됨: {c_id}")
            
    return {
        "my_courses": my_courses_info,
        "map_data": campus_map_data
    }

# 독립 실행 테스트 로그 기능
if __name__ == "__main__":
    # 데이터 테스트를 위한 임시 상위 경로 조정 시도
    try:
        # 현재 위치가 src 폴더인 경우 프로젝트 루트 기준으로 읽기 위함
        test_dir = "../" if os.path.basename(os.getcwd()) == "src" else "."
        data = get_user_schedule(base_dir=test_dir)
        print("="*50)
        print("✅ [팀원 A] 대용량 가상 캠퍼스 데이터 파싱 검증 완료!")
        print(f"▶ 로드 성공한 사용자 선택 강좌: {len(data['my_courses'])}개")
        print(f"▶ 시스템 내 전체 매핑 등록 건물 수: {len(data['map_data']['buildings'])}개")
        print("="*50)
    except Exception as e:
        print(f"❌ [팀원 A 데이터 로딩 실패]: {e}")
