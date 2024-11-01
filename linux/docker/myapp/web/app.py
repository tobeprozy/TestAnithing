from flask import Flask
import pymysql
import os

app = Flask(__name__)

@app.route('/')
def hello():
    db = pymysql.connect(host=os.getenv('DATABASE_HOST'),
                         user=os.getenv('DATABASE_USER'),
                         password=os.getenv('DATABASE_PASSWORD'),
                         db=os.getenv('DATABASE_NAME'))
    cursor = db.cursor()
    cursor.execute("SELECT VERSION()")
    data = cursor.fetchone()
    return "Database version : " + str(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
