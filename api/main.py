from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

app = FastAPI()

# Conexão MongoDB
MONGO_URL = "mongodb+srv://bww963w_db_user:ACOnUaYEDdqKiKLQ@processos.zxlumwz.mongodb.net/?retryWrites=true&w=majority&appName=processos"
client = MongoClient(MONGO_URL)
db = client["pwa_db"]
processos_collection = db["processos"]


USUARIO = "admin"
SENHA = "123"


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# -------------------- ROTAS --------------------

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "erro": None})

@app.post("/login")
async def login(request: Request, usuario: str = Form(...), senha: str = Form(...)):
    if usuario == USUARIO and senha == SENHA:
        return RedirectResponse(url="/cadastro", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "erro": "Usuário ou senha inválidos"})

@app.get("/cadastro", response_class=HTMLResponse)
async def cadastro(request: Request):
    return templates.TemplateResponse("cadastro_processo.html", {"request": request})

@app.post("/cadastro")
async def cadastro_process(numero: str = Form(...), descricao: str = Form(...)):
    processo = {
        "numero": numero,
        "ultima_atualizacao": datetime.now(),
        "detalhes": [{"descricao": descricao, "data": datetime.now()}]
    }
    processos_collection.insert_one(processo)
    return RedirectResponse(url="/processos", status_code=303)

@app.get("/processos", response_class=HTMLResponse)
async def listar_processos(request: Request):
    processos = list(processos_collection.find())
    for p in processos:
        p["_id"] = str(p["_id"])
    return templates.TemplateResponse("processos_processo.html", {"request": request, "processos": processos})

@app.get("/processo/{processo_id}", response_class=HTMLResponse)
async def detalhes_processo(request: Request, processo_id: str):
    processo = processos_collection.find_one({"_id": ObjectId(processo_id)})
    if processo:
        processo["_id"] = str(processo["_id"])
        processo["detalhes"] = sorted(processo["detalhes"], key=lambda d: d["data"], reverse=True)
    return templates.TemplateResponse("detalhes_processo.html", {"request": request, "processo": processo})

@app.post("/processo/{processo_id}/add")
async def add_detalhe(processo_id: str, descricao: str = Form(...)):
    processos_collection.update_one(
        {"_id": ObjectId(processo_id)},
        {"$push": {"detalhes": {"descricao": descricao, "data": datetime.now()}},
         "$set": {"ultima_atualizacao": datetime.now()}}
    )
    return RedirectResponse(url=f"/processo/{processo_id}", status_code=303)

@app.get("/logout")
async def logout():
    return RedirectResponse(url="/")
