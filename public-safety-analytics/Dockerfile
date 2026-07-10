FROM apache/airflow:2.7.1-python3.10

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=airflow:airflow . /opt/airflow/

ENV PYTHONPATH="${PYTHONPATH}:/opt/airflow"

ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__WEBSERVER__DEFAULT_UI_TIMEZONE=UTC
ENV AIRFLOW__SCHEDULER__CATCHUP_BY_DEFAULT=True

USER airflow