import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from bson.objectid import ObjectId

# Caminho absoluto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# MongoDB Atlas
MONGO_URL = "mongodb+srv://bww963w_db_user:<db_password>@processos.zxlumwz.mongodb.net/?retryWrites=true&w=majority&appName=processos"
client = MongoClient(MONGO_URL)
db = client["pwa_db"]
processos_col = db["processos"]

# Usuário fixo
USUARIO_FIXO = {"usuario":"admin", "senha":"123"}

# ----- LOGIN -----
@app.get("/")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "hide_menu": True})

@app.post("/login")
def login_post(request: Request, usuario: str = Form(...), senha: str = Form(...)):
    if usuario == USUARIO_FIXO["usuario"] and senha == USUARIO_FIXO["senha"]:
        response = RedirectResponse("/cadastro", status_code=303)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "erro": "Usuário ou senha incorretos", "hide_menu": True})

# ----- CADASTRO PROCESSO -----
@app.get("/cadastro")
def cadastro_get(request: Request):
    return templates.TemplateResponse("cadastro_processo.html", {"request": request})

@app.post("/cadastro")
def cadastro_post(request: Request, numero: str = Form(...), descricao: str = Form(...)):
    processo = {"numero": numero, "descricao": descricao}
    processos_col.insert_one(processo)
    return RedirectResponse("/processos", status_code=303)

# ----- LISTA PROCESSOS -----
@app.get("/processos")
def processos_get(request: Request):
    processos = list(processos_col.find({}))
    return templates.TemplateResponse("processos_processo.html", {"request": request, "processos": processos})

# ----- DETALHES PROCESSO -----
@app.get("/detalhes/{processo_id}")
def detalhes_get(request: Request, processo_id: str):
    processo = processos_col.find_one({"_id": ObjectId(processo_id)})
    return templates.TemplateResponse("detalhes_processo.html", {"request": request, "processo": processo})
