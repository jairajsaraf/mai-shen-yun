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

st.title("📊 Executive Overview", anchor=False)
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
st.header("🎯 Key Performance Indicators", anchor=False)

col1, col2, col3, col4 = st.columns(4)

# Calculate metrics from actual data
total_ingredients = len(shipment_df) if not shipment_df.empty else 0
total_dishes = len(ingredient_df) if not ingredient_df.empty else 0
months_tracked = len(loader.get_available_months())

# Calculate total sales from item data
total_sales = 0
total_revenue = 0.0

if not monthly_item.empty:
    # Convert Count column to numeric (handle string values)
    if 'Count' in monthly_item.columns:
        monthly_item['Count'] = pd.to_numeric(monthly_item['Count'], errors='coerce').fillna(0)
        total_sales = int(monthly_item['Count'].sum())
    
    # Clean and convert Amount column
    if 'Amount' in monthly_item.columns:
        # Clean amount column (remove $ and commas)
        monthly_item['Amount_Clean'] = pd.to_numeric(
            monthly_item['Amount'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False),
            errors='coerce'
        ).fillna(0.0)
        total_revenue = float(monthly_item['Amount_Clean'].sum())

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
        str(total_ingredients),
        delta=None
    )

with col4:
    viz.create_kpi_card(
        "Months Tracked",
        str(months_tracked),
        delta=None
    )

st.markdown("---")

# Monthly Data Sheet Info
st.header("📊 Data Sheet Structure", anchor=False)

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
    st.header("📦 Shipment Overview", anchor=False)

    # Clean data
    shipment_clean = processor.clean_shipment_data(shipment_df)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Shipment frequency chart
        fig = viz.plot_shipment_frequency(shipment_clean)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Frequency Breakdown", anchor=False)
        if 'frequency' in shipment_clean.columns:
            freq_counts = shipment_clean['frequency'].value_counts()
            for freq, count in freq_counts.items():
                st.metric(freq.title(), f"{count} items")

st.markdown("---")

# Top Selling Dishes with Ranking
if not monthly_item.empty:
    st.header("🏆 Top Selling Dishes (Ranked)", anchor=False)

    # Aggregate sales across all months
    if 'Item Name' in monthly_item.columns and 'Count' in monthly_item.columns:
        # Ensure Count is numeric
        monthly_item['Count'] = pd.to_numeric(monthly_item['Count'], errors='coerce').fillna(0)
        
        # Group by item and sum counts and revenue
        agg_dict = {'Count': 'sum'}
        if 'Amount_Clean' in monthly_item.columns:
            agg_dict['Amount_Clean'] = 'sum'
        
        dish_sales = monthly_item.groupby('Item Name').agg(agg_dict).sort_values('Count', ascending=False)

        st.subheader("📈 Sales Rankings", anchor=False)

        # Create ranking dataframe (Top 20)
        top_20 = dish_sales.head(20)
        ranking_data = {
            'Rank': list(range(1, len(top_20) + 1)),
            'Dish Name': top_20.index.tolist(),
            'Total Orders': [int(x) for x in top_20['Count'].values],
        }
        
        if 'Amount_Clean' in top_20.columns:
            ranking_data['Revenue'] = [f"${float(x):,.2f}" for x in top_20['Amount_Clean'].values]
        
        ranking_df = pd.DataFrame(ranking_data)

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
                    "Revenue": st.column_config.TextColumn("💰 Revenue", width="medium") if 'Revenue' in ranking_data else None
                }
            )

        with col2:
            st.subheader("📊 Summary", anchor=False)
            st.metric("Total Dishes", len(dish_sales))
            st.metric("Total Orders", f"{int(dish_sales['Count'].sum()):,}")

            if 'Amount_Clean' in dish_sales.columns:
                avg_rev = float(dish_sales['Amount_Clean'].mean())
                st.metric("Avg Revenue/Dish", f"${avg_rev:,.2f}")

            st.markdown("---")

            # Top 3 highlight
            st.write("**🥇 Top 3:**")
            for i, (dish, row) in enumerate(dish_sales.head(3).iterrows(), 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                st.write(f"{emoji} **{dish}**")
                st.write(f"   {int(row['Count']):,} orders")

        # Bottom 10 performers
        with st.expander("📉 View Bottom 10 Performers"):
            bottom_10 = dish_sales.tail(10).sort_values('Count', ascending=True)

            bottom_data = {
                'Dish Name': bottom_10.index.tolist(),
                'Total Orders': [int(x) for x in bottom_10['Count'].values],
            }
            
            if 'Amount_Clean' in bottom_10.columns:
                bottom_data['Revenue'] = [f"${float(x):,.2f}" for x in bottom_10['Amount_Clean'].values]
            
            bottom_df = pd.DataFrame(bottom_data)

            st.dataframe(
                bottom_df,
                use_container_width=True,
                hide_index=True
            )

            st.info("💡 Consider promoting or reviewing these items to increase sales")

st.markdown("---")

# Category Performance
if not monthly_category.empty:
    st.header("🍜 Category Performance", anchor=False)

    if 'Category' in monthly_category.columns and 'Count' in monthly_category.columns:
        # Ensure Count is numeric
        monthly_category['Count'] = pd.to_numeric(monthly_category['Count'], errors='coerce').fillna(0)
        
        category_sales = monthly_category.groupby('Category')['Count'].sum().sort_values(ascending=False)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Create horizontal bar chart
            import plotly.graph_objects as go

            top_10_cats = category_sales.head(10)
            
            fig = go.Figure(data=[
                go.Bar(
                    y=top_10_cats.index.tolist(),
                    x=[float(x) for x in top_10_cats.values],
                    orientation='h',
                    marker_color='#4ECDC4',
                    text=[int(x) for x in top_10_cats.values],
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
            st.subheader("Category Stats", anchor=False)
            st.metric("Total Categories", len(category_sales))
            st.metric("Top Category", str(category_sales.index[0]))
            st.metric("Top Category Orders", f"{int(category_sales.values[0]):,}")

st.markdown("---")

# Alerts Section
st.header("🚨 System Alerts & Insights", anchor=False)

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
st.header("💡 Executive Recommendations", anchor=False)

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
    st.header("📅 Monthly Performance Snapshot", anchor=False)

    # Clean Amount column if it exists
    if 'Amount' in monthly_group.columns:
        if 'Amount_Clean' not in monthly_group.columns:
            monthly_group['Amount_Clean'] = pd.to_numeric(
                monthly_group['Amount'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False),
                errors='coerce'
            ).fillna(0.0)
    
    if 'month' in monthly_group.columns and 'Amount_Clean' in monthly_group.columns:
        monthly_revenue = monthly_group.groupby('month')['Amount_Clean'].sum()

        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_revenue.index.tolist(),
            y=[float(x) for x in monthly_revenue.values],
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
