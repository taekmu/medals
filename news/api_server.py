from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import FileResponse

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

medals = [
    {"country": "USA", "gold": 39, "silver": 41, "bronze": 33},
    {"country": "China", "gold": 38, "silver": 32, "bronze": 18},
    {"country": "KOREA", "gold": 33, "silver": 32, "bronze": 18},
    {"country": "Japan", "gold": 27, "silver": 14, "bronze": 17},
    {"country": "Germany", "gold": 10, "silver": 11, "bronze": 16},     
    {"country": "Canada", "gold": 10, "silver": 11, "bronze": 16},          
    {"country": "Australia", "gold": 10, "silver": 11, "bronze": 16},        
    {"country": "Netherlands", "gold": 10, "silver": 11, "bronze": 16},      
    {"country": "France", "gold": 10, "silver": 11, "bronze": 16},          
    {"country": "Italy", "gold": 10, "silver": 11, "bronze": 16},
]
@app.get("/medals")

def get_medal():
    return medals


#new폴더에 있으므로 서버위치 경로를 설정함
# 현재 파일(api_server.py)의 위치를 기준으로 절대 경로를 설정합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")
#app.mount("/", StaticFiles(directory=static_path, html=True), name="root")

@app.get("/")
async def read_index():
    index_path = os.path.join(static_path, "index.html")
    return FileResponse(index_path)


print(f"현재 BASE_DIR: {BASE_DIR}", flush=True)
print(f"설정된 static_path: {static_path}", flush=True)
print(f"폴더 존재 여부: {os.path.exists(static_path)}", flush=True)