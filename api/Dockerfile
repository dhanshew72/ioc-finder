FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10-alpine3.8

RUN apk update \
 && apk upgrade \
 && apk add --no-cache nginx

ENV PROJECT_DIR=api

WORKDIR /$PROJECT_DIR

COPY requirements.txt ./

# install python dependencies, and aws cli
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY start.sh src ./

EXPOSE 80

RUN chmod +x start.sh
ENTRYPOINT ["./start.sh"]
