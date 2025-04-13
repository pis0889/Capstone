# app.py
from flask import Flask, redirect, request, session
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import pymysql
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()
print("SECRET_KEY:", os.getenv("SECRET_KEY"))
app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY"),  # 또는 직접 문자열도 가능: 'abc123!'
    SESSION_COOKIE_SAMESITE="None",      # cross-site 요청에도 쿠키 허용
    SESSION_COOKIE_SECURE=True          # HTTPS가 아닐 때도 허용 (개발 환경에서만!)
)
app.secret_key = os.getenv("SECRET_KEY")



GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = ""


AUTH_BASE_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
USER_INFO_URL = 'https://www.googleapis.com/userinfo/v2/me'

SCOPE = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email'
]

@app.route('/')
def index():
    return '구글 로그인 데모 – /login 으로 이동하세요'


@app.route('/login')
def login():
    google = OAuth2Session(GOOGLE_CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    auth_url, state = google.authorization_url(AUTH_BASE_URL,
                                               access_type='offline', prompt='select_account')
    session['oauth_state'] = state
    print("[/login] oauth_state 저장됨:", state)
    return redirect(auth_url)


@app.route('/callback')
def callback():
    print("[/callback] 현재 세션:", dict(session))
    google = OAuth2Session(GOOGLE_CLIENT_ID, state=session['oauth_state'], redirect_uri=REDIRECT_URI)
    token = google.fetch_token(TOKEN_URL, client_secret=GOOGLE_CLIENT_SECRET,
                               authorization_response=request.url)
    session['oauth_token'] = token

    user_info = google.get(USER_INFO_URL).json()
    return f"""
        ✅ 로그인 완료!<br>
        이름: {user_info['name']}<br>
        이메일: {user_info['email']}<br>
        <img src="{user_info['picture']}" />
    """



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
