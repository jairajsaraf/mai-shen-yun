"""
Inventory Management Page
Real-time inventory tracking and management
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
st.set_page_config(page_title="Inventory - Mai Shen Yun", page_icon="📦", layout="wide")

# Hide anchor links
st.markdown("""
    <style>
    .stHeadingContainer a {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Inventory Management")
st.markdown("---")

# Initialize
loader = DataLoader()
processor = DataProcessor()
analytics = InventoryAnalytics()
viz = InventoryVisualizations()

# Load data
ingredient_df = loader.load_ingredient_data()
shipment_df = loader.load_shipment_data()

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")

    # Filter by shipment frequency
    if not shipment_df.empty and 'frequency' in shipment_df.columns:
        frequencies = ['All'] + shipment_df['frequency'].unique().tolist()
        selected_freq = st.selectbox("Shipment Frequency", frequencies)

    # Filter by status
    status_filter = st.multiselect(
        "Stock Status",
        ['Low Stock', 'Normal', 'Overstock'],
        default=['Low Stock', 'Normal', 'Overstock']
    )

    st.markdown("---")
    st.info("💡 Use filters to focus on specific inventory segments")

# Clean and process data
shipment_clean = processor.clean_shipment_data(shipment_df)

# Simulate current stock levels (in production, this would come from real data)
if not shipment_clean.empty:
    np.random.seed(42)  # For reproducibility

    # Add simulated current stock
    shipment_clean['current_stock'] = shipment_clean['quantity_per_shipment'] * np.random.uniform(0.5, 3.0, len(shipment_clean))
    shipment_clean['current_stock'] = shipment_clean['current_stock'].round(1)

    # Calculate metrics
    shipment_clean['avg_daily_usage'] = shipment_clean.apply(
        lambda row: row['quantity_per_shipment'] * row['num_shipments'] / 30,
        axis=1
    )

    # Calculate lead time in days
    shipment_clean['lead_time_days'] = shipment_clean['frequency'].apply(processor.frequency_to_days)

    # Calculate reorder point
    shipment_clean['reorder_point'] = shipment_clean.apply(
        lambda row: processor.calculate_reorder_point(row['avg_daily_usage'], row['lead_time_days']),
        axis=1
    )

    # Determine status
    def get_status(row):
        if row['current_stock'] < row['reorder_point']:
            return 'Low Stock'
        elif row['current_stock'] > row['avg_daily_usage'] * 60:
            return 'Overstock'
        else:
            return 'Normal'

    shipment_clean['status'] = shipment_clean.apply(get_status, axis=1)

    # Days until stockout
    shipment_clean['days_of_stock'] = (shipment_clean['current_stock'] / shipment_clean['avg_daily_usage']).round(1)

# Apply filters
filtered_df = shipment_clean.copy()

if 'selected_freq' in locals() and selected_freq != 'All':
    filtered_df = filtered_df[filtered_df['frequency'] == selected_freq]

if status_filter:
    filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]

# Summary metrics
st.header("📊 Inventory Summary")

col1, col2, col3, col4 = st.columns(4)

if not filtered_df.empty:
    total_items = len(filtered_df)
    low_stock = len(filtered_df[filtered_df['status'] == 'Low Stock'])
    overstock = len(filtered_df[filtered_df['status'] == 'Overstock'])
    normal = len(filtered_df[filtered_df['status'] == 'Normal'])

    with col1:
        viz.create_kpi_card("Total Items", str(total_items))

    with col2:
        viz.create_kpi_card("Low Stock", str(low_stock), delta=None, delta_color="inverse")

    with col3:
        viz.create_kpi_card("Normal", str(normal))

    with col4:
        viz.create_kpi_card("Overstock", str(overstock), delta=None, delta_color="off")

# Alerts
st.header("🚨 Inventory Alerts")

if not filtered_df.empty:
    # Critical low stock
    critical = filtered_df[filtered_df['status'] == 'Low Stock'].sort_values('days_of_stock')

    if not critical.empty:
        st.error(f"⚠️ **{len(critical)} items require immediate reorder!**")

        with st.expander("View Critical Items", expanded=True):
            display_cols = ['ingredient', 'current_stock', 'reorder_point', 'days_of_stock', 'frequency']
            st.dataframe(
                critical[display_cols].head(10),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.success("✅ No critical stock alerts")

    # Overstock items
    overstock_items = filtered_df[filtered_df['status'] == 'Overstock']

    if not overstock_items.empty:
        st.warning(f"⚠️ **{len(overstock_items)} items are overstocked**")

        with st.expander("View Overstock Items"):
            display_cols = ['ingredient', 'current_stock', 'avg_daily_usage', 'days_of_stock']
            st.dataframe(
                overstock_items[display_cols],
                use_container_width=True,
                hide_index=True
            )

# Inventory visualization
st.header("📊 Current Inventory Levels")

if not filtered_df.empty:
    col1, col2 = st.columns([3, 1])

    with col1:
        # Bar chart
        fig = viz.plot_inventory_levels(filtered_df, title="Inventory Status by Ingredient")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Status Distribution")
        status_counts = filtered_df['status'].value_counts()

        for status, count in status_counts.items():
            if status == 'Low Stock':
                st.error(f"🔴 {status}: {count}")
            elif status == 'Overstock':
                st.warning(f"🟡 {status}: {count}")
            else:
                st.success(f"🟢 {status}: {count}")

# Detailed inventory table
st.header("📋 Detailed Inventory")

if not filtered_df.empty:
    # Add search
    search = st.text_input("🔍 Search ingredients", "")

    if search:
        filtered_df = filtered_df[filtered_df['ingredient'].str.contains(search, case=False, na=False)]

    # Display table
    display_columns = [
        'ingredient',
        'current_stock',
        'unit',
        'reorder_point',
        'avg_daily_usage',
        'days_of_stock',
        'status',
        'frequency'
    ]

    # Color-code the status
    def highlight_status(row):
        if row['status'] == 'Low Stock':
            return ['background-color: #ffcdd2'] * len(row)
        elif row['status'] == 'Overstock':
            return ['background-color: #fff9c4'] * len(row)
        else:
            return ['background-color: #c8e6c9'] * len(row)

    styled_df = filtered_df[display_columns].style.apply(highlight_status, axis=1)

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )

    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Inventory Report (CSV)",
        data=csv,
        file_name="inventory_report.csv",
        mime="text/csv"
    )

# Reorder recommendations
st.header("🔄 Reorder Recommendations")

if not filtered_df.empty:
    # Items needing reorder
    reorder_items = filtered_df[filtered_df['current_stock'] < filtered_df['reorder_point']]

    if not reorder_items.empty:
        st.info(f"📝 **{len(reorder_items)} items recommended for reorder**")

        # Calculate recommended order quantities
        reorder_items['recommended_order'] = (
            reorder_items['reorder_point'] - reorder_items['current_stock'] + reorder_items['quantity_per_shipment']
        ).round(1)

        cols_to_show = ['ingredient', 'current_stock', 'reorder_point', 'recommended_order', 'unit', 'frequency']

        st.dataframe(
            reorder_items[cols_to_show],
            use_container_width=True,
            hide_index=True
        )

        # Download reorder list
        reorder_csv = reorder_items[cols_to_show].to_csv(index=False)
        st.download_button(
            label="📥 Download Reorder List",
            data=reorder_csv,
            file_name="reorder_recommendations.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ All inventory levels are adequate. No immediate reorders needed.")

# Inventory metrics
st.header("📈 Inventory Metrics")

col1, col2, col3 = st.columns(3)

if not filtered_df.empty:
    avg_days = filtered_df['days_of_stock'].mean()
    total_value = filtered_df['current_stock'].sum()  # Placeholder
    items_below_reorder = len(filtered_df[filtered_df['current_stock'] < filtered_df['reorder_point']])

    with col1:
        st.metric("Avg Days of Stock", f"{avg_days:.1f} days")

    with col2:
        st.metric("Total Stock Units", f"{total_value:.1f}")

    with col3:
        st.metric("Items Below Reorder Point", items_below_reorder)

# Footer
st.markdown("---")
st.info("💡 **Tip:** Set up automated alerts to get notified when items reach reorder points.")
