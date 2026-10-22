-- Separate database for Airflow metadata (used in the orchestration step)
CREATE DATABASE airflow;

-- Warehouse layers (run against POSTGRES_DB)
CREATE SCHEMA IF NOT EXISTS raw;      -- ingested JSON, untouched
CREATE SCHEMA IF NOT EXISTS staging;  -- dbt: cleaned/typed
CREATE SCHEMA IF NOT EXISTS marts;    -- dbt: analytics-ready
