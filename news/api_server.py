from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
