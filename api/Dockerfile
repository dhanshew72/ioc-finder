FROM --platform=linux/amd64 tiangolo/uvicorn-gunicorn-fastapi:python3.10

RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y --no-install-recommends nginx \
 && rm -rf /var/lib/apt/lists/*

ENV PROJECT_DIR=api
ENV AWS_DEFAULT_REGION=us-east-1

WORKDIR /$PROJECT_DIR

COPY requirements.txt ./

# install python dependencies, and aws cli
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY start.sh src ./
COPY gunicorn_conf.py ./

EXPOSE 80

RUN chmod +x start.sh
ENTRYPOINT ["./start.sh"]
