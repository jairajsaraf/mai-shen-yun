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

# Hide anchor links
st.markdown("""
    <style>
    .stHeadingContainer a {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

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

# Load all 3 sheets from monthly data
all_sheets = loader.load_all_sheets()
monthly_group = all_sheets['group']
monthly_category = all_sheets['category']
monthly_item = all_sheets['item']

# KPIs Section
st.header("🎯 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

# Calculate metrics from actual data
total_ingredients = len(shipment_df) if not shipment_df.empty else 0
total_dishes = len(ingredient_df) if not ingredient_df.empty else 0
months_tracked = len(loader.get_available_months())

# Calculate total sales from item data
total_sales = 0
total_revenue = 0
if not monthly_item.empty:
    if 'Count' in monthly_item.columns:
        total_sales = monthly_item['Count'].sum()
    if 'Amount' in monthly_item.columns:
        # Clean amount column (remove $ and commas)
        monthly_item['Amount_Clean'] = monthly_item['Amount'].astype(str).str.replace('$', '').str.replace(',', '').astype(float)
        total_revenue = monthly_item['Amount_Clean'].sum()

with col1:
    viz.create_kpi_card(
        "Total Orders",
        f"{total_sales:,}",
        delta=None
    )

with col2:
    viz.create_kpi_card(
        "Total Revenue",
        f"${total_revenue:,.2f}",
        delta=None
    )

with col3:
    viz.create_kpi_card(
        "Tracked Ingredients",
        f"{total_ingredients}",
        delta=None
    )

with col4:
    viz.create_kpi_card(
        "Months Tracked",
        f"{months_tracked}",
        delta=None
    )

st.markdown("---")

# Monthly Data Sheet Info
st.header("📊 Data Sheet Structure")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **Sheet 1: Group Level**
    - Records: {len(monthly_group)}
    - Aggregated sales by group
    """)
    if not monthly_group.empty and 'Group' in monthly_group.columns:
        unique_groups = monthly_group['Group'].unique()
        st.write("**Groups:**")
        for g in unique_groups:
            st.write(f"- {g}")

with col2:
    st.info(f"""
    **Sheet 2: Category Level**
    - Records: {len(monthly_category)}
    - Sales by food category
    """)
    if not monthly_category.empty and 'Category' in monthly_category.columns:
        unique_cats = monthly_category['Category'].unique()
        st.write(f"**{len(unique_cats)} categories tracked**")

with col3:
    st.info(f"""
    **Sheet 3: Item Level**
    - Records: {len(monthly_item)}
    - Individual dish sales
    """)
    if not monthly_item.empty and 'Item Name' in monthly_item.columns:
        unique_items = monthly_item['Item Name'].nunique()
        st.write(f"**{unique_items} unique items**")

st.markdown("---")

# Shipment Overview
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

st.markdown("---")

# Top Selling Dishes with Ranking
if not monthly_item.empty:
    st.header("🏆 Top Selling Dishes (Ranked)")

    # Aggregate sales across all months
    if 'Item Name' in monthly_item.columns and 'Count' in monthly_item.columns:
        # Group by item and sum counts and revenue
        dish_sales = monthly_item.groupby('Item Name').agg({
            'Count': 'sum',
            'Amount_Clean': 'sum' if 'Amount_Clean' in monthly_item.columns else 'count'
        }).sort_values('Count', ascending=False)

        st.subheader("📈 Sales Rankings")

        # Create ranking dataframe (Top 20)
        ranking_df = pd.DataFrame({
            'Rank': range(1, min(21, len(dish_sales) + 1)),
            'Dish Name': dish_sales.head(20).index,
            'Total Orders': dish_sales.head(20)['Count'].values,
            'Revenue': [f"${x:,.2f}" for x in dish_sales.head(20)['Amount_Clean'].values] if 'Amount_Clean' in dish_sales.columns else ['N/A'] * min(20, len(dish_sales))
        })

        col1, col2 = st.columns([3, 1])

        with col1:
            # Display as styled table with highlighting
            st.dataframe(
                ranking_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn("🏅 Rank", width="small"),
                    "Dish Name": st.column_config.TextColumn("Dish Name", width="large"),
                    "Total Orders": st.column_config.NumberColumn("📦 Orders", format="%d"),
                    "Revenue": st.column_config.TextColumn("💰 Revenue", width="medium")
                }
            )

        with col2:
            st.subheader("📊 Summary")
            st.metric("Total Dishes", len(dish_sales))
            st.metric("Total Orders", f"{dish_sales['Count'].sum():,}")

            if 'Amount_Clean' in dish_sales.columns:
                st.metric("Avg Revenue/Dish", f"${dish_sales['Amount_Clean'].mean():,.2f}")

            st.markdown("---")

            # Top 3 highlight
            st.write("**🥇 Top 3:**")
            for i, (dish, row) in enumerate(dish_sales.head(3).iterrows(), 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                st.write(f"{emoji} **{dish}**")
                st.write(f"   {row['Count']:,} orders")

        # Bottom 10 performers
        with st.expander("📉 View Bottom 10 Performers"):
            bottom_10 = dish_sales.tail(10).sort_values('Count', ascending=True)

            bottom_df = pd.DataFrame({
                'Dish Name': bottom_10.index,
                'Total Orders': bottom_10['Count'].values,
                'Revenue': [f"${x:,.2f}" for x in bottom_10['Amount_Clean'].values] if 'Amount_Clean' in bottom_10.columns else ['N/A'] * len(bottom_10)
            })

            st.dataframe(
                bottom_df,
                use_container_width=True,
                hide_index=True
            )

            st.info("💡 Consider promoting or reviewing these items to increase sales")

st.markdown("---")

# Category Performance
if not monthly_category.empty:
    st.header("🍜 Category Performance")

    if 'Category' in monthly_category.columns and 'Count' in monthly_category.columns:
        category_sales = monthly_category.groupby('Category')['Count'].sum().sort_values(ascending=False)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Create horizontal bar chart
            import plotly.graph_objects as go

            fig = go.Figure(data=[
                go.Bar(
                    y=category_sales.head(10).index,
                    x=category_sales.head(10).values,
                    orientation='h',
                    marker_color='#4ECDC4',
                    text=category_sales.head(10).values,
                    textposition='auto',
                )
            ])

            fig.update_layout(
                title="Top 10 Categories by Orders",
                xaxis_title="Total Orders",
                yaxis_title="Category",
                template="plotly_white",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Category Stats")
            st.metric("Total Categories", len(category_sales))
            st.metric("Top Category", category_sales.index[0])
            st.metric("Top Category Orders", f"{category_sales.values[0]:,}")

st.markdown("---")

# Alerts Section
st.header("🚨 System Alerts & Insights")

col1, col2 = st.columns(2)

with col1:
    st.info("✅ **Data Status**")
    st.write(f"- ✅ {total_ingredients} ingredients tracked")
    st.write(f"- ✅ {total_dishes} dishes in recipe database")
    st.write(f"- ✅ {months_tracked} months of sales data")
    st.write(f"- ✅ {total_sales:,} total orders processed")

with col2:
    st.warning("ℹ️ **Important Notes**")
    st.write("- 18 ingredients in recipes vs 14 in shipments")
    st.write("- Some ingredients may be combined in shipments")
    st.write("- Monthly data has 3 levels: Group, Category, Item")
    st.write("- Use Analytics page for deeper insights")

# Recommendations
st.header("💡 Executive Recommendations")

with st.expander("View Actionable Insights", expanded=True):
    st.markdown("""
    ### Immediate Actions
    1. **Focus on Top Performers**: The top 3 dishes generate significant revenue - ensure adequate ingredient inventory
    2. **Review Bottom Performers**: Consider menu optimization for low-selling items
    3. **Category Analysis**: Use category performance data to guide marketing efforts

    ### Strategic Initiatives
    1. **Demand Forecasting**: Leverage 6 months of historical data for better predictions
    2. **Inventory Optimization**: Align ingredient shipments with actual dish popularity
    3. **Cost Analysis**: Review ingredient costs for top-selling items to maximize margins

    ### Data Quality
    1. **Ingredient Mapping**: Reconcile 18-ingredient recipes with 14-shipment tracking
    2. **Regular Updates**: Maintain consistent data collection across all sheets
    3. **Integration**: Consider POS integration for real-time data
    """)

# Monthly trends snapshot
if not monthly_group.empty:
    st.header("📅 Monthly Performance Snapshot")

    if 'month' in monthly_group.columns and 'Amount_Clean' in monthly_group.columns:
        monthly_revenue = monthly_group.groupby('month')['Amount_Clean'].sum()

        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_revenue.index,
            y=monthly_revenue.values,
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=10)
        ))

        fig.update_layout(
            title="Monthly Revenue Trend",
            xaxis_title="Month",
            yaxis_title="Revenue ($)",
            template="plotly_white",
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.info("💡 **Tip:** Navigate to other pages using the sidebar to explore detailed analytics, predictions, and cost analysis.")
