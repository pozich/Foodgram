# app/web/handlers/worker_api.py
from aiohttp import web

routes = web.RouteTableDef()

@routes.post('/api/worker')
async def worker_api_router(request):
    try:
        data = await request.json()
        action = data.get("action")
        
        return web.json_response({
            "status": "success", 
            "message": f"Worker API received action: {action}",
            "data": []
        })

    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)
