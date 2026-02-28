# app/web/__init__.py
from aiohttp import web
from .handlers import admin_api, seller_api, client_api

def setup_web_handlers(app: web.Application):
    app.add_routes(admin_api.routes)
    app.add_routes(seller_api.routes)
    app.add_routes(client_api.routes)
    
    app.router.add_static('/static', path='app/web/static', name='static')
    app.router.add_static('/', path='app/web/pages', name='pages', show_index=True)
