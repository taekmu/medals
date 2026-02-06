from bs4 import BeautifulSoup
import os

@app.get("/medals")
async def get_medals_data():
    medal_file = os.path.join(static_path, "medal.html")
    
    # 파일을 찾지 못하거나 오류가 날 때를 대비해 빈 리스트를 기본값으로 설정
    medal_data = []

    if os.path.exists(medal_file):
        try:
            with open(medal_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 클래스명이 'country-row'인 행들을 추출
            rows = soup.select(".country-row") 
            
            for row in rows:
                try:
                    # 각 칸의 데이터를 안전하게 가져오기
                    name = row.select_one(".name").get_text(strip=True)
                    gold = row.select_one(".gold").get_text(strip=True)
                    silver = row.select_one(".silver").get_text(strip=True)
                    bronze = row.select_one(".bronze").get_text(strip=True)
                    
                    medal_data.append({
                        "country": name,
                        "gold": gold,
                        "silver": silver,
                        "bronze": bronze
                    })
                except Exception:
                    continue # 한 줄이 잘못되어도 나머지는 계속 진행
                    
        except Exception as e:
            print(f"Error parsing file: {e}")

    # [핵심] 성공하든 실패하든 무조건 [ ] (리스트) 형태만 반환해야 위젯이 안 멈춤!
    return medal_data