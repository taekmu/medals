uvicorn api_server:app --reload --port 8000
python -m pip install --upgrade pip
최소 3개 파일 있어야 함 : requirement.txt, start.sh, api_server.py
git init
git add .
git commit -m "first deploy"