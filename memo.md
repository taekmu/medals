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

