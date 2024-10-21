FROM tiangolo/uvicorn-gunicorn:python3.9


RUN apt-get update && apt-get install -y portaudio19-dev

RUN mkdir /fastapi

COPY requirements.txt /fastapi

WORKDIR /fastapi

RUN pip install -r requirements.txt

COPY . /fastapi

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8091"]