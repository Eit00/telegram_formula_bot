from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func


from db import engine, get_db
from models import Base, Card, DropRate, User, UserCard, CardCategory, CATEGORY_DISPLAY
from services import ensure_default_drop_rates
from config import ADMIN_SECRET


Base.metadata.create_all(bind=engine)


app = FastAPI(title="Raffle Admin & API")
app.mount("/static", StaticFiles(directory="templates"), name="static")
templates = Jinja2Templates(directory="templates")


# ------------------- Admin Pages -------------------


@app.get("/admin", response_class=HTMLResponse)
async def admin_home(request: Request, secret: str = ""):
if secret != ADMIN_SECRET:
raise HTTPException(status_code=403, detail="Forbidden")
return templates.TemplateResponse("admin_home.html", {"request": request})


@app.get("/admin/cards", response_class=HTMLResponse)
async def admin_cards(request: Request, db: Session = Depends(get_db), secret: str = ""):
if secret