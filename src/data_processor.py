"""
Data Processor Module
Cleans, transforms, and merges datasets
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Tuple

class DataProcessor:
    """Process and transform data for analysis"""

    def __init__(self):
        self.processed_cache = {}

    def clean_ingredient_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize ingredient data"""
        if df.empty:
            return df

        # Make a copy
        df = df.copy()

        # Clean column names
        df.columns = df.columns.str.strip()

        # Handle the first column which is "Item name"
        if 'Item name' in df.columns:
            df = df.rename(columns={'Item name': 'dish_name'})

        # Replace NaN with 0 for ingredient quantities
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)

        return df

    def clean_shipment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize shipment data"""
        if df.empty:
            return df

        df = df.copy()
        df.columns = df.columns.str.strip()

        # Standardize column names
        column_mapping = {
            'Ingredient': 'ingredient',
            'Quantity per shipment': 'quantity_per_shipment',
            'Unit of shipment': 'unit',
            'Number of shipments': 'num_shipments',
            'frequency': 'frequency'
        }

        df = df.rename(columns=column_mapping)

        # Standardize frequency values
        if 'frequency' in df.columns:
            df['frequency'] = df['frequency'].str.lower().str.strip()

        return df

    def process_monthly_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process monthly data matrix
        Assumes first column is dish name, rest are ingredient quantities
        """
        if df.empty:
            return df

        df = df.copy()

        # Set first column as index (dish names)
        if len(df.columns) > 0:
            df = df.set_index(df.columns[0])

        # Replace NaN with 0
        df = df.fillna(0)

        # Reset index to make dish_name a column
        df = df.reset_index()
        df = df.rename(columns={df.columns[0]: 'dish_name'})

        return df

    def calculate_ingredient_usage(self,
                                   recipe_df: pd.DataFrame,
                                   sales_count: Dict[str, int]) -> pd.DataFrame:
        """
        Calculate total ingredient usage based on sales

        Args:
            recipe_df: DataFrame with dish recipes (ingredient quantities per dish)
            sales_count: Dictionary mapping dish names to number of sales

        Returns:
            DataFrame with ingredient usage totals
        """
        if recipe_df.empty:
            return pd.DataFrame()

        # Initialize ingredient totals
        ingredient_totals = {}

        # Get all ingredient columns (exclude dish_name and month)
        ingredient_cols = [col for col in recipe_df.columns
                          if col not in ['dish_name', 'month']]

        for _, row in recipe_df.iterrows():
            dish = row['dish_name']
            sales = sales_count.get(dish, 0)

            for ingredient in ingredient_cols:
                quantity_per_dish = row[ingredient]
                if pd.notna(quantity_per_dish) and quantity_per_dish > 0:
                    if ingredient not in ingredient_totals:
                        ingredient_totals[ingredient] = 0
                    ingredient_totals[ingredient] += quantity_per_dish * sales

        # Convert to DataFrame
        result = pd.DataFrame([
            {'ingredient': k, 'total_usage': v}
            for k, v in ingredient_totals.items()
        ])

        return result.sort_values('total_usage', ascending=False)

    def calculate_reorder_point(self,
                               avg_daily_usage: float,
                               lead_time_days: int,
                               safety_stock: float = None) -> float:
        """
        Calculate reorder point for inventory management

        Reorder Point = (Lead Time × Average Daily Usage) + Safety Stock
        """
        if safety_stock is None:
            # Default safety stock to 1 week of usage
            safety_stock = avg_daily_usage * 7

        reorder_point = (lead_time_days * avg_daily_usage) + safety_stock
        return reorder_point

    def frequency_to_days(self, frequency: str) -> int:
        """Convert frequency string to days"""
        frequency = frequency.lower().strip()

        freq_mapping = {
            'daily': 1,
            'weekly': 7,
            'biweekly': 14,
            'bi-weekly': 14,
            'monthly': 30,
            'quarterly': 90
        }

        return freq_mapping.get(frequency, 30)  # Default to monthly

    def calculate_inventory_metrics(self,
                                    current_stock: float,
                                    avg_daily_usage: float,
                                    reorder_point: float) -> Dict:
        """Calculate various inventory metrics"""

        days_of_stock = current_stock / avg_daily_usage if avg_daily_usage > 0 else 0

        status = 'Normal'
        if current_stock < reorder_point:
            status = 'Low - Reorder Now'
        elif current_stock > avg_daily_usage * 60:  # More than 2 months
            status = 'Overstock'

        metrics = {
            'days_of_stock': days_of_stock,
            'status': status,
            'utilization_rate': (avg_daily_usage * 30 / current_stock * 100) if current_stock > 0 else 0
        }

        return metrics

    def merge_datasets(self,
                      ingredient_df: pd.DataFrame,
                      shipment_df: pd.DataFrame,
                      usage_df: pd.DataFrame) -> pd.DataFrame:
        """Merge all datasets for comprehensive analysis"""

        # Start with ingredient data
        merged = ingredient_df.copy()

        # Merge with shipment data
        if not shipment_df.empty:
            # Normalize ingredient names for matching
            shipment_df = shipment_df.copy()
            shipment_df['ingredient_normalized'] = shipment_df['ingredient'].str.lower().str.strip()
            merged['ingredient_normalized'] = merged['dish_name'].str.lower().str.strip()

            merged = merged.merge(
                shipment_df,
                on='ingredient_normalized',
                how='left'
            )

        # Merge with usage data
        if not usage_df.empty:
            usage_df = usage_df.copy()
            usage_df['ingredient_normalized'] = usage_df['ingredient'].str.lower().str.strip()

            merged = merged.merge(
                usage_df,
                on='ingredient_normalized',
                how='left'
            )

        return merged

    def get_top_ingredients(self, df: pd.DataFrame, n: int = 10, by: str = 'usage') -> pd.DataFrame:
        """Get top N ingredients by specified metric"""
        if df.empty or by not in df.columns:
            return pd.DataFrame()

        return df.nlargest(n, by)

    def detect_seasonal_patterns(self, monthly_data: pd.DataFrame) -> pd.DataFrame:
        """Detect seasonal patterns in ingredient usage"""
        if monthly_data.empty or 'month' not in monthly_data.columns:
            return pd.DataFrame()

        # Group by month and calculate metrics
        monthly_summary = monthly_data.groupby('month').agg({
            col: 'sum' for col in monthly_data.columns
            if col not in ['dish_name', 'month']
        })

        return monthly_summary
