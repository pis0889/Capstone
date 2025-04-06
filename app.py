# app.py
from flask import Flask
import pymysql

app = Flask(__name__)

@app.route("/")
def hello():
    return "Flask 서버 정상 동작 중!"

@app.route("/db")
def db_test():
    try:
        conn = pymysql.connect(
            host="capstone-db.c3km22w8k6j9.ap-northeast-2.rds.amazonaws.com",
            user="admin",
            password="capstone125",
            db="MariaDB",
            charset="utf8"
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT NOW();")
            result = cursor.fetchone()
        conn.close()
        return f"DB 연결 성공! 현재 시간: {result[0]}"
    except Exception as e:
        return f"DB 연결 실패: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
