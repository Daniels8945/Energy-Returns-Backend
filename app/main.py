from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import init_db
from api.v1 import readings
from api.v1 import feeders as feeders_router
from api.v1 import monthly as monthly_router
from api.v1 import interface as interface_router

app = FastAPI(title="Onction Energy API")

app.include_router(readings.router)
app.include_router(feeders_router.router)
app.include_router(monthly_router.router)
app.include_router(interface_router.router)

@app.on_event('startup')
def on_startup():
    init_db()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)