"""
Analytics Module
Advanced analytics and business intelligence functions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class InventoryAnalytics:
    """Analytics functions for inventory optimization"""

    def __init__(self):
        pass

    def calculate_eoq(self, annual_demand: float, ordering_cost: float, holding_cost: float) -> float:
        """
        Economic Order Quantity (EOQ)
        EOQ = sqrt((2 × Annual Demand × Ordering Cost) / Holding Cost)
        """
        if holding_cost == 0:
            return 0
        eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
        return eoq

    def analyze_turnover_rate(self, usage: float, avg_inventory: float) -> Dict:
        """Calculate inventory turnover metrics"""
        if avg_inventory == 0:
            turnover_rate = 0
            days_on_hand = 0
        else:
            turnover_rate = usage / avg_inventory
            days_on_hand = 365 / turnover_rate if turnover_rate > 0 else 0

        return {
            'turnover_rate': turnover_rate,
            'days_on_hand': days_on_hand,
            'status': 'Fast-moving' if turnover_rate > 12 else 'Slow-moving'
        }

    def detect_stockout_risk(self,
                            current_stock: float,
                            daily_usage: float,
                            lead_time_days: int) -> Dict:
        """Assess risk of stockout"""
        if daily_usage == 0:
            return {'risk_level': 'Unknown', 'days_until_stockout': float('inf')}

        days_until_stockout = current_stock / daily_usage
        minimum_required = daily_usage * lead_time_days

        if current_stock <= minimum_required:
            risk_level = 'Critical'
        elif current_stock <= minimum_required * 1.5:
            risk_level = 'High'
        elif current_stock <= minimum_required * 2:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        return {
            'risk_level': risk_level,
            'days_until_stockout': days_until_stockout,
            'minimum_required': minimum_required,
            'recommended_reorder': current_stock < minimum_required * 1.5
        }

    def analyze_usage_trends(self, monthly_data: pd.DataFrame, ingredient: str) -> Dict:
        """Analyze usage trends for an ingredient over time"""
        if monthly_data.empty or ingredient not in monthly_data.columns:
            return {}

        usage_series = monthly_data[ingredient]

        trend_analysis = {
            'mean': usage_series.mean(),
            'median': usage_series.median(),
            'std': usage_series.std(),
            'min': usage_series.min(),
            'max': usage_series.max(),
            'trend': 'increasing' if usage_series.iloc[-1] > usage_series.iloc[0] else 'decreasing',
            'volatility': 'high' if usage_series.std() / usage_series.mean() > 0.3 else 'low'
        }

        return trend_analysis

    def calculate_cost_metrics(self,
                              quantity: float,
                              unit_cost: float,
                              waste_percentage: float = 0) -> Dict:
        """Calculate cost-related metrics"""

        total_cost = quantity * unit_cost
        waste_cost = total_cost * (waste_percentage / 100)
        effective_cost = total_cost - waste_cost

        return {
            'total_cost': total_cost,
            'waste_cost': waste_cost,
            'effective_cost': effective_cost,
            'cost_per_unit': unit_cost,
            'waste_percentage': waste_percentage
        }

    def identify_abc_classification(self, items_df: pd.DataFrame, value_column: str) -> pd.DataFrame:
        """
        ABC Analysis for inventory classification
        A items: Top 20% of items (80% of value)
        B items: Next 30% of items (15% of value)
        C items: Remaining 50% of items (5% of value)
        """
        if items_df.empty or value_column not in items_df.columns:
            return items_df

        df = items_df.copy()
        df = df.sort_values(value_column, ascending=False)
        df['cumulative_value'] = df[value_column].cumsum()
        total_value = df[value_column].sum()
        df['cumulative_percentage'] = (df['cumulative_value'] / total_value) * 100

        # Classify items
        df['abc_class'] = 'C'
        df.loc[df['cumulative_percentage'] <= 80, 'abc_class'] = 'A'
        df.loc[(df['cumulative_percentage'] > 80) & (df['cumulative_percentage'] <= 95), 'abc_class'] = 'B'

        return df

    def calculate_service_level(self,
                                orders_fulfilled: int,
                                total_orders: int) -> float:
        """Calculate service level percentage"""
        if total_orders == 0:
            return 0
        return (orders_fulfilled / total_orders) * 100

    def analyze_supplier_performance(self, shipment_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze supplier performance metrics"""
        if shipment_df.empty:
            return pd.DataFrame()

        # Group by ingredient (supplier)
        performance = shipment_df.groupby('ingredient').agg({
            'num_shipments': 'sum',
            'frequency': 'first'
        }).reset_index()

        # Calculate reliability score (simplified)
        performance['reliability_score'] = performance['num_shipments'] * 10  # Placeholder

        return performance

    def detect_anomalies(self, series: pd.Series, std_threshold: float = 2.5) -> pd.Series:
        """Detect anomalies using standard deviation method"""
        mean = series.mean()
        std = series.std()

        anomalies = (series > mean + std_threshold * std) | (series < mean - std_threshold * std)
        return anomalies

    def calculate_safety_stock(self,
                              max_daily_usage: float,
                              avg_daily_usage: float,
                              max_lead_time: int,
                              avg_lead_time: int) -> float:
        """
        Calculate safety stock using max-min method
        Safety Stock = (Max Daily Usage × Max Lead Time) - (Avg Daily Usage × Avg Lead Time)
        """
        safety_stock = (max_daily_usage * max_lead_time) - (avg_daily_usage * avg_lead_time)
        return max(0, safety_stock)

    def forecast_demand_simple(self,
                               historical_data: pd.Series,
                               periods: int = 30) -> pd.Series:
        """Simple moving average forecast"""
        if len(historical_data) < 3:
            # Not enough data, use average
            avg = historical_data.mean()
            return pd.Series([avg] * periods)

        # Use last 3 months for moving average
        window = min(3, len(historical_data))
        ma = historical_data.rolling(window=window).mean().iloc[-1]

        forecast = pd.Series([ma] * periods)
        return forecast

    def calculate_carrying_cost(self,
                               avg_inventory_value: float,
                               annual_rate: float = 0.25) -> float:
        """Calculate annual carrying cost (typically 25% of inventory value)"""
        return avg_inventory_value * annual_rate
