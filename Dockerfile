FROM python:latest

# Set the working directory
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --on-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=production

EXPOSE 8000

CMD ["waitress-serve", "--host=0.0.0.0", "--port=8000", "app:app"]