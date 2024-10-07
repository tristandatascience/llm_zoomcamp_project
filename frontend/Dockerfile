FROM python:3.10

WORKDIR /app

COPY ["../Pipfile",  "."]

RUN pip install pipenv

RUN pipenv install --deploy
COPY . .

EXPOSE 8501

CMD ["pipenv", "run", "streamlit", "run", "streamlit_app.py"]