FROM python:3.8

WORKDIR /work

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY Readme.md .
COPY data ./data

EXPOSE 8000
CMD [ "gunicorn", "main:server", "-b 0.0.0.0:8000"]