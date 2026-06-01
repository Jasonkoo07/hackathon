import json
import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
DEFAULT_COURSE_PATH = os.path.join(BASE_DIR, "data", "course_data.json")

# Mapping for Korean day names to English abbreviations used in analysis
DAY_MAP = {
    "월": "Mon", "화": "Tue", "수": "Wed", "목": "Thu", "금": "Fri", "토": "Sat", "일": "Sun"
}

def read_courses(file_path=DEFAULT_COURSE_PATH):
    """
    Reads course data from a JSON file.
    Returns a list of course dictionaries or None if an error occurs.
    """
    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' not found.")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        processed_courses = {}
        for course_id, info in raw_data.items():
            # Convert Korean days to English (e.g., ["월", "수"] -> ["Mon", "Wed"])
            eng_days = [DAY_MAP.get(d, d) for d in info.get('day', [])]
            
            # Parse time string "10:00~11:15" into start and end
            time_slots = info.get('time', [])
            start_time, end_time = "", ""
            if time_slots:
                # We take the first slot as the representative time for the analysis logic
                parts = time_slots[0].split('~')
                if len(parts) == 2:
                    start_time, end_time = parts[0], parts[1]
            
            # Parse exam string "2026-07-13 10:00" into date and time
            exam_str = info.get('exam', '')
            exam_parts = exam_str.split(' ')
            exam_date = exam_parts[0] if len(exam_parts) > 0 else ""
            exam_time = exam_parts[1] if len(exam_parts) > 1 else ""

            # Reconstruct into the format expected by analyze_schedule and analyze_exams
            processed_courses[course_id] = {
                "id": course_id,
                "name": info.get('name', ''),
                "building": info.get('building_no', ''),
                "classroom": info.get('classroom', ''),
                "start": start_time,
                "end": end_time,
                "days": eng_days,
                "exam_date": exam_date,
                "exam_time": exam_time,
                "professor": info.get('professor', 'N/A')
            }
        return processed_courses

    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON in '{file_path}'. {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading '{file_path}': {e}")
        return None

def sort_timetable(courses_list):
    """
    Sorts a list of course dictionaries by their start time.
    """
    return sorted(courses_list, key=lambda x: x.get('start', '00:00'))

def arrange_timetable(courses_id_list):
    
    """
    Organizes a list of course IDs into a timetable structure grouped by day.
    Returns a dictionary where keys are days (Mon-Fri) and values are sorted course lists.
    """
    all_courses = read_courses()
    if not all_courses:
        return {}

    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    timetable = {day: [] for day in days}

    for cid in courses_id_list:
        if cid in all_courses:
            course_info = all_courses[cid]
            for day in course_info['days']:
                if day in timetable:
                    timetable[day].append(course_info)

    # Sort each day's courses by start time
    for day in timetable:
        timetable[day] = sort_timetable(timetable[day])

    return timetable

def print_timetable(timetable):
    """
    Prints the organized timetable in a human-readable format.
    """
    if not timetable:
        print("No timetable data to display.")
        return

    print("\n" + "="*70)
    print(f"{'WEEKLY CAMPUS SCHEDULE':^70}")
    print("="*70)
    
    for day, courses in timetable.items():
        print(f"\n[ {day} ]")
        if not courses:
            print("  - No classes scheduled.")
            continue
        
        for course in courses:
            time_str = f"{course['start']} - {course['end']}"
            location = f"{course['building']} ({course['classroom']})"
            print(f"  {time_str:<15} | {course['name']} ({course['id']})")
            print(f"  {'':<15} | Location: {location} | Prof: {course['professor']}")
    
    print("\n" + "="*70 + "\n")

def check_exam_conflicts(courses_id_list):
    """
    Checks whether selected courses have exam time conflicts.
    Returns a list of conflict warning messages.
    """
    all_courses = read_courses()
    if not all_courses:
        return []

    exam_table = {}
    conflicts = []

    for cid in courses_id_list:
        if cid not in all_courses:
            continue

        course = all_courses[cid]
        exam_key = f"{course.get('exam_date', '')} {course.get('exam_time', '')}".strip()

        if not exam_key:
            continue

        if exam_key not in exam_table:
            exam_table[exam_key] = []

        exam_table[exam_key].append(course)

    for exam_time, courses in exam_table.items():
        if len(courses) >= 2:
            course_names = [course["name"] for course in courses]
            conflicts.append({
                "exam_time": exam_time,
                "courses": course_names,
                "message": f"🚨 시험 시간 충돌: {exam_time} / {', '.join(course_names)}"
            })

    return conflicts


def print_exam_conflicts(conflicts):
    """
    Prints exam conflict results.
    """
    print("\n" + "=" * 70)
    print(f"{'📝 EXAM CONFLICT CHECK':^70}")
    print("=" * 70)

    if not conflicts:
        print("✅ 시험 시간이 겹치는 과목이 없습니다.")
    else:
        for conflict in conflicts:
            print(conflict["message"])

    print("=" * 70 + "\n")

if __name__ == "__main__":
    # Example usage for testing purposes
    test_ids = ["M2177.005500_002", "035.001_002", "251.101_001", "300.111_003"]
    timetable = arrange_timetable(test_ids)
    print_timetable(timetable)
