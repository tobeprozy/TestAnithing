from flask import Flask, jsonify

app = Flask(__name__)

# 测试路由
@app.route('/api/test', methods=['GET'])
def test():
    data = {"message": "Hello from Flask!"}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
