cat > deploy.sh << 'EOF'
#!/bin/bash

# Активация виртуального окружения
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Установка зависимостей
pip install -r requirements.txt

# Создание базы данных
python -c "
from database import db
import asyncio
asyncio.run(db.create_tables())
print('База данных создана')
"

# Запуск бота
python bot.py
EOF
