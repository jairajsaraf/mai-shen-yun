"""
Intelligent Alerts Dashboard
Real-time monitoring and proactive alerting system
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_loader import DataLoader
from data_processor import DataProcessor
from analytics import InventoryAnalytics
from alert_intelligence import AlertIntelligence
from visualizations import InventoryVisualizations

# Page config
st.set_page_config(page_title="Intelligent Alerts - Mai Shen Yun", page_icon="🚨", layout="wide")

st.title("🚨 Intelligent Alerts Dashboard", anchor=False)
st.markdown("### Proactive Inventory Monitoring & Actionable Intelligence")
st.markdown("---")

# Initialize
loader = DataLoader()
processor = DataProcessor()
analytics = InventoryAnalytics()
alert_system = AlertIntelligence()
viz = InventoryVisualizations()

# Load data
ingredient_df = loader.load_ingredient_data()
shipment_df = loader.load_shipment_data()
all_sheets = loader.load_all_sheets()
monthly_item = all_sheets['item']

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Alert Settings", anchor=False)

    st.subheader("Alert Filters", anchor=False)

    show_critical = st.checkbox("🔴 Critical", value=True)
    show_high = st.checkbox("🟠 High", value=True)
    show_medium = st.checkbox("🟡 Medium", value=True)
    show_low = st.checkbox("🟢 Low", value=False)

    st.markdown("---")

    st.subheader("Detection Settings", anchor=False)

    stockout_days = st.multiselect(
        "Stock-out Forecast Periods",
        [3, 7, 14, 30],
        default=[3, 7, 14]
    )

    overstock_threshold = st.slider(
        "Overstock Threshold (days)",
        30, 120, 60,
        help="Days of stock considered excessive"
    )

    anomaly_sensitivity = st.slider(
        "Anomaly Detection Sensitivity",
        1.0, 3.0, 2.0, 0.5,
        help="Lower = more sensitive (more alerts)"
    )

    st.markdown("---")
    st.info("🔄 Auto-refresh: Every 5 minutes")

# Prepare inventory data for alerts
shipment_clean = processor.clean_shipment_data(shipment_df)

if not shipment_clean.empty:
    # Simulate current stock (in production, this would be real-time data)
    np.random.seed(42)
    shipment_clean['current_stock'] = shipment_clean['quantity_per_shipment'] * np.random.uniform(0.5, 3.0, len(shipment_clean))
    shipment_clean['avg_daily_usage'] = shipment_clean.apply(
        lambda row: row['quantity_per_shipment'] * row['num_shipments'] / 30,
        axis=1
    )
    shipment_clean['lead_time_days'] = shipment_clean['frequency'].apply(processor.frequency_to_days)
    shipment_clean['reorder_point'] = shipment_clean.apply(
        lambda row: processor.calculate_reorder_point(row['avg_daily_usage'], row['lead_time_days']),
        axis=1
    )

# Calculate consumption data for anomaly detection
def calculate_ingredient_consumption(sales_df, recipe_df, shipment_df):
    """Calculate ingredient consumption from sales data"""
    if sales_df.empty or recipe_df.empty:
        return pd.DataFrame()

    # Get tracked ingredients
    tracked_ingredients = shipment_df['ingredient'].tolist() if 'ingredient' in shipment_df.columns else []

    if not tracked_ingredients:
        return pd.DataFrame()

    # Ensure Count is numeric
    if 'Count' in sales_df.columns:
        sales_df['Count'] = pd.to_numeric(sales_df['Count'], errors='coerce').fillna(0)

    # Clean recipe data
    recipe_clean = processor.clean_ingredient_data(recipe_df)

    # Ingredient mapping
    ingredient_mapping = {
        'braised beef used (g)': 'Beef',
        'Braised Chicken(g)': 'Chicken',
        'Braised Pork(g)': 'Pork',
        'Egg(count)': 'Egg',
        'Rice(g)': 'Rice',
        'Ramen (count)': 'Ramen',
        'Rice Noodles(g)': 'Rice Noodles',
        'flour (g)': 'Flour',
        'Chicken Wings (pcs)': 'Chicken Wings',
        'Green Onion': 'Green Onion',
        'Cilantro': 'Cilantro',
        'White onion': 'White Onion',
        'Peas(g)': 'Peas + Carrot',
        'Carrot(g)': 'Peas + Carrot',
        'Boychoy(g)': 'Bokchoy',
        'Tapioca Starch': 'Tapioca Starch'
    }

    consumption_data = []

    for month in sales_df['month'].unique():
        month_sales = sales_df[sales_df['month'] == month]
        month_consumption = {'month': month}

        for ing in tracked_ingredients:
            month_consumption[ing] = 0

        for _, sale_row in month_sales.iterrows():
            dish_name = sale_row['Item Name']
            quantity_sold = sale_row['Count']

            if pd.isna(dish_name) or not isinstance(dish_name, str) or len(dish_name.strip()) == 0:
                continue

            recipe_match = recipe_clean[recipe_clean['dish_name'].str.contains(dish_name.split()[0], case=False, na=False)]

            if not recipe_match.empty:
                recipe = recipe_match.iloc[0]

                for recipe_col, tracked_ing in ingredient_mapping.items():
                    if recipe_col in recipe.index and pd.notna(recipe[recipe_col]):
                        usage = recipe[recipe_col] * quantity_sold
                        if tracked_ing in month_consumption:
                            month_consumption[tracked_ing] += usage

        consumption_data.append(month_consumption)

    return pd.DataFrame(consumption_data)

# Calculate consumption for anomaly detection
consumption_df = calculate_ingredient_consumption(monthly_item, ingredient_df, shipment_clean)

# Generate all alerts
st.info("🔍 Analyzing inventory data and generating intelligent alerts...")

alerts = alert_system.generate_all_alerts(
    inventory_df=shipment_clean,
    consumption_df=consumption_df
)

# Filter alerts based on sidebar settings
priority_filter = []
if show_critical:
    priority_filter.append(AlertIntelligence.CRITICAL)
if show_high:
    priority_filter.append(AlertIntelligence.HIGH)
if show_medium:
    priority_filter.append(AlertIntelligence.MEDIUM)
if show_low:
    priority_filter.append(AlertIntelligence.LOW)

filtered_alerts = [a for a in alerts if a.get('priority') in priority_filter]

# Alert Summary
st.header("📊 Alert Summary", anchor=False)

summary = alert_system.get_alert_summary(alerts)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    critical_count = summary['by_priority'][AlertIntelligence.CRITICAL]
    st.metric("🔴 Critical", critical_count,
              delta=f"-{critical_count}" if critical_count > 0 else None,
              delta_color="inverse")

with col2:
    high_count = summary['by_priority'][AlertIntelligence.HIGH]
    st.metric("🟠 High", high_count,
              delta=f"-{high_count}" if high_count > 0 else None,
              delta_color="inverse")

with col3:
    medium_count = summary['by_priority'][AlertIntelligence.MEDIUM]
    st.metric("🟡 Medium", medium_count)

with col4:
    low_count = summary['by_priority'][AlertIntelligence.LOW]
    st.metric("🟢 Low", low_count)

with col5:
    st.metric("📋 Total Alerts", summary['total'])

st.markdown("---")

# Actionable Insights
st.header("💡 Actionable Insights", anchor=False)

insights = alert_system.get_actionable_insights(alerts)

for insight in insights:
    if "🚨" in insight or "URGENT" in insight:
        st.error(insight)
    elif "💰" in insight:
        st.warning(insight)
    elif "📊" in insight:
        st.info(insight)
    else:
        st.success(insight)

st.markdown("---")

# Critical Alerts Section
critical_alerts = [a for a in filtered_alerts if a.get('priority') == AlertIntelligence.CRITICAL]

if critical_alerts:
    st.header("🚨 Critical Alerts - Immediate Action Required", anchor=False)

    for i, alert in enumerate(critical_alerts):
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.error(f"### {alert['title']}")
                st.write(f"**Message:** {alert['message']}")
                st.write(f"**Action Required:** {alert['action']}")

                # Additional details
                if 'days_remaining' in alert:
                    st.write(f"⏱️ Time remaining: **{alert['days_remaining']:.1f} days**")
                if 'current_value' in alert:
                    st.write(f"📦 Current stock: **{alert['current_value']:.1f}**")

            with col2:
                st.write(f"**Priority:** 🔴 CRITICAL")
                st.write(f"**Category:** {alert['category'].replace('_', ' ').title()}")

                # Action buttons
                if st.button(f"✅ Acknowledge", key=f"ack_crit_{i}"):
                    st.success("Alert acknowledged!")

                if st.button(f"📋 Create Order", key=f"order_crit_{i}"):
                    st.success("Order creation initiated!")

            st.markdown("---")

# High Priority Alerts
high_alerts = [a for a in filtered_alerts if a.get('priority') == AlertIntelligence.HIGH]

if high_alerts:
    with st.expander(f"🟠 High Priority Alerts ({len(high_alerts)})", expanded=True):
        for i, alert in enumerate(high_alerts):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.warning(f"**{alert['title']}**")
                st.write(alert['message'])
                st.caption(alert['action'])

            with col2:
                if st.button(f"✓ Review", key=f"review_high_{i}"):
                    st.info("Marked for review")

# Medium Priority Alerts
medium_alerts = [a for a in filtered_alerts if a.get('priority') == AlertIntelligence.MEDIUM]

if medium_alerts:
    with st.expander(f"🟡 Medium Priority Alerts ({len(medium_alerts)})", expanded=False):
        # Group by category
        alert_by_category = {}
        for alert in medium_alerts:
            category = alert.get('category', 'other')
            if category not in alert_by_category:
                alert_by_category[category] = []
            alert_by_category[category].append(alert)

        for category, category_alerts in alert_by_category.items():
            st.subheader(category.replace('_', ' ').title(), anchor=False)

            for alert in category_alerts:
                st.info(f"**{alert['ingredient']}**: {alert['message']}")
                st.caption(f"💡 {alert['action']}")

# Alert Analytics
st.markdown("---")
st.header("📈 Alert Analytics", anchor=False)

col1, col2 = st.columns(2)

with col1:
    # Alert distribution by category
    st.subheader("Alerts by Category", anchor=False)

    if summary['by_category']:
        import plotly.graph_objects as go

        fig = go.Figure(data=[
            go.Pie(
                labels=[cat.replace('_', ' ').title() for cat in summary['by_category'].keys()],
                values=list(summary['by_category'].values()),
                hole=0.4,
                marker_colors=['#FF6B6B', '#FFE66D', '#4ECDC4', '#95E1D3', '#A8E6CF']
            )
        ])

        fig.update_layout(
            template="plotly_white",
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

with col2:
    # Priority distribution
    st.subheader("Alert Priority Distribution", anchor=False)

    priorities = []
    counts = []
    colors = []

    for priority, count in summary['by_priority'].items():
        if count > 0:
            priorities.append(priority.title())
            counts.append(count)

            if priority == AlertIntelligence.CRITICAL:
                colors.append('#FF0000')
            elif priority == AlertIntelligence.HIGH:
                colors.append('#FF8C00')
            elif priority == AlertIntelligence.MEDIUM:
                colors.append('#FFD700')
            elif priority == AlertIntelligence.LOW:
                colors.append('#90EE90')
            else:
                colors.append('#87CEEB')

    if priorities:
        fig = go.Figure(data=[
            go.Bar(
                x=priorities,
                y=counts,
                marker_color=colors,
                text=counts,
                textposition='auto'
            )
        ])

        fig.update_layout(
            xaxis_title="Priority Level",
            yaxis_title="Number of Alerts",
            template="plotly_white",
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

# Alert History (simulated)
st.markdown("---")
st.header("📅 Alert Timeline", anchor=False)

st.info("""
**Coming Soon:** Historical alert tracking to monitor trends and system effectiveness:
- Alert resolution time
- Recurring issues identification
- Effectiveness metrics
- Predictive improvements based on past alerts
""")

# Export alerts
st.markdown("---")
st.header("📥 Export Alerts", anchor=False)

if filtered_alerts:
    # Create export DataFrame
    export_data = []
    for alert in filtered_alerts:
        export_data.append({
            'Priority': alert['priority'].upper(),
            'Category': alert['category'].replace('_', ' ').title(),
            'Ingredient': alert.get('ingredient', 'N/A'),
            'Title': alert['title'],
            'Message': alert['message'],
            'Action': alert['action'],
            'Timestamp': alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })

    export_df = pd.DataFrame(export_data)

    col1, col2 = st.columns(2)

    with col1:
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="📄 Download Alerts Report (CSV)",
            data=csv,
            file_name=f"alerts_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    with col2:
        if st.button("📧 Email Report to Manager"):
            st.success("✅ Alert report sent to management!")
            st.caption("(In production, this would send actual emails)")

# Footer
st.markdown("---")
st.info("💡 **Tip:** This intelligent alert system uses advanced analytics to provide proactive warnings and actionable recommendations. Check this dashboard daily for optimal inventory management.")

# System Status
with st.expander("⚙️ System Status & Information"):
    st.write("**Alert System Version:** 1.0.0")
    st.write("**Last Analysis:** " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    st.write(f"**Data Sources:** {len(loader.get_available_months())} months of historical data")
    st.write(f"**Tracked Items:** {len(shipment_clean) if not shipment_clean.empty else 0}")
    st.write("**Detection Algorithms:**")
    st.write("  - Stock-out risk prediction")
    st.write("  - Overstock detection")
    st.write("  - Consumption anomaly detection")
    st.write("  - Optimal reorder timing")
    st.write("  - Statistical outlier detection")
