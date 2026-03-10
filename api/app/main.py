# api/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
import os
from app.database import engine, get_db
from app.models import Base, User, OwnerProfile, Tier, Bakery, Product, Order
import random
import string

load_dotenv()
ADMINS_ID = int(os.getenv("ADMINS_ID", 0))
app = FastAPI()

# Схема для получения данных от бота
class UserCreate(BaseModel):
    tg_id: int
    username: str | None = None
    role: str = "user"

class AddSellerRequest(BaseModel):
    username: str

class BakeryCreate(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float

class ProductCreate(BaseModel):
    title: str
    description: str | None = None
    old_price: int
    price: int
    quantity: int = 1
    bakery_id: int
    available_until: datetime

class OrderCreate(BaseModel):
    product_id: int
    quantity: int = 1

def generate_pickup_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.get("/owner/profile")
async def get_owner_full_profile(tg_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Проверяем, не ты ли это (супер-админ из .env)
    is_admin_from_env = (tg_id == ADMINS_ID)

    result = await db.execute(
        select(User)
        .where(User.tg_id == tg_id)
        .options(
            selectinload(User.owner_profile).selectinload(OwnerProfile.bakeries),
            selectinload(User.owner_profile).selectinload(OwnerProfile.tier)
        )
    )
    user = result.scalar_one_or_none()
    
    # Доступ разрешен если админ ИЛИ если роль owner
    is_owner = user and user.role == "owner"
    
    if not is_admin_from_env and not is_owner:
        raise HTTPException(status_code=403, detail="Доступ только для владельцев")

    # Если ты админ из env, но в базе у тебя еще нет пекарен, вернем пустой список
    return {
        "user": user,
        "is_superuser": is_admin_from_env,
        "is_owner": is_owner,
        "tier": user.owner_profile.tier if user and user.owner_profile else {"name": "Admin Mode", "commission": 0},
        "bakeries": user.owner_profile.bakeries if user and user.owner_profile else []
    }

# --- Bakery Endpoints ---

@app.post("/bakeries/")
async def create_bakery(bakery_data: BakeryCreate, tg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .where(User.tg_id == tg_id)
        .options(selectinload(User.owner_profile))
    )
    user = result.scalar_one_or_none()
    if not user or user.role != "owner":
        raise HTTPException(status_code=403, detail="Только владельцы могут создавать пекарни")
    
    new_bakery = Bakery(
        title=bakery_data.title,
        description=bakery_data.description,
        latitude=bakery_data.latitude,
        longitude=bakery_data.longitude,
        owner_id=user.owner_profile.id
    )
    db.add(new_bakery)
    await db.commit()
    await db.refresh(new_bakery)
    return new_bakery

@app.put("/bakeries/{bakery_id}")
async def update_bakery(bakery_id: int, bakery_data: BakeryCreate, tg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Bakery)
        .where(Bakery.id == bakery_id)
        .options(selectinload(Bakery.owner).selectinload(OwnerProfile.user))
    )
    bakery = result.scalar_one_or_none()
    
    if not bakery or bakery.owner.user.tg_id != tg_id:
        raise HTTPException(status_code=403, detail="Нет прав на редактирование этой пекарни")
    
    bakery.title = bakery_data.title
    bakery.description = bakery_data.description
    bakery.latitude = bakery_data.latitude
    bakery.longitude = bakery_data.longitude
    
    await db.commit()
    await db.refresh(bakery)
    return bakery

@app.get("/bakeries/")
async def list_bakeries(tg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User)
        .where(User.tg_id == tg_id)
        .options(selectinload(User.owner_profile).selectinload(OwnerProfile.bakeries))
    )
    user = result.scalar_one_or_none()
    if not user or user.role != "owner":
        return []
    return user.owner_profile.bakeries

# --- Product Endpoints ---

@app.post("/products/")
async def add_product(product_data: ProductCreate, tg_id: int, db: AsyncSession = Depends(get_db)):
    # Проверка прав (владелец ли этой пекарни?)
    result = await db.execute(
        select(Bakery)
        .where(Bakery.id == product_data.bakery_id)
        .options(selectinload(Bakery.owner).selectinload(OwnerProfile.user))
    )
    bakery = result.scalar_one_or_none()
    
    if not bakery or bakery.owner.user.tg_id != tg_id:
         raise HTTPException(status_code=403, detail="Нет прав на добавление товара в эту пекарню")

    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

@app.get("/products/feed")
async def get_product_feed(db: AsyncSession = Depends(get_db)):
    # Показываем только активные товары
    result = await db.execute(
        select(Product)
        .where(Product.is_active == True)
        .where(Product.available_until > datetime.now())
        .options(selectinload(Product.bakery))
    )
    return result.scalars().all()

# --- Order Endpoints ---

@app.post("/orders/")
async def create_order(order_data: OrderCreate, tg_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Проверяем продукт
    result = await db.execute(
        select(Product)
        .where(Product.id == order_data.product_id)
        .options(selectinload(Product.bakery).selectinload(Bakery.owner).selectinload(OwnerProfile.user))
    )
    product = result.scalar_one_or_none()
    
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Товар не найден или уже раскупили")
    
    if product.quantity < order_data.quantity:
        raise HTTPException(status_code=400, detail="Недостаточное количество товара")

    # 2. Проверяем пользователя
    user_result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = user_result.scalar_one_or_none()
    if not user:
         raise HTTPException(status_code=404, detail="Пользователь не зарегистрирован")

    # 3. Создаем заказ
    total_price = product.price * order_data.quantity
    new_order = Order(
        user_id=user.id,
        product_id=product.id,
        bakery_id=product.bakery_id,
        quantity=order_data.quantity,
        total_price=total_price,
        pickup_code=generate_pickup_code(),
        status="pending"
    )
    
    # 4. Уменьшаем количество товара
    product.quantity -= order_data.quantity
    if product.quantity <= 0:
        product.is_active = False

    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)
    
    # 5. Пытаемся уведомить владельца (через бота)
    owner_tg_id = product.bakery.owner.user.tg_id
    bot_token = os.getenv("BOT_TOKEN")
    if bot_token:
        import httpx
        msg = (
            f"🔔 Новый заказ!\n"
            f"Товар: {product.title}\n"
            f"Количество: {order_data.quantity}\n"
            f"Сумма: {total_price} ₽\n"
            f"Код выдачи: {new_order.pickup_code}"
        )
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={"chat_id": owner_tg_id, "text": msg}
                )
        except Exception as e:
            print(f"Ошибка уведомления: {e}")

    return new_order

@app.get("/orders/me")
async def get_my_orders(tg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order)
        .join(User, Order.user_id == User.id)
        .where(User.tg_id == tg_id)
        .options(selectinload(Order.product))
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()

@app.get("/orders/owner")
async def get_owner_orders(tg_id: int, db: AsyncSession = Depends(get_db)):
    # Заказы для всех моих пекарен
    result = await db.execute(
        select(Order)
        .join(Bakery, Order.bakery_id == Bakery.id)
        .join(OwnerProfile, Bakery.owner_id == OwnerProfile.id)
        .join(User, OwnerProfile.user_id == User.id)
        .where(User.tg_id == tg_id)
        .options(selectinload(Order.product), selectinload(Order.user))
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()

# --- Admin Endpoints ---

@app.post("/users/")
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли уже такой пользователь
    query = select(User).where(User.tg_id == user_data.tg_id)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return {"status": "ok", "message": "User already exists"}

    # Создаем нового пользователя
    new_user = User(
        tg_id=user_data.tg_id,
        username=user_data.username,
        role=user_data.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {"status": "created", "user_id": new_user.id}

@app.get("/")
def read_root():
    return {"message": "Foodgram API is running"}

@app.get("/admin/sellers")
async def get_all_sellers(tg_id: int, db: AsyncSession = Depends(get_db)):
    if tg_id != ADMINS_ID:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
        
    result = await db.execute(
        select(User)
        .where(User.role == 'owner')
        .options(
            selectinload(User.owner_profile).selectinload(OwnerProfile.bakeries),
            selectinload(User.owner_profile).selectinload(OwnerProfile.tier)
        )
    )
    sellers = result.scalars().all()
    
    return [
        {
            "user": seller,
            "bakeries": seller.owner_profile.bakeries if seller.owner_profile else [],
            "tier": seller.owner_profile.tier if seller.owner_profile else None
        }
        for seller in sellers
    ]

@app.post("/admin/sellers")
async def add_seller(data: AddSellerRequest, tg_id: int, db: AsyncSession = Depends(get_db)):
    if tg_id != ADMINS_ID:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    username = data.username.lstrip('@')
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден (он должен запустить бота)")
        
    if user.role == "owner":
        return {"status": "ok", "message": "Пользователь уже является продавцом"}
        
    user.role = "owner"
    
    profile_result = await db.execute(select(OwnerProfile).where(OwnerProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    
    if not profile:
        new_profile = OwnerProfile(user_id=user.id, tier_id=1)
        db.add(new_profile)
        
    await db.commit()
    return {"status": "ok", "message": "Продавец добавлен"}

@app.delete("/admin/sellers/{user_tg_id}")
async def remove_seller(user_tg_id: int, tg_id: int, db: AsyncSession = Depends(get_db)):
    if tg_id != ADMINS_ID:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
        
    result = await db.execute(select(User).where(User.tg_id == user_tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
        
    if user.role != "owner":
        return {"status": "ok", "message": "Пользователь не является продавцом"}
        
    user.role = "client"
    
    profile_result = await db.execute(select(OwnerProfile).where(OwnerProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    
    if profile:
        await db.delete(profile)
        
    await db.commit()
    return {"status": "ok", "message": "Продавец удален"}

# --- Staff Endpoints ---

@app.get("/owner/staff")
async def list_staff(tg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OwnerProfile)
        .join(User, OwnerProfile.user_id == User.id)
        .where(User.tg_id == tg_id)
        .options(selectinload(OwnerProfile.staff_list).selectinload(Staff.user))
    )
    profile = result.scalar_one_or_none()
    if not profile:
        return []
    return profile.staff_list

@app.post("/owner/staff/add")
async def add_staff(data: AddSellerRequest, owner_tg_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Находим владельца
    owner_result = await db.execute(
        select(OwnerProfile)
        .join(User, OwnerProfile.user_id == User.id)
        .where(User.tg_id == owner_tg_id)
    )
    owner = owner_result.scalar_one_or_none()
    if not owner:
        raise HTTPException(status_code=403, detail="Владелец не найден")

    # 2. Находим будущего работника
    username = data.username.lstrip('@')
    user_result = await db.execute(select(User).where(User.username == username))
    worker_user = user_result.scalar_one_or_none()
    
    if not worker_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден (должен запустить бота)")

    # 3. Добавляем в штат
    from app.models import Staff
    new_staff = Staff(user_id=worker_user.id, owner_id=owner.id)
    db.add(new_staff)
    await db.commit()
    
    return {"status": "ok", "message": "Сотрудник добавлен"}
