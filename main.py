from flask import Flask, request, jsonify, send_file
import os
import sys

# src 폴더 안의 파일을 import하기 위한 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from scheduler import arrange_timetable, print_timetable
from router import analyze_routes, print_route_report, get_route_summary_text

app = Flask(__name__)


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze_api():
    """
    프론트엔드에서 선택한 과목 ID 목록을 받아서
    시간표 + 이동 경로 분석 결과를 JSON으로 반환한다.
    """
    data = request.get_json() or {}
    selected_ids = data.get("selected_courses", [])

    if not selected_ids:
        return jsonify({
            "error": "선택된 과목이 없습니다."
        }), 400

    try:
        timetable = arrange_timetable(selected_ids)
        route_results = analyze_routes(
            timetable,
            campus_map_path=os.path.join(BASE_DIR, "data", "campus_distance.json")
        )

        return jsonify({
            "selected_courses": selected_ids,
            "timetable": timetable,
            "route_results": route_results,
            "route_summary": get_route_summary_text(route_results)
        })

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 500


@app.route("/api/demo", methods=["GET"])
def demo_api():
    """
    발표/테스트용 기본 예시 실행 API
    """
    selected_ids = [
        "M2177.005500_002",
        "035.001_002",
        "251.101_001",
        "300.111_003"
    ]

    timetable = arrange_timetable(selected_ids)
    route_results = analyze_routes(
        timetable,
        campus_map_path=os.path.join(BASE_DIR, "data", "campus_distance.json")
    )

    return jsonify({
        "selected_courses": selected_ids,
        "timetable": timetable,
        "route_results": route_results,
        "route_summary": get_route_summary_text(route_results)
    })


if __name__ == "__main__":
    selected_ids = [
        "M2177.005500_002",
        "035.001_002",
        "251.101_001",
        "300.111_003"
    ]

    timetable = arrange_timetable(selected_ids)

    print("==================== 시간표 결과 ====================")
    print_timetable(timetable)

    print("==================== 이동 경로 분석 ====================")
    route_results = analyze_routes(
        timetable,
        campus_map_path=os.path.join(BASE_DIR, "data", "campus_distance.json")
    )
    print_route_report(route_results)

    app.run(debug=True)
