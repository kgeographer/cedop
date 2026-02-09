# from fastapi import APIRouter, Request
# from fastapi.templating import Jinja2Templates
#
# router = APIRouter()
# templates = Jinja2Templates(directory="app/templates")
#
#
# @router.get("/")
# def index(request: Request):
#     return templates.TemplateResponse(
#         "index.html",
#         {"request": request}
#     )

from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
print("TEMPLATES_DIR =", TEMPLATES_DIR)

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/edop")
def edop(request: Request):
    return templates.TemplateResponse("edop.html", {"request": request})