import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from config import DATABASE_URL

# ---------------------------------------
# Database Connection
# ---------------------------------------

engine = create_engine(DATABASE_URL)

print("Reading Dataset...")

df = pd.read_csv("data/crop_prices.csv")

print("Cleaning Data...")

df.columns = df.columns.str.strip()

df["Date"] = pd.to_datetime(df["Date"])

df["Market"] = df["Market"].fillna("Unknown Market")

df["Crop"] = df["Crop"].fillna("Unknown Crop")

df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

df["Price"] = (
    df.groupby("Crop")["Price"]
    .transform(lambda x: x.fillna(x.median()))
)

df = df.sort_values(["Crop", "Date"])

df["MovingAverage7"] = (
    df.groupby("Crop")["Price"]
    .transform(lambda x: x.rolling(7, min_periods=1).mean())
    .round(2)
)

df["Volatility"] = (
    df.groupby("Crop")["Price"]
    .transform(lambda x: x.rolling(7, min_periods=1).std())
)

df["Volatility"] = df["Volatility"].fillna(0)

# Rename columns for PostgreSQL
df.columns = [
    "date",
    "market",
    "crop",
    "price",
    "moving_average",
    "volatility"
]

print(df.head())

print("Rows:", len(df))

# ---------------------------------------
# Upload to PostgreSQL
# ---------------------------------------

df.to_sql(
    "crop_analytics",
    engine,
    if_exists="replace",
    index=False
)

print("✅ Data uploaded successfully!")