import logging
from datetime import timedelta

import joblib
import numpy as np
import pandas as pd

from sqlalchemy import create_engine

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from config import DATABASE_URL


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


# =====================================================
# DATABASE
# =====================================================

engine = create_engine(DATABASE_URL)


# =====================================================
# MODEL CLASS
# =====================================================

class CropPricePredictor:

    def __init__(self):

        self.engine = engine

        self.linear_model = LinearRegression()

        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )

        self.best_model = None
        self.best_model_name = ""
        self.metrics = {}

    # =================================================

    def load_data(self):

        logger.info("Loading crop analytics data...")

        df = pd.read_sql(
            "SELECT * FROM crop_analytics ORDER BY date",
            self.engine
        )

        df["date"] = pd.to_datetime(df["date"])

        logger.info(f"Rows Loaded : {len(df)}")

        return df

    # =================================================

    def feature_engineering(self, df):

        logger.info("Creating ML features...")

        df = df.sort_values(
            ["crop", "date"]
        )

        df["day_number"] = (
            df["date"] - df["date"].min()
        ).dt.days

        df["month"] = df["date"].dt.month
        df["week"] = df["date"].dt.isocalendar().week.astype(int)
        df["day"] = df["date"].dt.day
        df["year"] = df["date"].dt.year
        df["day_of_week"] = df["date"].dt.dayofweek

        df["price_lag_1"] = (
            df.groupby("crop")["price"]
            .shift(1)
        )

        df["price_lag_2"] = (
            df.groupby("crop")["price"]
            .shift(2)
        )

        df["price_lag_3"] = (
            df.groupby("crop")["price"]
            .shift(3)
        )

        df["rolling_mean"] = (
            df.groupby("crop")["price"]
            .transform(
                lambda x: x.rolling(
                    7,
                    min_periods=1
                ).mean()
            )
        )

        df["rolling_std"] = (
            df.groupby("crop")["price"]
            .transform(
                lambda x: x.rolling(
                    7,
                    min_periods=1
                ).std()
            )
        )

        df = df.bfill()

        logger.info(f"Rows After Feature Engineering : {len(df)}")

        return df

    # =================================================

    def prepare_dataset(self, df):

        logger.info("Preparing Dataset...")

        features = [

            "day_number",

            "month",

            "week",

            "day",

            "year",

            "day_of_week",

            "price_lag_1",

            "price_lag_2",

            "price_lag_3",

            "rolling_mean",

            "rolling_std"

        ]

        X = df[features]

        y = df["price"]

        logger.info(f"Training Samples : {len(X)}")

        return train_test_split(

            X,

            y,

            test_size=0.20,

            random_state=42

        )

    # =================================================

    def train_linear_model(

        self,

        X_train,

        X_test,

        y_train,

        y_test

    ):

        logger.info("Training Linear Regression...")

        self.linear_model.fit(
            X_train,
            y_train
        )

        predictions = self.linear_model.predict(
            X_test
        )

        self.metrics["Linear Regression"] = {

            "MAE": mean_absolute_error(
                y_test,
                predictions
            ),

            "RMSE": np.sqrt(
                mean_squared_error(
                    y_test,
                    predictions
                )
            ),

            "R2": r2_score(
                y_test,
                predictions
            )

        }

        logger.info("Linear Regression Completed.")

    # =================================================

    def train_random_forest(

        self,

        X_train,

        X_test,

        y_train,

        y_test

    ):

        logger.info("Training Random Forest...")

        self.rf_model.fit(
            X_train,
            y_train
        )

        predictions = self.rf_model.predict(
            X_test
        )

        self.metrics["Random Forest"] = {

            "MAE": mean_absolute_error(
                y_test,
                predictions
            ),

            "RMSE": np.sqrt(
                mean_squared_error(
                    y_test,
                    predictions
                )
            ),

            "R2": r2_score(
                y_test,
                predictions
            )

        }

        logger.info("Random Forest Completed.")
            # =================================================

    def select_best_model(self):

        linear_r2 = self.metrics["Linear Regression"]["R2"]
        rf_r2 = self.metrics["Random Forest"]["R2"]

        if rf_r2 >= linear_r2:

            self.best_model = self.rf_model
            self.best_model_name = "Random Forest"

        else:

            self.best_model = self.linear_model
            self.best_model_name = "Linear Regression"

        logger.info(f"Best Model : {self.best_model_name}")

    # =================================================

    def save_model(self):

        joblib.dump(
            self.best_model,
            "models/best_model.pkl"
        )

        logger.info("Model saved successfully.")

    # =================================================

    def generate_predictions(self, df):

        logger.info("Generating 7-Day Forecast...")

        latest = (
            df.sort_values("date")
              .groupby("crop")
              .tail(1)
        )

        predictions = []

        for _, row in latest.iterrows():

            rolling_std = row["rolling_std"]

            if pd.isna(rolling_std):
                rolling_std = 0

            for i in range(1, 8):

                future_date = row["date"] + timedelta(days=i)

                features = pd.DataFrame({

                    "day_number": [row["day_number"] + i],

                    "month": [future_date.month],

                    "week": [int(future_date.isocalendar()[1])],

                    "day": [future_date.day],

                    "year": [future_date.year],

                    "day_of_week": [future_date.weekday()],

                    "price_lag_1": [row["price"]],

                    "price_lag_2": [row["price"]],

                    "price_lag_3": [row["price"]],

                    "rolling_mean": [row["rolling_mean"]],

                    "rolling_std": [rolling_std]

                })

                predicted_price = float(
                    self.best_model.predict(features)[0]
                )

                predictions.append({

                    "crop": row["crop"],

                    "prediction_date": future_date,

                    "predicted_price": round(predicted_price, 2)

                })

        prediction_df = pd.DataFrame(predictions)

        logger.info(f"Predictions Generated : {len(prediction_df)}")

        return prediction_df

    # =================================================

    def save_predictions(self, prediction_df):

        logger.info("Saving predictions to SQLite...")

        prediction_df.to_sql(

            "crop_predictions",

            self.engine,

            if_exists="replace",

            index=False

        )

        logger.info("Predictions saved successfully.")

    # =================================================

    def print_metrics(self):

        print("\n")
        print("=" * 60)
        print("MODEL PERFORMANCE")
        print("=" * 60)

        for model, values in self.metrics.items():

            print(f"\n{model}")
            print("-" * 30)
            print(f"MAE  : {values['MAE']:.2f}")
            print(f"RMSE : {values['RMSE']:.2f}")
            print(f"R²   : {values['R2']:.3f}")

        print("=" * 60)


# =====================================================
# MAIN
# =====================================================

def main():

    predictor = CropPricePredictor()

    df = predictor.load_data()

    df = predictor.feature_engineering(df)

    X_train, X_test, y_train, y_test = predictor.prepare_dataset(df)

    predictor.train_linear_model(
        X_train,
        X_test,
        y_train,
        y_test
    )

    predictor.train_random_forest(
        X_train,
        X_test,
        y_train,
        y_test
    )

    predictor.select_best_model()

    predictor.save_model()

    prediction_df = predictor.generate_predictions(df)

    predictor.save_predictions(prediction_df)

    predictor.print_metrics()

    print("\n")
    print("=" * 60)
    print("Forecast Generated Successfully")
    print(f"Best Model : {predictor.best_model_name}")
    print("Predictions stored in SQLite.")
    print("=" * 60)


if __name__ == "__main__":
    main()