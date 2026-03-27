FROM python:3.11-slim

WORKDIR /app

# 避免 bytecode 寫入容器層造成不必要變更
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Cloud Run 會注入 PORT 變數；使用 gunicorn 以符合 production 標準
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 0 app:app

