"""
Cost Analysis Page
Financial insights and cost optimization
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
st.set_page_config(page_title="Cost Analysis - Mai Shen Yun", page_icon="💰", layout="wide")

st.title("💰 Cost Analysis & Optimization")
st.markdown("---")

# Initialize
loader = DataLoader()
processor = DataProcessor()
analytics = InventoryAnalytics()
viz = InventoryVisualizations()

# Load data
ingredient_df = loader.load_ingredient_data()
shipment_df = loader.load_shipment_data()
monthly_df = loader.load_monthly_data()

# Sidebar
with st.sidebar:
    st.header("💵 Cost Settings")

    # Currency
    currency = st.selectbox("Currency", ["USD ($)", "EUR (€)", "GBP (£)"], index=0)
    currency_symbol = currency.split("(")[1].split(")")[0]

    # Default unit costs (these would come from a database in production)
    st.subheader("Unit Cost Settings")
    st.info("💡 Adjust unit costs to reflect your actual procurement prices")

    # Time period for analysis
    analysis_period = st.selectbox(
        "Analysis Period",
        ["Monthly", "Quarterly", "Yearly"]
    )

    st.markdown("---")
    st.write("**Cost Categories:**")
    st.write("- Purchase Costs")
    st.write("- Holding Costs")
    st.write("- Ordering Costs")
    st.write("- Waste Costs")

# Cost Overview
st.header("📊 Cost Overview")

if not shipment_df.empty:
    shipment_clean = processor.clean_shipment_data(shipment_df)

    # Simulate unit costs (in production, these would be real data)
    np.random.seed(42)
    shipment_clean['unit_cost'] = np.random.uniform(2, 50, len(shipment_clean))

    # Calculate total purchase cost per ingredient
    shipment_clean['monthly_quantity'] = shipment_clean.apply(
        lambda row: row['quantity_per_shipment'] * row['num_shipments'],
        axis=1
    )

    shipment_clean['monthly_cost'] = shipment_clean['monthly_quantity'] * shipment_clean['unit_cost']

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_monthly_cost = shipment_clean['monthly_cost'].sum()
    avg_cost_per_item = shipment_clean['monthly_cost'].mean()
    highest_cost_item = shipment_clean.loc[shipment_clean['monthly_cost'].idxmax(), 'ingredient']
    num_items = len(shipment_clean)

    with col1:
        viz.create_kpi_card(
            "Total Monthly Cost",
            f"{currency_symbol}{total_monthly_cost:,.2f}"
        )

    with col2:
        viz.create_kpi_card(
            "Avg Cost per Item",
            f"{currency_symbol}{avg_cost_per_item:,.2f}"
        )

    with col3:
        st.metric("Highest Cost Item", highest_cost_item)

    with col4:
        viz.create_kpi_card(
            "Items Tracked",
            str(num_items)
        )

    # Cost breakdown by ingredient
    st.header("💵 Cost Breakdown")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Top 10 most expensive ingredients
        top_cost = shipment_clean.nlargest(10, 'monthly_cost')[['ingredient', 'monthly_cost']]

        import plotly.graph_objects as go

        fig = go.Figure(data=[
            go.Bar(
                y=top_cost['ingredient'],
                x=top_cost['monthly_cost'],
                orientation='h',
                marker_color='#FF6B6B',
                text=[f"{currency_symbol}{x:,.2f}" for x in top_cost['monthly_cost']],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title="Top 10 Most Expensive Ingredients (Monthly)",
            xaxis_title=f"Cost ({currency_symbol})",
            yaxis_title="Ingredient",
            template="plotly_white",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Cost Statistics")

        st.metric("Total", f"{currency_symbol}{total_monthly_cost:,.2f}")
        st.metric("Median", f"{currency_symbol}{shipment_clean['monthly_cost'].median():,.2f}")
        st.metric("Std Dev", f"{currency_symbol}{shipment_clean['monthly_cost'].std():,.2f}")

        # Cost distribution
        high_cost = len(shipment_clean[shipment_clean['monthly_cost'] > avg_cost_per_item])
        st.write(f"**Above average cost:** {high_cost} items")

    # Cost by frequency
    st.subheader("📦 Cost by Shipment Frequency")

    freq_cost = shipment_clean.groupby('frequency')['monthly_cost'].sum().reset_index()
    freq_cost.columns = ['Frequency', 'Total Cost']

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_pie = go.Figure(data=[
            go.Pie(
                labels=freq_cost['Frequency'],
                values=freq_cost['Total Cost'],
                hole=0.4,
                textinfo='label+percent',
                marker_colors=['#FF6B6B', '#4ECDC4', '#95E1D3', '#FFE66D']
            )
        ])

        fig_pie.update_layout(
            title="Cost Distribution by Shipment Frequency",
            template="plotly_white",
            height=400
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.dataframe(
            freq_cost.assign(**{'Total Cost': freq_cost['Total Cost'].apply(lambda x: f"{currency_symbol}{x:,.2f}")}),
            use_container_width=True,
            hide_index=True
        )

# Cost Optimization Opportunities
st.header("🎯 Cost Optimization Opportunities")

if not shipment_clean.empty:
    # Calculate EOQ for each item
    st.subheader("📉 Economic Order Quantity (EOQ) Analysis")

    st.info("""
    **EOQ** helps determine the optimal order quantity that minimizes total inventory costs (ordering + holding costs).
    """)

    # Simulate ordering and holding costs
    ordering_cost = 50  # Cost per order
    holding_cost_rate = 0.25  # 25% of unit cost per year

    eoq_analysis = []

    for _, row in shipment_clean.iterrows():
        annual_demand = row['monthly_quantity'] * 12
        holding_cost = row['unit_cost'] * holding_cost_rate

        eoq = analytics.calculate_eoq(annual_demand, ordering_cost, holding_cost)

        eoq_analysis.append({
            'Ingredient': row['ingredient'],
            'Current Order Qty': row['quantity_per_shipment'],
            'Optimal EOQ': round(eoq, 1),
            'Potential Savings': abs(row['quantity_per_shipment'] - eoq) * 0.1,  # Simplified
            'Recommendation': 'Increase' if eoq > row['quantity_per_shipment'] else 'Decrease'
        })

    eoq_df = pd.DataFrame(eoq_analysis)

    # Show top opportunities
    top_savings = eoq_df.nlargest(10, 'Potential Savings')

    st.dataframe(
        top_savings,
        use_container_width=True,
        hide_index=True
    )

    total_potential_savings = eoq_df['Potential Savings'].sum()
    st.success(f"💡 **Potential monthly savings: {currency_symbol}{total_potential_savings:,.2f}**")

    # Download
    csv = eoq_df.to_csv(index=False)
    st.download_button(
        label="📥 Download EOQ Analysis (CSV)",
        data=csv,
        file_name="eoq_analysis.csv",
        mime="text/csv"
    )

# Cost trends (if monthly data available)
if not monthly_df.empty:
    st.header("📈 Cost Trends Over Time")

    monthly_clean = processor.process_monthly_sales(monthly_df)

    if not monthly_clean.empty and 'month' in monthly_clean.columns:
        # Simulate costs over time
        months = loader.get_available_months()

        # Create monthly cost trend
        monthly_costs = []

        for month in months:
            # Simulate cost (would be real data in production)
            base_cost = total_monthly_cost if not shipment_clean.empty else 1000
            variation = np.random.uniform(0.9, 1.1)
            monthly_costs.append(base_cost * variation)

        trend_df = pd.DataFrame({
            'Month': months,
            'Total Cost': monthly_costs
        })

        fig_trend = go.Figure()

        fig_trend.add_trace(go.Scatter(
            x=trend_df['Month'],
            y=trend_df['Total Cost'],
            mode='lines+markers',
            name='Monthly Cost',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=10)
        ))

        fig_trend.update_layout(
            title="Monthly Cost Trend",
            xaxis_title="Month",
            yaxis_title=f"Total Cost ({currency_symbol})",
            template="plotly_white",
            height=400
        )

        st.plotly_chart(fig_trend, use_container_width=True)

        # Cost variance analysis
        st.subheader("📊 Cost Variance")

        col1, col2, col3 = st.columns(3)

        with col1:
            avg_monthly = np.mean(monthly_costs)
            st.metric("Average Monthly Cost", f"{currency_symbol}{avg_monthly:,.2f}")

        with col2:
            max_cost = np.max(monthly_costs)
            max_month = months[np.argmax(monthly_costs)]
            st.metric(f"Highest ({max_month})", f"{currency_symbol}{max_cost:,.2f}")

        with col3:
            min_cost = np.min(monthly_costs)
            min_month = months[np.argmin(monthly_costs)]
            st.metric(f"Lowest ({min_month})", f"{currency_symbol}{min_cost:,.2f}")

# Waste & Spoilage Analysis
st.header("🗑️ Waste & Spoilage Analysis")

with st.expander("View Waste Analysis", expanded=False):
    st.write("**Estimated Waste by Category:**")

    # Simulate waste data
    waste_categories = {
        'Perishables (Vegetables)': 5.0,
        'Proteins (Meat)': 3.0,
        'Dry Goods': 1.0,
        'Other': 2.0
    }

    waste_df = pd.DataFrame([
        {'Category': k, 'Waste %': v, 'Estimated Cost': total_monthly_cost * (v/100)}
        for k, v in waste_categories.items()
    ])

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(
            waste_df.assign(**{
                'Estimated Cost': waste_df['Estimated Cost'].apply(lambda x: f"{currency_symbol}{x:,.2f}")
            }),
            use_container_width=True,
            hide_index=True
        )

    with col2:
        total_waste_cost = waste_df['Estimated Cost'].sum()
        st.error(f"**Total Monthly Waste Cost: {currency_symbol}{total_waste_cost:,.2f}**")

        st.write("**Recommendations:**")
        st.write("- Implement FIFO (First In, First Out)")
        st.write("- Improve portion control")
        st.write("- Better demand forecasting")
        st.write("- Consider smaller, more frequent orders for perishables")

# ROI Calculator
st.header("💎 ROI Calculator")

with st.expander("Calculate ROI for Inventory Improvements"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Investment")
        software_cost = st.number_input("Software/System Cost", value=5000, step=100)
        training_cost = st.number_input("Training Cost", value=1000, step=100)
        total_investment = software_cost + training_cost

    with col2:
        st.subheader("Expected Benefits")
        waste_reduction = st.slider("Waste Reduction (%)", 0, 50, 20)
        efficiency_gain = st.slider("Efficiency Gain (%)", 0, 50, 15)

    # Calculate ROI
    annual_cost = total_monthly_cost * 12 if not shipment_clean.empty else 120000
    annual_savings = annual_cost * (waste_reduction + efficiency_gain) / 100
    roi = ((annual_savings - total_investment) / total_investment) * 100 if total_investment > 0 else 0
    payback_months = (total_investment / (annual_savings / 12)) if annual_savings > 0 else 0

    st.subheader("📊 ROI Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Annual Savings", f"{currency_symbol}{annual_savings:,.2f}")

    with col2:
        st.metric("ROI", f"{roi:.1f}%")

    with col3:
        st.metric("Payback Period", f"{payback_months:.1f} months")

    if roi > 0:
        st.success(f"✅ This investment would pay for itself in {payback_months:.1f} months!")
    else:
        st.warning("⚠️ Adjust assumptions to improve ROI")

# Footer
st.markdown("---")
st.info("💡 **Tip:** Regular cost analysis helps identify savings opportunities and improve profitability.")
