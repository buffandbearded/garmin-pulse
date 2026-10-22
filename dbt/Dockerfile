FROM python:3.12-slim
RUN pip install --no-cache-dir dbt-postgres
WORKDIR /usr/app/dbt
ENV DBT_PROFILES_DIR=/usr/app/dbt
ENTRYPOINT ["dbt"]
