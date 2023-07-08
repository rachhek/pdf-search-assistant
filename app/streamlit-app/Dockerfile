FROM python:3.10
WORKDIR /code
EXPOSE 80

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app.py /code/app.py

CMD ["streamlit", "run", "/code/app.py", "--server.port", "80"]