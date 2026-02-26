# Foodgram
> Телеграм бот для организации сервиса фудшеринга в Казахстане.

![GitHub release (latest by date)](https://img.shields.io/github/v/release/pozich/Foodgram?style=flat-square)
![GitHub top language](https://img.shields.io/github/languages/top/pozich/Foodgram?color=yellow&style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/pozich/Foodgram?style=flat-square)
![License](https://img.shields.io/github/license/pozich/Foodgram?color=blue&style=flat-square)

---

## 🚀 Get started

### 1. Frontend
Для работы WebApp необходимо запустить проксирование (например, через Cloudflare):
```bash
cloudflared tunnel --url http://localhost:8000
```

### 2. Backend
```bash
git clone [https://github.com/pozich/Foodgram.git](https://github.com/pozich/Foodgram.git)
cd Foodgram

# Создайте и заполните .env файл
touch .env
```

### Содержимое .env:
```bash
TOKEN=123456789:ABCDEF
ADMINS=123456789
WEB_URL=https://your-tunnel.cloudflare.com
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

### Запуск
```bash
chmod +x run.sh
./run.sh
```

## 📂 Project Structure
```bash
.
├── app
│   ├── bot         # Логика бота (handlers, keyboards, filters)
│   ├── db          # Модели SQLAlchemy и работа с базой
│   └── web         # Backend для WebApp (API и статика)
├── bot.py          # Точка входа
├── config.py       # Загрузка конфигурации из .env
└── run.sh          # Скрипт автоматизации запуска
```

### 🛠 Stack
* Backend: Python 3.14 + Aiogram 3.x
* Database: PostgreSQL + SQLAlchemy 2.0 (Async)
* Web Server: Aiohttp
* Other: Pydantic v2, python-dotenv

