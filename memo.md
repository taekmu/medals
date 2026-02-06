uvicorn api_server:app --reload --port 8000
python -m pip install --upgrade pip
최소 3개 파일 있어야 함 : requirement.txt, start.sh, api_server.py
git init
git add .
git commit -m "메달 보드 프로젝트 초기화 및 DB 연동 완료"
git status
# 1. 메인 브랜치 이름을 main으로 설정
git branch -M main

# 2. 내 컴퓨터와 GitHub 저장소 연결 (URL은 본인 것으로 교체!)
git remote add origin https://github.com/아이디/저장소이름.git

git push -u origin main

Render 접속
https://dashboard.render.com/login


Start Command
uvicorn api_server:app --host 0.0.0.0 --port $PORT

✅ 가장 쉬운 방법 (FastAPI에 정적파일 추가)
프로젝트에 static 폴더 만들기
news/
  api_server.py
  requirements.txt
  static/
      widget.js

2️⃣ api_server.py 수정 ⭐⭐⭐

맨 위 import 추가

from fastapi.staticfiles import StaticFiles


그리고 app = FastAPI() 아래

app.mount("/static", StaticFiles(directory="static"), name="static")

3️⃣ Git push
git add .
git commit -m "add widget"
git push