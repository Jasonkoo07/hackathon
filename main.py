'''
I've put any features in it for HTML connection testing.
'''

from flask import Flask, request, jsonify, send_file

app = Flask(__name__)


def add_two_numbers(number1, number2):
    """Return the sum of exactly two integers."""
    if number1 is None or number2 is None:
        raise ValueError("Please provide both number1 and number2.")
    return number1 + number2


@app.route('/api/add', methods=['POST'])
def add_api():
    data = request.get_json() or {}
    number1 = data.get('number1')
    number2 = data.get('number2')
    try:
        if number1 is None or number2 is None:
            raise ValueError("Please provide both number1 and number2.")
        result = add_two_numbers(number1, number2)
        return jsonify({'sum': result})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 400


@app.route('/')
def index():
    return send_file('index.html')


if __name__ == '__main__':
    app.run(debug=True)

