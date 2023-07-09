FROM python:3.10
WORKDIR /code
EXPOSE 80

COPY ./ /code

# print step
RUN echo "installing requirements"

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN echo "done"
RUN echo "starting streamlit"

CMD ["streamlit", "run", "/code/app.py", "--server.port", "80"]