FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r hf_backend/requirements.txt

RUN pip install --no-cache-dir -e .

EXPOSE 7860

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "hf_backend.app:app"]
