# Weekly ABCD image: fetch this-week (no WARP) → mart → Fact Pack → outlook.
# Historical HTML scrape is not the default path; that still needs WARP egress.
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Ho_Chi_Minh \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        tzdata \
    && ln -snf /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime \
    && echo Asia/Ho_Chi_Minh > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts ./scripts
COPY docs ./docs
COPY tests ./tests
COPY data ./data
COPY reports ./reports
COPY docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh \
    && useradd --create-home --uid 1000 app \
    && chown -R app:app /app

USER app
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "scripts/run_weekly_abcd.py", "--fmt", "csv"]
