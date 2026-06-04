FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y --no-install-recommends nginx \
 && rm -rf /var/lib/apt/lists/*

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
