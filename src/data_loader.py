"""
Data Loader Module
Handles loading and validation of all data sources
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Tuple
import streamlit as st

class DataLoader:
    """Load and validate data from various sources"""

    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.cache = {}

    @st.cache_data(ttl=3600)
    def load_ingredient_data(_self) -> pd.DataFrame:
        """Load ingredient master list"""
        file_path = _self.data_dir / "MSY Data - Ingredient.csv"
        try:
            df = pd.read_csv(file_path)
            # Clean column names
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Error loading ingredient data: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=3600)
    def load_shipment_data(_self) -> pd.DataFrame:
        """Load shipment information"""
        file_path = _self.data_dir / "MSY Data - Shipment.csv"
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Error loading shipment data: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=3600)
    def load_monthly_data(_self, month: str = None) -> pd.DataFrame:
        """
        Load monthly sales/usage data from Excel files
        If month is None, loads all months and combines them
        """
        try:
            # Find all Excel files
            excel_files = list(_self.data_dir.glob("*.xlsx"))

            if month:
                # Load specific month
                matching_files = [f for f in excel_files if month.lower() in f.name.lower()]
                if matching_files:
                    df = pd.read_excel(matching_files[0])
                    df['month'] = month
                    return df
                else:
                    st.warning(f"No data found for {month}")
                    return pd.DataFrame()
            else:
                # Load all months
                all_data = []
                month_names = ['May', 'June', 'July', 'August', 'September', 'October']

                for excel_file in excel_files:
                    # Extract month from filename
                    file_month = None
                    for m in month_names:
                        if m.lower() in excel_file.name.lower():
                            file_month = m
                            break

                    if file_month:
                        df = pd.read_excel(excel_file)
                        df['month'] = file_month
                        all_data.append(df)

                if all_data:
                    combined_df = pd.concat(all_data, ignore_index=True)
                    return combined_df
                else:
                    return pd.DataFrame()

        except Exception as e:
            st.error(f"Error loading monthly data: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=3600)
    def get_available_months(_self) -> List[str]:
        """Get list of available months from Excel files"""
        try:
            excel_files = list(_self.data_dir.glob("*.xlsx"))
            months = []
            month_names = ['May', 'June', 'July', 'August', 'September', 'October']

            for excel_file in excel_files:
                for month in month_names:
                    if month.lower() in excel_file.name.lower():
                        months.append(month)
                        break

            return sorted(months, key=lambda x: month_names.index(x))
        except Exception as e:
            st.error(f"Error getting available months: {e}")
            return []

    def validate_data(self, df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, str]:
        """Validate that dataframe has required columns"""
        if df.empty:
            return False, "DataFrame is empty"

        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            return False, f"Missing columns: {missing_cols}"

        return True, "Data validation passed"

    def get_data_summary(self) -> Dict:
        """Get summary of all available data"""
        summary = {
            'ingredients_available': not self.load_ingredient_data().empty,
            'shipments_available': not self.load_shipment_data().empty,
            'available_months': self.get_available_months(),
            'total_months': len(self.get_available_months())
        }
        return summary
