FROM python:3.9.18-slim-bullseye

COPY src/ /app/src/
COPY ./requirements.txt /app/requirements.txt
COPY ./model_dir /app/model_dir
COPY ./data_weaviate /app/data_weaviate
RUN pip install -r /app/requirements.txt
WORKDIR /app/

EXPOSE 9002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9002" ,"--workers", "4" ,"--root-path","/zania-agent"]