# app/web/handlers/admin_api.py
from aiohttp import web
from app.db.requests.users import set_user_role, get_all_sellers

routes = web.RouteTableDef()

@routes.post('/api/admin')
async def admin_api_router(request):
    try:
        data = await request.json()
        action = data.get("action")
        async_session = request.app['db_session']

        async with async_session() as session:
            if action == "get_sellers":
                sellers = await get_all_sellers(session)
                
                return web.json_response({
                    "status": "success", 
                    "sellers": [{
                        "tg_id": s.tg_id,
                        "username": s.username or "Unknown", 
                        "bakery_name": getattr(s, 'bakery_name', '-')
                    } for s in sellers]
                })

            elif action in ["add", "remove"]:
                target = data.get("target")
                if not target:
                    return web.json_response({"status": "error", "message": "Введите ID или @Username"}, status=400)
                
                success = await set_user_role(session, target, "seller" if action == "add" else "client")
                await session.commit()
                return web.json_response({"status": "success" if success else "error"})

            return web.json_response({"status": "error", "message": "Неизвестное действие"}, status=400)

    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)
