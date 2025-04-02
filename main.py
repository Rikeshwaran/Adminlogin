from fastapi import FastAPI, Form, HTTPException, Depends, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import sqlite3
import os


app = FastAPI()




DATABASE_NAME = "dynamic_form.db"



def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row 
    return conn
def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS form_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL
        )
        """)
        conn.commit()
init_db()



templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.post("/admin")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "password":
        return templates.TemplateResponse("admin.html", {"request": request, "username": username})
    else:
        return templates.TemplateResponse("oops.html", {"request": request})



@app.post("/logout")
async def logout():
    return RedirectResponse(url="/", status_code=303)



@app.post("/submit")
async def submit_data(data: Dict[str, Any]):
    with get_db() as conn:
        conn.execute("INSERT INTO form_entries (data) VALUES (?)", (str(data),))
        conn.commit()
    return {"message": "Data submitted successfully"}



@app.get("/get-data")
async def get_data():
    with get_db() as conn:
        cursor = conn.execute("SELECT id, data FROM form_entries")
        stored_data = [{"_id": str(row["id"]), **eval(row["data"])} for row in cursor.fetchall()]
    return stored_data



@app.put("/update/{item_id}")
async def update_data(item_id: str, updated_data: Dict[str, Any]):
    with get_db() as conn:
        conn.execute("UPDATE form_entries SET data = ? WHERE id = ?", (str(updated_data), item_id))
        conn.commit()
    return {"message": "Data updated successfully"}



@app.delete("/delete/{item_id}")
async def delete_data(item_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM form_entries WHERE id = ?", (item_id,))
        conn.commit()
    return {"message": "Data deleted successfully"}