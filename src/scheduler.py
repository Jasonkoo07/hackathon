import json
import os

def read_courses(file_path='data/course_data.json'):
    """
    Reads course data from a JSON file.
    Returns a list of course dictionaries or None if an error occurs.
    """
    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' not found.")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON in '{file_path}'. {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading '{file_path}': {e}")
        return None

if __name__ == "__main__":
    # Example usage for testing purposes
    courses = read_courses()
    if courses:
        print(f"Successfully loaded {len(courses)} courses.")
        for course in courses:
            print(course)
    else:
        print("Failed to load courses.")
