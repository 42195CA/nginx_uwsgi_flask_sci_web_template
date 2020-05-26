FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app /app

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt
