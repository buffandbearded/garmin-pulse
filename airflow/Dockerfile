FROM apache/airflow:2.10.5-python3.12
RUN pip install --no-cache-dir garminconnect psycopg2-binary python-dotenv
RUN python -m venv /home/airflow/dbt-venv \
 && /home/airflow/dbt-venv/bin/pip install --no-cache-dir dbt-postgres
