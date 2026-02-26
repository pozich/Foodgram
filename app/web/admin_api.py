# app/web/admin_api.py
from aiohttp import web
from sqlalchemy import select
import logging
from app.db.requests import set_user_role
from app.db.models import User

async def admin_api_router(request):
    try:
        data = await request.json()
        action = data.get("action")
        # Проверяем, что scope == 'admin', чтобы обычные юзеры не лазили сюда
        scope = data.get("scope") 
        
        async_session = request.app['db_session']

        async with async_session() as session:
            # 1. ЗАГРУЗКА СПИСКА
            if action == "get_sellers":
                # Ищем всех, у кого роль seller
                stmt = select(User).where(User.role == 'seller')
                result = await session.execute(stmt)
                sellers = result.scalars().all()
                
                sellers_list = []
                for s in sellers:
                    sellers_list.append({
                        "tg_id": s.tg_id,
                        "username": s.username or "Unknown", # Защита от None
                        "bakery_name": getattr(s, 'bakery_name', '-') # Если поля еще нет в модели
                    })
                return web.json_response({"status": "success", "sellers": sellers_list})

            # 2. УПРАВЛЕНИЕ (Добавить/Убрать)
            elif action in ["add", "remove"]:
                target = data.get("target")
                if not target:
                    return web.json_response({"status": "error", "message": "Не указан ID/Username"}, status=400)
                
                role = "seller" if action == "add" else "client"
                
                # Передаем сессию в функцию. 
                # ВАЖНО: убедись, что в set_user_role стоит await session.commit()
                success = await set_user_role(session, target, role)
                
                return web.json_response({"status": "success" if success else "error"})

            # Если action не распознан
            return web.json_response({"status": "error", "message": f"Действие {action} не поддерживается"}, status=400)

    except Exception as e:
        # Печатаем полную ошибку в консоль сервера
        import traceback
        print(f"🚨 WEB API ERROR: {e}")
        traceback.print_exc() 
        return web.json_response({"status": "error", "message": str(e)}, status=500)
