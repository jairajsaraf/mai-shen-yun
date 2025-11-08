"""
Overview Page - Executive Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_loader import DataLoader
from data_processor import DataProcessor
from analytics import InventoryAnalytics
from visualizations import InventoryVisualizations

# Page config
st.set_page_config(page_title="Overview - Mai Shen Yun", page_icon="📊", layout="wide")

st.title("📊 Executive Overview")
st.markdown("---")

# Initialize classes
loader = DataLoader()
processor = DataProcessor()
analytics = InventoryAnalytics()
viz = InventoryVisualizations()

# Load data
ingredient_df = loader.load_ingredient_data()
shipment_df = loader.load_shipment_data()
monthly_df = loader.load_monthly_data()

# KPIs Section
st.header("🎯 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

# Calculate metrics
total_ingredients = len(shipment_df) if not shipment_df.empty else 0
total_dishes = len(ingredient_df) if not ingredient_df.empty else 0
months_tracked = len(loader.get_available_months())

with col1:
    viz.create_kpi_card(
        "Total Ingredients",
        f"{total_ingredients}",
        delta=None
    )

with col2:
    viz.create_kpi_card(
        "Menu Items",
        f"{total_dishes}",
        delta=None
    )

with col3:
    viz.create_kpi_card(
        "Months Tracked",
        f"{months_tracked}",
        delta=None
    )

with col4:
    # Calculate total shipments
    total_shipments = shipment_df['num_shipments'].sum() if not shipment_df.empty and 'num_shipments' in shipment_df.columns else 0
    viz.create_kpi_card(
        "Total Shipments",
        f"{total_shipments}",
        delta=None
    )

st.markdown("---")

# Alerts Section
st.header("🚨 Critical Alerts")

col1, col2 = st.columns(2)

with col1:
    st.warning("⚠️ **Inventory Alerts**")
    st.write("- Recommend implementing real-time stock tracking")
    st.write("- Set up automated reorder points")
    st.write("- Monitor high-frequency items closely")

with col2:
    st.success("✅ **System Status**")
    st.write(f"- {total_ingredients} ingredients monitored")
    st.write(f"- {total_dishes} dishes in menu")
    st.write(f"- Data from {months_tracked} months loaded")

# Shipment Frequency Analysis
if not shipment_df.empty:
    st.header("📦 Shipment Overview")

    # Clean data
    shipment_clean = processor.clean_shipment_data(shipment_df)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Shipment frequency chart
        fig = viz.plot_shipment_frequency(shipment_clean)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Frequency Breakdown")
        if 'frequency' in shipment_clean.columns:
            freq_counts = shipment_clean['frequency'].value_counts()
            for freq, count in freq_counts.items():
                st.metric(freq.title(), f"{count} items")

# Top Ingredients
if not ingredient_df.empty:
    st.header("🔝 Menu Analysis")

    # Clean data
    ingredient_clean = processor.clean_ingredient_data(ingredient_df)

    # Count ingredients used in each dish
    if 'dish_name' in ingredient_clean.columns:
        st.subheader("Popular Dishes")

        # Display top dishes
        dish_sample = ingredient_clean['dish_name'].head(10)

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Sample Menu Items:**")
            for dish in dish_sample[:5]:
                st.write(f"- {dish}")

        with col2:
            st.write("**More Items:**")
            for dish in dish_sample[5:10]:
                st.write(f"- {dish}")

# Monthly Data Overview
if not monthly_df.empty:
    st.header("📅 Monthly Data Summary")

    months = loader.get_available_months()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"**Earliest Month:** {months[0] if months else 'N/A'}")

    with col2:
        st.info(f"**Latest Month:** {months[-1] if months else 'N/A'}")

    with col3:
        st.info(f"**Total Records:** {len(monthly_df)}")

# Recommendations
st.header("💡 Recommendations")

with st.expander("View Actionable Insights", expanded=True):
    st.markdown("""
    ### Immediate Actions
    1. **Set up reorder points** for all ingredients based on usage patterns
    2. **Implement safety stock** for high-frequency ingredients (weekly shipments)
    3. **Review** items with monthly shipments for potential cost savings

    ### Strategic Initiatives
    1. **Demand Forecasting**: Use historical data to predict future needs
    2. **ABC Analysis**: Classify ingredients by value and prioritize management
    3. **Supplier Optimization**: Negotiate better terms for high-volume items

    ### Cost Optimization
    1. Identify slow-moving ingredients to reduce carrying costs
    2. Consolidate shipments where possible
    3. Implement just-in-time ordering for non-perishables
    """)

# Data Quality Check
st.header("✅ Data Quality")

col1, col2, col3 = st.columns(3)

with col1:
    status = "✅ Good" if not ingredient_df.empty else "❌ Missing"
    st.metric("Ingredient Data", status)

with col2:
    status = "✅ Good" if not shipment_df.empty else "❌ Missing"
    st.metric("Shipment Data", status)

with col3:
    status = "✅ Good" if not monthly_df.empty else "⚠️ Limited"
    st.metric("Monthly Data", status)

# Footer
st.markdown("---")
st.info("💡 **Tip:** Navigate to other pages using the sidebar to explore detailed analytics, predictions, and cost analysis.")
