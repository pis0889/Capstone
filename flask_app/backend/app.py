from flask import Flask, redirect, request, session
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import pymysql
import os
import requests

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

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = "https://pkplantcare.shop/auth/kakao/callback"
KAKAO_API_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = "https://pkplantcare.shop/callback"


AUTH_BASE_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
USER_INFO_URL = 'https://www.googleapis.com/userinfo/v2/me'

SCOPE = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email'
]

# 네이버 OAuth 설정
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = "https://pkplantcare.shop/auth/naver/callback"

NAVER_AUTH_URL = "https://nid.naver.com/oauth2.0/authorize"
NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
NAVER_USER_INFO_URL = "https://openapi.naver.com/v1/nid/me"

@app.route('/auth/login/naver')
def naver_login():
    # 네이버 로그인 페이지로 리디렉션하는 URL
    naver_oauth = OAuth2Session(NAVER_CLIENT_ID, redirect_uri=NAVER_REDIRECT_URI)
    auth_url, state = naver_oauth.authorization_url(NAVER_AUTH_URL)
    session['oauth_state'] = state  # 상태값 저장
    return redirect(auth_url)

@app.route('/auth/naver/callback')
def naver_callback():
    # 네이버에서 받은 인증 코드
    code = request.args.get('code')

    # 토큰을 요청할 URL
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': NAVER_CLIENT_ID,
        'client_secret': NAVER_CLIENT_SECRET,
        'redirect_uri': NAVER_REDIRECT_URI,
        'code': code,
    }

    # 엑세스 토큰 요청
    token_response = requests.post(NAVER_TOKEN_URL, data=token_data)
    token_info = token_response.json()
    access_token = token_info.get('access_token')

    if access_token:
        # 엑세스 토큰으로 사용자 정보 요청
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        user_info_response = requests.get(NAVER_USER_INFO_URL, headers=headers)
        user_info = user_info_response.json()

        # 사용자 정보 처리 (예: 세션에 저장하거나 DB에 저장)
        session['user_info'] = user_info

        return f"Hello, {user_info['response']['name']}!"  # 사용자 이름 출력

    return 'Failed to get the access token.'


@app.route('/auth/login/kakao')
def kakao_login():
    # 카카오 로그인 페이지로 리디렉션하는 URL
    kakao_api_url = 'https://kauth.kakao.com/oauth/authorize'
    url = f"{kakao_api_url}?client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code"
    return redirect(url)

@app.route('/auth/kakao/callback')
def kakao_callback():
    # 카카오에서 받은 인증 코드
    code = request.args.get('code')

    # 토큰을 요청할 URL
    token_url = 'https://kauth.kakao.com/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': KAKAO_CLIENT_ID,
        'redirect_uri': KAKAO_REDIRECT_URI,
        'code': code,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # 액세스 토큰 요청
    response = requests.post(token_url, data=data, headers=headers)
    access_token = response.json().get('access_token')

    if access_token:
        # 액세스 토큰을 사용하여 카카오 API로 사용자 정보 요청
        user_info_url = 'https://kapi.kakao.com/v2/user/me'
        user_info_headers = {
            'Authorization': f'Bearer {access_token}',
        }
        user_info_response = requests.get(user_info_url, headers=user_info_headers)
        user_info = user_info_response.json()

        # 사용자 정보 처리 (예: 세션에 저장하거나 DB에 저장)
        session['user_info'] = user_info

        return f'Hello, {user_info["properties"]["nickname"]}!'

    return 'Failed to get the access token.'



@app.route('/')
def index():
    return '구글 로그인 데모 – /login 으로 이동하세요'


@app.route('/login')
def login():
    google = OAuth2Session(GOOGLE_CLIENT_ID, scope=SCOPE, redirect_uri=GOOGLE_REDIRECT_URI)
    auth_url, state = google.authorization_url(AUTH_BASE_URL,
                                               access_type='offline', prompt='select_account')
    session['oauth_state'] = state
    print("[/login] oauth_state 저장됨:", state)
    return redirect(auth_url)


@app.route('/callback')
def callback():
    print("[/callback] 현재 세션:", dict(session))
    google = OAuth2Session(GOOGLE_CLIENT_ID, state=session['oauth_state'], redirect_uri=GOOGLE_REDIRECT_URI)
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

