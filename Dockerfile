FROM python:3.9

# Создание директории для приложения
RUN mkdir /file_blink

# Установка рабочей директории
WORKDIR /file_blink

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов проекта
COPY . .

# Добавление прав на выполнение скриптов
RUN chmod +x Docker/*.sh

# Применение миграций будет в app.sh, а не здесь
# CMD уже прописан в app.sh

# Запуск через app.sh
CMD ["/file_blink/Docker/app.sh"]
