import pandas as pd


def calculate_kpis(df):
    """
    Calculate dashboard KPI values.
    """

    if df.empty:
        return {
            "highest": 0,
            "lowest": 0,
            "average": 0,
            "volatility": 0,
            "growth": 0
        }

    highest = float(df["price"].max())
    lowest = float(df["price"].min())
    average = float(df["price"].mean())
    volatility = float(df["price"].std())

    first_price = float(df.iloc[0]["price"])
    last_price = float(df.iloc[-1]["price"])

    if first_price == 0:
        growth = 0
    else:
        growth = ((last_price - first_price) / first_price) * 100

    return {
        "highest": round(highest, 2),
        "lowest": round(lowest, 2),
        "average": round(average, 2),
        "volatility": round(volatility, 2),
        "growth": round(growth, 2)
    }


def recommendation(current_price, moving_average):
    """
    Generate farmer recommendation.
    """

    if current_price > moving_average * 1.05:
        return (
            "SELL NOW",
            "🟢",
            "Current market price is significantly above the moving average."
        )

    elif current_price < moving_average * 0.95:
        return (
            "HOLD STOCK",
            "🔴",
            "Current market price is below the moving average."
        )

    else:
        return (
            "WATCH MARKET",
            "🟡",
            "Market price is stable. Monitor before making a decision."
        )


def format_currency(value):
    """
    Format price.
    """
    return f"₹ {value:,.2f}"


def format_percentage(value):
    """
    Format percentage.
    """
    return f"{value:.2f}%"

def latest_record(df):
    """
    Return latest record safely.
    """
    if df.empty:
        return None

    return df.sort_values("date").iloc[-1]


def market_summary(df):
    """
    Average price by market.
    """

    return (
        df.groupby("market")["price"]
        .mean()
        .reset_index()
        .sort_values("price", ascending=False)
    )


def crop_summary(df):
    """
    Average price by crop.
    """

    return (
        df.groupby("crop")["price"]
        .mean()
        .reset_index()
        .sort_values("price", ascending=False)
    )