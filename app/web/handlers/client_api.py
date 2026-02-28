# app/web/handlers/client_api.py
from aiohttp import web

routes = web.RouteTableDef()

@routes.post('/api/client')
async def client_api_router(request):
    try:
        data = await request.json()
        action = data.get("action")
        
        # Минимальный ответ, чтобы фронтенд не падал
        return web.json_response({
            "status": "success", 
            "message": f"Client API received action: {action}",
            "data": []
        })

    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)
