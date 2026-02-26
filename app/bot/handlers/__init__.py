# app/handlers/__init__.py
from .start import router as start_router
from .admin import router as admin_router
from .seller import router as seller_router
#from .worker import router as worker_router
from .client import router as client_router

routers = [
    admin_router,
    seller_router,
    #worker_router,
    client_router,
    start_router
]
