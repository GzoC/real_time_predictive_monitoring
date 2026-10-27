FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt pyproject.toml README.md LICENSE ./
COPY src ./src
COPY data/raw/ai4i2020.csv ./data/raw/ai4i2020.csv
COPY .streamlit ./.streamlit
RUN pip install --no-cache-dir --require-hashes -r requirements.txt \
    && pip install --no-cache-dir --no-deps . \
    && condition-monitor train --output /app/model \
    && useradd --create-home --uid 10001 monitor \
    && mkdir /data && chown monitor:monitor /data
ENV MODEL_DIR=/app/model TELEMETRY_DB=/data/telemetry.db
USER monitor
EXPOSE 8000 8501
CMD ["condition-monitor", "serve", "--host", "0.0.0.0"]
