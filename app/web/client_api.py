from aiohttp import web
from sqlalchemy import select
from app.db.models import User

async def client_api_router(request):
    try:
        data = await request.json()
        action = data.get("action")
        async_session = request.app['db_session']

        async with async_session() as session:
            # Получение списка доступных пекарен
            if action == "get_shops":
                # Берем только тех, кто seller и уже нажал старт (tg_id не None)
                stmt = select(User).where(User.role == 'seller', User.tg_id.isnot(None))
                result = await session.execute(stmt)
                shops = result.scalars().all()

                return web.json_response({
                    "status": "success",
                    "shops": [
                        {
                            "tg_id": s.tg_id,
                            "username": s.username,
                            "bakery_name": getattr(s, 'bakery_name', f"Пекарня @{s.username}")
                        } for s in shops
                    ]
                })

            return web.json_response({"status": "error", "message": "Action not supported"}, status=400)

    except Exception as e:
        print(f"🚨 CLIENT API ERROR: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)
