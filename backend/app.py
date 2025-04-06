# app.py
from flask import Flask
from dotenv import load_dotenv
import pymysql
import os
app = Flask(__name__)

load_dotenv()


@app.route("/")
def hello():
    return "Flask 서버 정상 동작 중!"

@app.route("/db")
def db_test():
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
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
