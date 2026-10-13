FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

# Versi kode yang sedang berjalan. Diisi otomatis oleh scripts/uji-pr dan scripts/balik-main,
# lalu ditampilkan lewat /versi di Telegram.
ARG GIT_COMMIT=dev
ARG GIT_BRANCH=lokal
ENV GIT_COMMIT=$GIT_COMMIT \
    GIT_BRANCH=$GIT_BRANCH

CMD ["python", "-m", "app.main"]
