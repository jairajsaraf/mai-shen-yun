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

# Hide anchor links
st.markdown("""
    <style>
    .stHeadingContainer a {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

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

# Exchange rates (USD as base currency)
EXCHANGE_RATES = {
    "USD ($)": 1.0,
    "EUR (€)": 0.92,
    "GBP (£)": 0.79,
    "JPY (¥)": 149.50
}

def convert_currency(amount, from_currency="USD ($)", to_currency="USD ($)"):
    """Convert amount from USD to target currency"""
    if from_currency == to_currency:
        return amount
    # Convert to USD first (if needed), then to target currency
    usd_amount = amount / EXCHANGE_RATES[from_currency]
    converted = usd_amount * EXCHANGE_RATES[to_currency]
    return converted

# Sidebar
with st.sidebar:
    st.header("💵 Cost Settings")

    # Currency
    currency = st.selectbox("Currency", ["USD ($)", "EUR (€)", "GBP (£)", "JPY (¥)"], index=0)
    currency_symbol = currency.split("(")[1].split(")")[0]

    # Default unit costs (these would come from a database in production)
    st.subheader("Unit Cost Settings")
    st.info("💡 Adjust unit costs to reflect your actual procurement prices")

    # Time period for analysis
    analysis_period = st.selectbox(
        "Analysis Period",
        ["Monthly", "Quarterly", "Yearly"]
    )

    # Show exchange rate info
    if currency != "USD ($)":
        st.info(f"Exchange Rate: 1 USD = {EXCHANGE_RATES[currency]:.2f} {currency_symbol}")

    st.markdown("---")
    st.write("**Cost Categories:**")
    st.write("- Purchase Costs")
    st.write("- Holding Costs")
    st.write("- Ordering Costs")
    st.write("- Waste Costs")

# Cost Overview
st.header("📊 Cost Overview")

# Period multiplier for analysis
period_multiplier = 1 if analysis_period == "Monthly" else 3 if analysis_period == "Quarterly" else 12
period_label = analysis_period.rstrip('ly')  # "Month", "Quarter", "Year"

if not shipment_df.empty:
    shipment_clean = processor.clean_shipment_data(shipment_df)

    # Simulate unit costs in USD (in production, these would be real data)
    np.random.seed(42)
    shipment_clean['unit_cost_usd'] = np.random.uniform(2, 50, len(shipment_clean))

    # Calculate total purchase cost per ingredient
    shipment_clean['monthly_quantity'] = shipment_clean.apply(
        lambda row: row['quantity_per_shipment'] * row['num_shipments'],
        axis=1
    )

    # Calculate cost in USD first, then convert to selected currency
    shipment_clean['monthly_cost_usd'] = shipment_clean['monthly_quantity'] * shipment_clean['unit_cost_usd']
    shipment_clean['period_cost'] = shipment_clean['monthly_cost_usd'] * period_multiplier

    # Convert to selected currency
    shipment_clean['period_cost_converted'] = shipment_clean['period_cost'].apply(
        lambda x: convert_currency(x, "USD ($)", currency)
    )

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_period_cost = shipment_clean['period_cost_converted'].sum()
    avg_cost_per_item = shipment_clean['period_cost_converted'].mean()
    highest_cost_item = shipment_clean.loc[shipment_clean['period_cost_converted'].idxmax(), 'ingredient']
    num_items = len(shipment_clean)

    with col1:
        viz.create_kpi_card(
            f"Total {period_label} Cost",
            f"{currency_symbol}{total_period_cost:,.2f}"
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
        top_cost = shipment_clean.nlargest(10, 'period_cost_converted')[['ingredient', 'period_cost_converted']]

        import plotly.graph_objects as go

        fig = go.Figure(data=[
            go.Bar(
                y=top_cost['ingredient'],
                x=top_cost['period_cost_converted'],
                orientation='h',
                marker_color='#FF6B6B',
                text=[f"{currency_symbol}{x:,.2f}" for x in top_cost['period_cost_converted']],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title=f"Top 10 Most Expensive Ingredients ({period_label})",
            xaxis_title=f"Cost ({currency_symbol})",
            yaxis_title="Ingredient",
            template="plotly_white",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Cost Statistics")

        st.metric("Total", f"{currency_symbol}{total_period_cost:,.2f}")
        st.metric("Median", f"{currency_symbol}{shipment_clean['period_cost_converted'].median():,.2f}")
        st.metric("Std Dev", f"{currency_symbol}{shipment_clean['period_cost_converted'].std():,.2f}")

        # Cost distribution
        high_cost = len(shipment_clean[shipment_clean['period_cost_converted'] > avg_cost_per_item])
        st.write(f"**Above average cost:** {high_cost} items")

    # Cost by frequency
    st.subheader("📦 Cost by Shipment Frequency")

    freq_cost = shipment_clean.groupby('frequency')['period_cost_converted'].sum().reset_index()
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

    # Convert savings to selected currency
    total_potential_savings_converted = convert_currency(eoq_df['Potential Savings'].sum(), "USD ($)", currency)
    st.success(f"💡 **Potential monthly savings: {currency_symbol}{total_potential_savings_converted:,.2f}**")

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

        # Create monthly cost trend in USD
        monthly_costs_usd = []
        base_cost_usd = shipment_clean['monthly_cost_usd'].sum() if not shipment_clean.empty else 1000

        for month in months:
            # Simulate cost variation (would be real data in production)
            variation = np.random.uniform(0.9, 1.1)
            monthly_costs_usd.append(base_cost_usd * variation)

        # Convert to selected currency and apply period aggregation
        if analysis_period == "Monthly":
            period_costs = [convert_currency(cost, "USD ($)", currency) for cost in monthly_costs_usd]
            period_labels = months
        elif analysis_period == "Quarterly":
            # Aggregate by quarter
            period_costs = []
            period_labels = []
            for i in range(0, len(monthly_costs_usd), 3):
                quarter_cost = sum(monthly_costs_usd[i:i+3])
                period_costs.append(convert_currency(quarter_cost, "USD ($)", currency))
                period_labels.append(f"Q{i//3 + 1} ({months[i]})")
        else:  # Yearly
            yearly_cost = sum(monthly_costs_usd)
            period_costs = [convert_currency(yearly_cost, "USD ($)", currency)]
            period_labels = ["Year Total"]

        trend_df = pd.DataFrame({
            'Period': period_labels,
            'Total Cost': period_costs
        })

        fig_trend = go.Figure()

        fig_trend.add_trace(go.Scatter(
            x=trend_df['Period'],
            y=trend_df['Total Cost'],
            mode='lines+markers',
            name=f'{period_label} Cost',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=10)
        ))

        fig_trend.update_layout(
            title=f"{period_label} Cost Trend",
            xaxis_title="Period",
            yaxis_title=f"Total Cost ({currency_symbol})",
            template="plotly_white",
            height=400
        )

        st.plotly_chart(fig_trend, use_container_width=True)

        # Cost variance analysis
        st.subheader("📊 Cost Variance")

        col1, col2, col3 = st.columns(3)

        with col1:
            avg_cost = np.mean(period_costs)
            st.metric(f"Average {period_label} Cost", f"{currency_symbol}{avg_cost:,.2f}")

        with col2:
            max_cost = np.max(period_costs)
            max_period = period_labels[np.argmax(period_costs)]
            st.metric(f"Highest ({max_period})", f"{currency_symbol}{max_cost:,.2f}")

        with col3:
            min_cost = np.min(period_costs)
            min_period = period_labels[np.argmin(period_costs)]
            st.metric(f"Lowest ({min_period})", f"{currency_symbol}{min_cost:,.2f}")

# Waste & Spoilage Analysis
st.header("🗑️ Waste & Spoilage Analysis")

# How to use explanation
st.info("""
**📖 How to Use Waste & Spoilage Analysis:**

This section helps you identify and reduce waste costs:
1. **Review waste percentages** by category (perishables, proteins, dry goods)
2. **Identify high-waste categories** - these offer the biggest savings opportunities
3. **Calculate financial impact** - see how waste affects your bottom line
4. **Follow recommendations** - implement suggested strategies to reduce waste
5. **Monitor trends** - track waste reduction over time after implementing changes

💡 **Typical industry waste rates:** 4-10% for restaurants. Reducing waste by even 1-2% can significantly improve profitability.
""")

with st.expander("View Waste Analysis", expanded=False):
    st.write("**Estimated Waste by Category:**")

    # Simulate waste data
    waste_categories = {
        'Perishables (Vegetables)': 5.0,
        'Proteins (Meat)': 3.0,
        'Dry Goods': 1.0,
        'Other': 2.0
    }

    # Use USD cost first, then convert
    base_monthly_cost_usd = shipment_clean['monthly_cost_usd'].sum() if not shipment_clean.empty else 1000
    base_monthly_cost_converted = convert_currency(base_monthly_cost_usd, "USD ($)", currency)

    waste_df = pd.DataFrame([
        {'Category': k, 'Waste %': v, 'Estimated Cost': base_monthly_cost_converted * (v/100)}
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

# How to use explanation
st.info("""
**📖 How to Use the ROI Calculator:**

Calculate the return on investment for inventory management improvements:

1. **Enter Investment Costs:**
   - Software/system costs (inventory management software, POS integration, etc.)
   - Training costs (staff training, onboarding time, etc.)

2. **Set Expected Benefits:**
   - **Waste Reduction (%):** How much you expect to reduce waste (typical: 10-20%)
   - **Efficiency Gain (%):** Time/cost savings from better processes (typical: 10-15%)

3. **Review Results:**
   - **Annual Savings:** Total cost savings per year
   - **ROI (%):** Return on investment percentage (higher is better)
   - **Payback Period:** How long until the investment pays for itself

💡 **Rule of Thumb:** An ROI > 100% or payback period < 12 months is generally considered excellent for inventory improvements.
""")

with st.expander("Calculate ROI for Inventory Improvements", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Investment")
        software_cost = st.number_input(f"Software/System Cost ({currency_symbol})", value=5000, step=100)
        training_cost = st.number_input(f"Training Cost ({currency_symbol})", value=1000, step=100)
        total_investment = software_cost + training_cost

    with col2:
        st.subheader("Expected Benefits")
        waste_reduction = st.slider("Waste Reduction (%)", 0, 50, 20)
        efficiency_gain = st.slider("Efficiency Gain (%)", 0, 50, 15)

    # Calculate ROI in selected currency
    annual_cost_usd = (shipment_clean['monthly_cost_usd'].sum() * 12) if not shipment_clean.empty else 120000
    annual_cost_converted = convert_currency(annual_cost_usd, "USD ($)", currency)
    annual_savings = annual_cost_converted * (waste_reduction + efficiency_gain) / 100
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
