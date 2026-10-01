from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import init_db
from .routes import router
app=FastAPI(title=settings.app_name,debug=settings.debug)
app.mount('/static',StaticFiles(directory='static'),name='static')
app.state.templates=Jinja2Templates(directory='templates')
app.include_router(router)
@app.on_event('startup')
def startup(): init_db()
@app.exception_handler(Exception)
async def error(request:Request,exc:Exception): return app.state.templates.TemplateResponse('error.html',{'request':request,'error':str(exc)},status_code=500)
