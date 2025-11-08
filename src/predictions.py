"""
Predictions Module
Time series forecasting and predictive analytics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class InventoryPredictor:
    """Predictive models for inventory forecasting"""

    def __init__(self):
        self.models = {}

    def moving_average_forecast(self,
                                data: pd.Series,
                                window: int = 3,
                                periods: int = 30) -> pd.Series:
        """
        Simple Moving Average forecast
        """
        if len(data) < window:
            # Not enough data, return mean
            mean_value = data.mean()
            return pd.Series([mean_value] * periods)

        ma = data.rolling(window=window).mean().iloc[-1]
        forecast = pd.Series([ma] * periods)
        return forecast

    def weighted_moving_average(self,
                                data: pd.Series,
                                weights: List[float] = None,
                                periods: int = 30) -> pd.Series:
        """
        Weighted Moving Average - gives more weight to recent data
        """
        if weights is None:
            # Default: more weight to recent periods
            weights = [0.5, 0.3, 0.2]

        if len(data) < len(weights):
            return self.moving_average_forecast(data, window=len(data), periods=periods)

        recent_data = data.iloc[-len(weights):]
        wma = sum(recent_data.iloc[i] * weights[i] for i in range(len(weights)))

        forecast = pd.Series([wma] * periods)
        return forecast

    def exponential_smoothing(self,
                             data: pd.Series,
                             alpha: float = 0.3,
                             periods: int = 30) -> pd.Series:
        """
        Exponential Smoothing forecast
        alpha: smoothing parameter (0-1), higher = more weight to recent data
        """
        if len(data) < 2:
            return pd.Series([data.mean()] * periods)

        # Calculate smoothed values
        smoothed = [data.iloc[0]]
        for i in range(1, len(data)):
            smoothed.append(alpha * data.iloc[i] + (1 - alpha) * smoothed[-1])

        # Use last smoothed value as forecast
        last_value = smoothed[-1]
        forecast = pd.Series([last_value] * periods)

        return forecast

    def linear_regression_forecast(self,
                                   data: pd.Series,
                                   periods: int = 30) -> pd.Series:
        """Simple linear regression forecast"""
        if len(data) < 3:
            return pd.Series([data.mean()] * periods)

        try:
            from sklearn.linear_model import LinearRegression

            # Prepare data
            X = np.arange(len(data)).reshape(-1, 1)
            y = data.values

            # Fit model
            model = LinearRegression()
            model.fit(X, y)

            # Predict future
            future_X = np.arange(len(data), len(data) + periods).reshape(-1, 1)
            forecast = model.predict(future_X)

            # Ensure no negative forecasts
            forecast = np.maximum(forecast, 0)

            return pd.Series(forecast)

        except ImportError:
            # Fallback to simple method
            return self.moving_average_forecast(data, periods=periods)

    def seasonal_decompose_forecast(self,
                                   data: pd.Series,
                                   periods: int = 30,
                                   seasonal_period: int = 7) -> pd.Series:
        """
        Forecast with seasonal decomposition
        """
        if len(data) < seasonal_period * 2:
            return self.exponential_smoothing(data, periods=periods)

        try:
            from statsmodels.tsa.seasonal import seasonal_decompose

            # Decompose
            decomposition = seasonal_decompose(data, model='additive', period=seasonal_period)

            # Use trend and seasonal components for forecast
            trend_forecast = decomposition.trend.iloc[-1]
            seasonal_pattern = decomposition.seasonal.iloc[-seasonal_period:]

            # Repeat seasonal pattern for forecast periods
            forecast_values = []
            for i in range(periods):
                seasonal_idx = i % len(seasonal_pattern)
                forecast_value = trend_forecast + seasonal_pattern.iloc[seasonal_idx]
                forecast_values.append(max(0, forecast_value))

            return pd.Series(forecast_values)

        except:
            return self.exponential_smoothing(data, periods=periods)

    def prophet_forecast(self,
                        data: pd.DataFrame,
                        periods: int = 30) -> pd.DataFrame:
        """
        Facebook Prophet forecast (if available)
        Expects DataFrame with 'ds' (date) and 'y' (value) columns
        """
        try:
            from prophet import Prophet

            # Initialize model
            model = Prophet(
                yearly_seasonality=False,
                weekly_seasonality=True,
                daily_seasonality=False,
                seasonality_mode='multiplicative'
            )

            # Fit model
            model.fit(data)

            # Create future dataframe
            future = model.make_future_dataframe(periods=periods)

            # Predict
            forecast = model.predict(future)

            return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

        except ImportError:
            # Prophet not available, return empty
            return pd.DataFrame()

    def ensemble_forecast(self,
                         data: pd.Series,
                         periods: int = 30) -> Dict[str, pd.Series]:
        """
        Ensemble forecast combining multiple methods
        """
        forecasts = {}

        # Generate forecasts using different methods
        forecasts['moving_average'] = self.moving_average_forecast(data, periods=periods)
        forecasts['exponential_smoothing'] = self.exponential_smoothing(data, periods=periods)
        forecasts['weighted_ma'] = self.weighted_moving_average(data, periods=periods)

        # Try linear regression
        try:
            forecasts['linear_regression'] = self.linear_regression_forecast(data, periods=periods)
        except:
            pass

        # Calculate ensemble (average of all methods)
        all_forecasts = np.array([f.values for f in forecasts.values()])
        ensemble = np.mean(all_forecasts, axis=0)
        forecasts['ensemble'] = pd.Series(ensemble)

        return forecasts

    def calculate_forecast_accuracy(self,
                                   actual: pd.Series,
                                   forecast: pd.Series) -> Dict[str, float]:
        """Calculate forecast accuracy metrics"""

        # Align series
        min_len = min(len(actual), len(forecast))
        actual = actual.iloc[:min_len]
        forecast = forecast.iloc[:min_len]

        # Mean Absolute Error
        mae = np.mean(np.abs(actual - forecast))

        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((actual - forecast) / actual)) * 100 if actual.mean() > 0 else 0

        # Root Mean Squared Error
        rmse = np.sqrt(np.mean((actual - forecast) ** 2))

        return {
            'mae': mae,
            'mape': mape,
            'rmse': rmse
        }

    def predict_reorder_date(self,
                            current_stock: float,
                            daily_usage: float,
                            reorder_point: float) -> Tuple[int, str]:
        """
        Predict when to reorder based on current stock and usage
        Returns: (days_until_reorder, date_string)
        """
        if daily_usage == 0:
            return float('inf'), "Unknown"

        days_until_reorder = max(0, (current_stock - reorder_point) / daily_usage)

        from datetime import datetime, timedelta
        reorder_date = datetime.now() + timedelta(days=int(days_until_reorder))
        date_string = reorder_date.strftime('%Y-%m-%d')

        return int(days_until_reorder), date_string

    def optimize_order_quantity(self,
                               forecast_demand: float,
                               current_stock: float,
                               min_order: float = 0,
                               max_storage: float = float('inf')) -> float:
        """
        Calculate optimal order quantity considering constraints
        """
        # Base order = forecast demand - current stock
        base_order = max(0, forecast_demand - current_stock)

        # Apply constraints
        order_quantity = max(min_order, base_order)
        order_quantity = min(max_storage, order_quantity)

        return order_quantity
