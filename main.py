from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from routes.api import router as api_router

app = FastAPI(title="AI Network Domain Agent", version="0.4.0")
app.include_router(api_router)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def web_interface(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )