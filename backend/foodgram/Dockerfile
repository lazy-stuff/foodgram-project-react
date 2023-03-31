FROM python:3.7

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "backend.foodgram.foodgram.wsgi:application", "--bind", "0:8000" ]