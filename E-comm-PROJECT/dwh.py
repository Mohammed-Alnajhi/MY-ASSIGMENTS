import pandas as pd
import sqlite3
from sqlalchemy import create_engine

def get_sqlite_connection():
    return sqlite3.connect("olist.sqlite")

def get_postgres_engine():
    return create_engine(
        "postgresql+psycopg2://postgres:Postgres%40123@localhost:5432/olist_dwh"
    )

def load_data(conn):
    tables = ["orders", "customers", "products", "sellers", "order_items"]
    data = {}
    for table in tables:
        data[table] = pd.read_sql(f"SELECT * FROM {table}", conn)
    return data

def build_dimensions(data):
    dim_customer = data["customers"].drop_duplicates()
    dim_product = data["products"].drop_duplicates()
    dim_seller = data["sellers"].drop_duplicates()

    dates = pd.to_datetime(data["orders"]["order_purchase_timestamp"]).dropna()

    dim_date = pd.DataFrame({
        "date_key": dates.dt.date,
        "day": dates.dt.day,
        "month": dates.dt.month,
        "year": dates.dt.year
    }).drop_duplicates()

    return {
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_seller": dim_seller,
        "dim_date": dim_date
    }

def build_fact(data, dims):
    fact = data["order_items"].merge(
        data["orders"],
        on="order_id",
        how="left"
    )

    fact["date_key"] = pd.to_datetime(
        fact["order_purchase_timestamp"]
    ).dt.date

    fact = fact[[
        "order_id",
        "product_id",
        "seller_id",
        "price",
        "order_item_id",
        "date_key"
    ]]

    fact = fact[
        fact["product_id"].isin(dims["dim_product"]["product_id"]) &
        fact["seller_id"].isin(dims["dim_seller"]["seller_id"]) &
        fact["date_key"].isin(dims["dim_date"]["date_key"])
    ]

    return fact

def load_to_postgres(engine, dims, fact):
    try:
        for name, df in dims.items():
            df.to_sql(name, engine, if_exists="replace", index=False, method="multi", chunksize=5000)

        fact.to_sql("fact_sales", engine, if_exists="replace", index=False, method="multi", chunksize=5000)

        print("done")

    except Exception as e:
        print(e)

def validate(engine):
    tables = ["dim_customer", "dim_product", "dim_seller", "dim_date", "fact_sales"]

    for t in tables:
        try:
            count = pd.read_sql(f"SELECT COUNT(*) FROM {t}", engine)
            print(t, count.iloc[0, 0])
        except:
            print(t, "error")

def run_pipeline():
    try:
        sqlite_conn = get_sqlite_connection()
        engine = get_postgres_engine()

        data = load_data(sqlite_conn)
        dims = build_dimensions(data)
        fact = build_fact(data, dims)

        load_to_postgres(engine, dims, fact)
        validate(engine)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    run_pipeline()