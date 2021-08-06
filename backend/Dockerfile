FROM python:3.8.5
WORKDIR /web
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD gunicorn -b 0.0.0.0:8000 --chdir /web/foodgram/ foodgram.wsgi