FROM python:3.10

WORKDIR /app

COPY ["../Pipfile", "."]

RUN pip install pipenv

RUN pipenv install --deploy

COPY . .

EXPOSE 9000

CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]