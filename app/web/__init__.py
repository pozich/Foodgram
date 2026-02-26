from aiohttp import web
from .admin_api import admin_api_router as admin_handler
from .client_api import client_api_router as client_handler

def setup_web_handlers(app: web.Application):
    # API эндпоинты
    app.router.add_post('/api/admin', admin_handler)
    app.router.add_post('/api/client', client_handler)
    
    # Статика и страницы
    app.router.add_static('/static', path='app/web/static', name='static')
    app.router.add_static('/', path='app/web/pages', name='pages')
