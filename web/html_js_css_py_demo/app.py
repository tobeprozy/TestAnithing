from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    input1 = data.get('input1')
    input2 = data.get('input2')
    try:
        result = int(input1) + int(input2)
    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
