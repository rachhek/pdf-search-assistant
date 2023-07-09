FROM python:3.10
WORKDIR /code
EXPOSE 80

COPY ./ /code

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["streamlit", "run", "/code/app.py", "--server.port", "80"]