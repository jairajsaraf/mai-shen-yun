"""
Visualizations Module
Chart and graph components using Plotly and Altair
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List

class InventoryVisualizations:
    """Create interactive visualizations for inventory dashboard"""

    def __init__(self):
        self.color_palette = {
            'primary': '#FF6B6B',
            'secondary': '#4ECDC4',
            'success': '#95E1D3',
            'warning': '#FFE66D',
            'danger': '#FF6B6B',
            'info': '#6C5CE7'
        }

    def create_kpi_card(self, title: str, value: str, delta: str = None, delta_color: str = "normal"):
        """Create a KPI metric card"""
        st.metric(label=title, value=value, delta=delta, delta_color=delta_color)

    def plot_inventory_levels(self, df: pd.DataFrame, title: str = "Current Inventory Levels") -> go.Figure:
        """Bar chart showing current inventory levels with status colors"""

        if df.empty:
            return go.Figure()

        # Ensure required columns exist
        if 'ingredient' not in df.columns or 'current_stock' not in df.columns:
            return go.Figure()

        # Color code by status
        colors = []
        for status in df.get('status', ['Normal'] * len(df)):
            if 'Low' in str(status) or 'Critical' in str(status):
                colors.append(self.color_palette['danger'])
            elif 'Overstock' in str(status):
                colors.append(self.color_palette['warning'])
            else:
                colors.append(self.color_palette['success'])

        fig = go.Figure(data=[
            go.Bar(
                x=df['ingredient'],
                y=df['current_stock'],
                marker_color=colors,
                text=df['current_stock'],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title=title,
            xaxis_title="Ingredient",
            yaxis_title="Current Stock",
            template="plotly_white",
            height=500
        )

        return fig

    def plot_usage_trends(self, df: pd.DataFrame, ingredient: str = None) -> go.Figure:
        """Line chart showing usage trends over time"""

        if df.empty:
            return go.Figure()

        fig = go.Figure()

        if ingredient and ingredient in df.columns:
            # Plot single ingredient
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[ingredient],
                mode='lines+markers',
                name=ingredient,
                line=dict(color=self.color_palette['primary'], width=3)
            ))
        else:
            # Plot multiple ingredients
            for col in df.columns:
                if col not in ['month', 'dish_name']:
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df[col],
                        mode='lines+markers',
                        name=col
                    ))

        fig.update_layout(
            title=f"Usage Trends - {ingredient if ingredient else 'All Ingredients'}",
            xaxis_title="Period",
            yaxis_title="Usage",
            template="plotly_white",
            height=500,
            hovermode='x unified'
        )

        return fig

    def plot_top_ingredients(self, df: pd.DataFrame, n: int = 10, metric: str = 'usage') -> go.Figure:
        """Horizontal bar chart of top N ingredients"""

        if df.empty or len(df) == 0:
            return go.Figure()

        # Get top N
        top_df = df.head(n)

        fig = go.Figure(data=[
            go.Bar(
                y=top_df['ingredient'],
                x=top_df[metric],
                orientation='h',
                marker_color=self.color_palette['primary'],
                text=top_df[metric],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title=f"Top {n} Ingredients by {metric.title()}",
            xaxis_title=metric.title(),
            yaxis_title="Ingredient",
            template="plotly_white",
            height=500
        )

        return fig

    def plot_forecast(self,
                     historical: pd.Series,
                     forecast: pd.Series,
                     title: str = "Demand Forecast") -> go.Figure:
        """Plot historical data with forecast"""

        fig = go.Figure()

        # Historical data
        fig.add_trace(go.Scatter(
            x=list(range(len(historical))),
            y=historical,
            mode='lines+markers',
            name='Historical',
            line=dict(color=self.color_palette['primary'], width=2)
        ))

        # Forecast
        forecast_x = list(range(len(historical), len(historical) + len(forecast)))
        fig.add_trace(go.Scatter(
            x=forecast_x,
            y=forecast,
            mode='lines+markers',
            name='Forecast',
            line=dict(color=self.color_palette['secondary'], width=2, dash='dash')
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Period",
            yaxis_title="Quantity",
            template="plotly_white",
            height=500,
            hovermode='x unified'
        )

        return fig

    def plot_cost_breakdown(self, df: pd.DataFrame) -> go.Figure:
        """Pie chart showing cost breakdown by category"""

        if df.empty:
            return go.Figure()

        fig = go.Figure(data=[
            go.Pie(
                labels=df['category'],
                values=df['cost'],
                hole=0.4,
                marker_colors=[self.color_palette['primary'],
                              self.color_palette['secondary'],
                              self.color_palette['success'],
                              self.color_palette['warning']]
            )
        ])

        fig.update_layout(
            title="Cost Breakdown by Category",
            template="plotly_white",
            height=500
        )

        return fig

    def plot_shipment_frequency(self, df: pd.DataFrame) -> go.Figure:
        """Bar chart showing shipment frequency analysis"""

        if df.empty:
            return go.Figure()

        fig = go.Figure(data=[
            go.Bar(
                x=df['ingredient'],
                y=df['num_shipments'],
                marker_color=self.color_palette['info'],
                text=df['frequency'],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title="Shipment Frequency Analysis",
            xaxis_title="Ingredient",
            yaxis_title="Number of Shipments",
            template="plotly_white",
            height=500
        )

        return fig

    def plot_abc_analysis(self, df: pd.DataFrame) -> go.Figure:
        """ABC Analysis visualization"""

        if df.empty or 'abc_class' not in df.columns:
            return go.Figure()

        # Count items in each class
        abc_counts = df['abc_class'].value_counts()

        fig = go.Figure(data=[
            go.Bar(
                x=abc_counts.index,
                y=abc_counts.values,
                marker_color=[self.color_palette['danger'],
                             self.color_palette['warning'],
                             self.color_palette['success']],
                text=abc_counts.values,
                textposition='auto',
            )
        ])

        fig.update_layout(
            title="ABC Classification of Inventory",
            xaxis_title="Class",
            yaxis_title="Number of Items",
            template="plotly_white",
            height=400
        )

        return fig

    def plot_heatmap(self, df: pd.DataFrame, title: str = "Ingredient Usage Heatmap") -> go.Figure:
        """Heatmap showing ingredient usage across different dishes/time periods"""

        if df.empty:
            return go.Figure()

        fig = go.Figure(data=go.Heatmap(
            z=df.values,
            x=df.columns,
            y=df.index,
            colorscale='RdYlGn',
            hoverongaps=False
        ))

        fig.update_layout(
            title=title,
            template="plotly_white",
            height=600
        )

        return fig

    def plot_gauge(self, value: float, max_value: float, title: str = "Stock Level") -> go.Figure:
        """Gauge chart for stock level indicators"""

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': self.color_palette['primary']},
                'steps': [
                    {'range': [0, max_value * 0.3], 'color': self.color_palette['danger']},
                    {'range': [max_value * 0.3, max_value * 0.7], 'color': self.color_palette['warning']},
                    {'range': [max_value * 0.7, max_value], 'color': self.color_palette['success']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))

        fig.update_layout(height=400)

        return fig

    def plot_correlation_matrix(self, df: pd.DataFrame) -> go.Figure:
        """Correlation matrix heatmap"""

        if df.empty:
            return go.Figure()

        # Calculate correlation
        corr = df.corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale='RdBu',
            zmid=0
        ))

        fig.update_layout(
            title="Correlation Matrix",
            template="plotly_white",
            height=600
        )

        return fig

    def create_summary_table(self, df: pd.DataFrame, columns: List[str] = None):
        """Display formatted table with Streamlit"""
        if df.empty:
            st.warning("No data available")
            return

        if columns:
            df = df[columns]

        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
