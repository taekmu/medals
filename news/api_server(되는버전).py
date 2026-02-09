from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from bs4 import BeautifulSoup

# 1. 여기서 app을 정의해줘야 에러가 안 납니다!
app = FastAPI()

# CORS 설정 (위젯 접속 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

# 2. 메달 데이터 추출 로직 (크롤링)
@app.get("/medals")
async def get_medals():
    medal_file = os.path.join(static_path, "medal.html")
    medal_data = []

    if os.path.exists(medal_file):
        try:
            with open(medal_file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            rows = soup.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    medal_data.append({
                        "country": cols[0].get_text(strip=True),
                        "gold": cols[1].get_text(strip=True),
                        "silver": cols[2].get_text(strip=True),
                        "bronze": cols[3].get_text(strip=True)
                    })
        except Exception as e:
            print(f"Error: {e}")

    # 데이터가 없으면 빈 리스트 [] 반환 (그래야 widget.js가 안 죽음)
    return medal_data

# 3. 기본 인덱스 페이지
@app.get("/")
async def read_index():
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": "index.html not found"}

# 4. 정적 파일 마운트 (맨 아래에 위치)
app.mount("/static", StaticFiles(directory=static_path), name="static")