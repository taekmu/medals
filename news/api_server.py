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

#new폴더에 있으므로 서버위치 경로를 설정함
# 현재 파일(api_server.py)의 위치를 기준으로 절대 경로를 설정합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")


# 2. 테스트 경로 (반드시 mount보다 위에 작성!)
@app.get("/test-medal")
async def test_medal():
    medal_file = os.path.join(static_path, "medal.html")
    if os.path.exists(medal_file):
        return FileResponse(medal_file)
    
    # 파일이 없을 경우 디버깅 정보 출력
    files_in_static = os.listdir(static_path) if os.path.exists(static_path) else "static 폴더 없음"
    return {
        "status": "error",
        "message": "medal.html을 찾을 수 없습니다.",
        "checked_path": medal_file,
        "files_found": files_in_static,
        "current_dir": os.getcwd()
    }
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
async def medals():
    medal_file = os.path.join(static_path, "index.html")
    if os.path.exists(medal_file):
        return FileResponse(medal_file)
    
    # 파일이 없을 경우 디버깅 정보 출력
    files_in_static = os.listdir(static_path) if os.path.exists(static_path) else "static 폴더 없음"
    return {
        "status": "error",
        "message": "index.html을 찾을 수 없습니다.",
        "checked_path": medal_file,
        "files_found": files_in_static,
        "current_dir": os.getcwd()
    }


#def get_medal():  지금 수정 do(2026-02-06)
#    return medals : 지금 수정 do(2026-02-06)

#app.mount("/static", StaticFiles(directory=static_path), name="static")  지금 수정 do(2026-02-06)
#app.mount("/", StaticFiles(directory=static_path, html=True), name="root")

# 3. 정적 파일 마운트 (가장 마지막에)
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/")
async def read_index():
    index_path = os.path.join(static_path, "index.html")
    return FileResponse(index_path)


print(f"현재 BASE_DIR: {BASE_DIR}", flush=True)
print(f"설정된 static_path: {static_path}", flush=True)
print(f"폴더 존재 여부: {os.path.exists(static_path)}", flush=True)

# api_server.py에 추가
@app.get("/test-medal")
async def serve_medal_file():
    target = os.path.join(static_path, "medal.html")
    if os.path.exists(target):
        return FileResponse(target)
    else:
        # 파일이 실제로 어디 있는지 리스트를 출력해봅니다 (디버깅용)
        files = os.listdir(static_path)
        return {"error": "파일 없음", "path": target, "folder_contents": files}