
import json
import os
import math

DEFAULT_BREAK_MINUTES = 15
WALKING_SPEED_M_PER_MIN = 80  # 보통 도보 속도 약 4.8km/h 기준


def load_campus_map(file_path="campus_distance.json"):
    """campus_distance.json 파일을 읽어서 캠퍼스 지도 데이터를 반환한다."""
    if not os.path.exists(file_path):
        alt_path = os.path.join("data", "campus_distance.json")
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            raise FileNotFoundError(f"캠퍼스 거리 데이터 파일을 찾을 수 없습니다: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def time_to_minutes(time_text):
    """'10:30' 형식의 시간을 0시 기준 분 단위 정수로 바꾼다."""
    if not time_text:
        return 0
    hour, minute = time_text.split(":")
    return int(hour) * 60 + int(minute)


def building_label(building_no, campus_map):
    """건물 번호를 보기 좋은 건물 이름으로 바꾼다."""
    building_no = str(building_no)
    buildings = campus_map.get("buildings", {})
    if building_no in buildings:
        return buildings[building_no].get("name", f"{building_no}동")
    return f"{building_no}동"


def estimate_distance_by_position(start_building, end_building, campus_map):
    """
    거리 데이터가 직접 없을 때, x/y 좌표를 이용해 대략적인 이동 시간을 계산한다.
    실제 지도 경로가 아니라 Mock Data 보완용 추정값이다.
    """
    buildings = campus_map.get("buildings", {})
    start_info = buildings.get(str(start_building))
    end_info = buildings.get(str(end_building))

    if not start_info or not end_info:
        return None

    dx = start_info.get("x", 0) - end_info.get("x", 0)
    dy = start_info.get("y", 0) - end_info.get("y", 0)
    straight_distance = math.sqrt(dx * dx + dy * dy)

    # Mock 좌표는 실제 m 단위가 아니므로, 보기 좋은 결과가 나오도록 1.5 보정값 사용
    estimated_minutes = math.ceil((straight_distance * 1.5) / WALKING_SPEED_M_PER_MIN)
    return max(1, estimated_minutes)


def get_travel_time(start_building, end_building, campus_map):
    """
    두 건물 사이 도보 이동 시간을 반환한다.
    같은 건물이면 0분, campus_distance.json에 직접 있으면 그 값을 사용한다.
    직접 데이터가 없으면 좌표 기반 추정값을 사용한다.
    """
    start_building = str(start_building)
    end_building = str(end_building)

    if start_building == end_building:
        return 0

    distances = campus_map.get("distances", {})
    direct_key = f"{start_building}-{end_building}"
    reverse_key = f"{end_building}-{start_building}"

    if direct_key in distances:
        return distances[direct_key]
    if reverse_key in distances:
        return distances[reverse_key]

    estimated = estimate_distance_by_position(start_building, end_building, campus_map)
    if estimated is not None:
        return estimated

    return None


def make_route_text(start_course, end_course, travel_time, campus_map):
    """[건물A] --(도보 n분)--> [건물B] 형식의 텍스트 지도를 만든다."""
    start_building = start_course.get("building", "?")
    end_building = end_course.get("building", "?")
    start_name = building_label(start_building, campus_map)
    end_name = building_label(end_building, campus_map)

    if travel_time is None:
        return f"[{start_name}] ──(🚶 이동시간 데이터 없음)──> [{end_name}]"
    return f"[{start_name}] ──(🚶 도보 {travel_time}분)──> [{end_name}]"


def analyze_daily_routes(day, courses, campus_map, default_break_minutes=DEFAULT_BREAK_MINUTES):
    """
    하루 시간표 안에서 앞뒤 수업 이동 시간을 분석한다.
    Team B가 이미 정렬해 준 courses를 받는 것을 기준으로 한다.
    """
    results = []

    if len(courses) < 2:
        return results

    for i in range(len(courses) - 1):
        current_course = courses[i]
        next_course = courses[i + 1]

        current_end = time_to_minutes(current_course.get("end", "00:00"))
        next_start = time_to_minutes(next_course.get("start", "00:00"))
        break_time = next_start - current_end

        # 시간이 겹치거나 바로 이어지는 경우도 분석 대상에 포함한다.
        travel_time = get_travel_time(
            current_course.get("building", ""),
            next_course.get("building", ""),
            campus_map
        )

        route_text = make_route_text(current_course, next_course, travel_time, campus_map)

        if break_time < 0:
            status = "OVERLAP"
            message = "🚨 [경고] 수업 시간이 겹칩니다. 이동 여부와 관계없이 시간표 수정이 필요합니다."
        elif travel_time is None:
            status = "UNKNOWN"
            message = "⚠️ [주의] 이동 시간 데이터가 없어 지각 위험을 정확히 판단할 수 없습니다."
        elif travel_time > break_time:
            status = "LATE_RISK"
            message = f"⚠️ [경고] 쉬는 시간은 {break_time}분인데 이동 시간이 {travel_time}분이라 지각 위험이 있습니다!"
        elif break_time <= default_break_minutes:
            status = "CONSECUTIVE_OK"
            message = f"✅ 연강이지만 이동 가능해 보입니다. 쉬는 시간 {break_time}분 / 이동 시간 {travel_time}분"
        else:
            status = "OK"
            message = f"✅ 이동 가능: 쉬는 시간 {break_time}분 / 이동 시간 {travel_time}분"

        results.append({
            "day": day,
            "from_course": current_course.get("name", "Unknown"),
            "to_course": next_course.get("name", "Unknown"),
            "from_time": f"{current_course.get('start', '')}~{current_course.get('end', '')}",
            "to_time": f"{next_course.get('start', '')}~{next_course.get('end', '')}",
            "from_building": current_course.get("building", ""),
            "to_building": next_course.get("building", ""),
            "break_time": break_time,
            "travel_time": travel_time,
            "route_text": route_text,
            "status": status,
            "message": message
        })

    return results


def analyze_routes(timetable, campus_map=None, campus_map_path="campus_distance.json"):
    """
    전체 주간 시간표의 이동 경로를 분석한다.
    입력: scheduler.arrange_timetable()이 반환한 timetable 딕셔너리
    출력: 이동 분석 결과 리스트
    """
    if campus_map is None:
        campus_map = load_campus_map(campus_map_path)

    all_results = []
    for day, courses in timetable.items():
        all_results.extend(analyze_daily_routes(day, courses, campus_map))

    return all_results


def print_route_report(route_results):
    """이동 분석 결과를 터미널에 보기 좋게 출력한다."""
    print("\n" + "=" * 70)
    print(f"{'🚶 CAMPUS ROUTE GUIDE':^70}")
    print("=" * 70)

    if not route_results:
        print("✅ 분석할 연속 수업이 없습니다.")
        print("=" * 70 + "\n")
        return

    for item in route_results:
        print(f"\n[{item['day']}]")
        print(f"{item['from_course']} ({item['from_time']})")
        print("   ↓")
        print(f"{item['to_course']} ({item['to_time']})")
        print(f"🗺️  {item['route_text']}")
        print(item["message"])

    print("\n" + "=" * 70 + "\n")


def get_route_summary_text(route_results):
    """웹/README/main.py에서 재사용하기 좋은 문자열 요약을 반환한다."""
    if not route_results:
        return "✅ 분석할 연속 수업이 없습니다."

    lines = []
    for item in route_results:
        lines.append(
            f"[{item['day']}] {item['from_course']} → {item['to_course']}\n"
            f"{item['route_text']}\n"
            f"{item['message']}"
        )
    return "\n\n".join(lines)


if __name__ == "__main__":
    # 단독 테스트용 예시
    from scheduler import arrange_timetable

    test_ids = ["M2177.005500_002", "035.001_002", "251.101_001", "300.111_003"]
    test_timetable = arrange_timetable(test_ids)
    test_map = load_campus_map()
    test_results = analyze_routes(test_timetable, test_map)
    print_route_report(test_results)
