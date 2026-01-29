FROM python:3.8-slim
RUN pip install flask PyMySQL cryptography
COPY ./app.py /app.py
CMD ["python", "/app.py"]