from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

medal_cache = {
    "data": [],
    "last_update": None
}

def fetch_medals_from_local():
    """medal.html에서 메달 데이터 읽기"""
    try:
        medal_file = os.path.join(static_path, "medal.html")
        medal_data = []
        
        if not os.path.exists(medal_file):
            print(f"Error: {medal_file} not found")
            return []
        
        with open(medal_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        
        # class="country-row" 인 모든 tr 찾기
        rows = soup.find_all("tr", {"class": "country-row"})
        
        for row in rows[:10]:  # 상위 10개
            cols = row.find_all("td")
            if len(cols) >= 4:
                country = cols[0].get_text(strip=True)
                gold = cols[1].get_text(strip=True)
                silver = cols[2].get_text(strip=True)
                bronze = cols[3].get_text(strip=True)
                
                medal_data.append({
                    "country": country,
                    "gold": gold,
                    "silver": silver,
                    "bronze": bronze
                })
        
        print(f"✅ Loaded {len(medal_data)} countries from medal.html")
        return medal_data
    
    except Exception as e:
        print(f"❌ Error reading medal.html: {e}")
        return []

@app.get("/medals")
async def get_medals():
    """메달 데이터 반환 (캐싱 포함)"""
    global medal_cache
    now = datetime.now()
    
    # 캐시가 유효하면 반환 (5분 이내)
    if (medal_cache["last_update"] is not None and 
        now - medal_cache["last_update"] < timedelta(minutes=5) and
        len(medal_cache["data"]) > 0):
        return medal_cache["data"]
    
    # 새로운 데이터 읽기
    medal_cache["data"] = fetch_medals_from_local()
    medal_cache["last_update"] = now
    
    return medal_cache["data"]

@app.get("/")
async def read_index():
    """인덱스 페이지"""
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": "index.html not found"}

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "ok",
        "medals_cached": len(medal_cache["data"]) > 0,
        "last_update": medal_cache["last_update"].isoformat() if medal_cache["last_update"] else None
    }

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000)
