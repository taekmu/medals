from bs4 import BeautifulSoup

@app.get("/medals")
async def get_medals():
    medal_file = os.path.join(static_path, "medal.html")
    medal_data = []

    if os.path.exists(medal_file):
        try:
            with open(medal_file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # 모든 행(tr)을 다 뒤져서 데이터를 찾습니다.
            rows = soup.find_all("tr")
            for row in rows:
                # 클래스가 없어도 순서대로 가져오도록 보완
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

    # 데이터가 아예 없으면 테스트용 가짜 데이터라도 보냅니다 (연결 중 해결 확인용)
    if not medal_data:
        return [{"country": "데이터 없음", "gold": "0", "silver": "0", "bronze": "0"}]
    
    return medal_data