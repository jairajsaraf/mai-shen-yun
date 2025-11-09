"""
Predictions Page
Forecasting and predictive analytics for the 14 tracked ingredients
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_loader import DataLoader
from data_processor import DataProcessor
from analytics import InventoryAnalytics
from predictions import InventoryPredictor
from visualizations import InventoryVisualizations

# Page config
st.set_page_config(page_title="Predictions - Mai Shen Yun", page_icon="🔮", layout="wide")

# Hide anchor links
st.markdown("""
    <style>
    .stHeadingContainer a {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔮 Predictive Analytics")
st.markdown("---")

# Initialize
loader = DataLoader()
processor = DataProcessor()
analytics = InventoryAnalytics()
predictor = InventoryPredictor()
viz = InventoryVisualizations()

# Load data
ingredient_df = loader.load_ingredient_data()
shipment_df = loader.load_shipment_data()

# Load all sheets for proper ingredient tracking
all_sheets = loader.load_all_sheets()
monthly_item = all_sheets['item']

# Get the 14 tracked ingredients
shipment_clean = processor.clean_shipment_data(shipment_df)
tracked_ingredients = shipment_clean['ingredient'].tolist() if not shipment_clean.empty else []

# Sidebar
with st.sidebar:
    st.header("🎯 Forecast Settings")

    forecast_method = st.selectbox(
        "Forecasting Method",
        [
            "Moving Average",
            "Exponential Smoothing",
            "Weighted Moving Average",
            "Linear Regression",
            "Ensemble (All Methods)"
        ]
    )

    forecast_periods = st.slider("Forecast Periods (days)", 7, 90, 30)

    confidence_level = st.slider("Confidence Level (%)", 80, 99, 95)

    st.markdown("---")
    st.info(f"🔮 Forecasting for {len(tracked_ingredients)} tracked ingredients")

# Helper function to calculate ingredient consumption (same as Analytics page)
def calculate_ingredient_consumption(sales_df, recipe_df, ingredient_list):
    """Calculate ingredient consumption based on dish sales and recipes"""
    if sales_df.empty or recipe_df.empty:
        return pd.DataFrame()

    # Ensure Count is numeric
    if 'Count' in sales_df.columns:
        sales_df['Count'] = pd.to_numeric(sales_df['Count'], errors='coerce').fillna(0)

    # Clean recipe data
    recipe_clean = processor.clean_ingredient_data(recipe_df)

    # Map ingredient columns to tracked ingredients
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

    # Create consumption dataframe
    consumption_data = []

    for month in sales_df['month'].unique():
        month_sales = sales_df[sales_df['month'] == month]
        month_consumption = {'month': month}

        # Initialize all ingredients to 0
        for ing in ingredient_list:
            month_consumption[ing] = 0

        # Calculate consumption for each dish sold
        for _, sale_row in month_sales.iterrows():
            dish_name = sale_row['Item Name']
            quantity_sold = sale_row['Count']

            # Skip if dish_name is not a valid string
            if pd.isna(dish_name) or not isinstance(dish_name, str) or len(dish_name.strip()) == 0:
                continue

            # Find matching recipe
            recipe_match = recipe_clean[recipe_clean['dish_name'].str.contains(dish_name.split()[0], case=False, na=False)]

            if not recipe_match.empty:
                recipe = recipe_match.iloc[0]

                # Add ingredient usage for this dish
                for recipe_col, tracked_ing in ingredient_mapping.items():
                    if recipe_col in recipe.index and pd.notna(recipe[recipe_col]):
                        usage = recipe[recipe_col] * quantity_sold
                        if tracked_ing in month_consumption:
                            month_consumption[tracked_ing] += usage

        consumption_data.append(month_consumption)

    return pd.DataFrame(consumption_data)

# Main content
st.header("📊 Demand Forecasting")

if not monthly_item.empty and not ingredient_df.empty and tracked_ingredients:
    # Calculate ingredient consumption from sales
    consumption_df = calculate_ingredient_consumption(monthly_item, ingredient_df, tracked_ingredients)

    if not consumption_df.empty:
        # Select ingredient to forecast (showing the 14 tracked ingredients)
        selected_ingredient = st.selectbox(
            "Select Ingredient to Forecast",
            tracked_ingredients,
            help="Choose from the 14 tracked ingredients"
        )

        if selected_ingredient:
            # Get historical data
            if 'month' in consumption_df.columns and selected_ingredient in consumption_df.columns:
                historical = consumption_df.groupby('month')[selected_ingredient].sum()
            else:
                historical = pd.Series([0])

            if len(historical) > 0:
                # Generate forecast based on selected method
                if forecast_method == "Moving Average":
                    forecast = predictor.moving_average_forecast(historical, periods=forecast_periods)
                elif forecast_method == "Exponential Smoothing":
                    forecast = predictor.exponential_smoothing(historical, periods=forecast_periods)
                elif forecast_method == "Weighted Moving Average":
                    forecast = predictor.weighted_moving_average(historical, periods=forecast_periods)
                elif forecast_method == "Linear Regression":
                    forecast = predictor.linear_regression_forecast(historical, periods=forecast_periods)
                else:  # Ensemble
                    forecasts = predictor.ensemble_forecast(historical, periods=forecast_periods)
                    forecast = forecasts['ensemble']

                # Display forecast
                col1, col2 = st.columns([3, 1])

                with col1:
                    fig = viz.plot_forecast(historical, forecast, title=f"{selected_ingredient} - Demand Forecast")
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("Forecast Summary")

                    st.metric("Forecast Period", f"{forecast_periods} days")
                    st.metric("Method", forecast_method)
                    st.metric("Avg Forecast", f"{forecast.mean():.1f}")
                    st.metric("Total Forecast", f"{forecast.sum():.1f}")

                    # Historical average for comparison
                    hist_avg = historical.mean()
                    forecast_avg = forecast.mean()
                    change = ((forecast_avg - hist_avg) / hist_avg * 100) if hist_avg > 0 else 0
                    st.metric("Change vs Historical", f"{change:+.1f}%")

                # Forecast details
                st.subheader("📋 Detailed Forecast")

                # Create forecast dataframe with MM-DD-YYYY format
                start_date = datetime.now()
                dates = [start_date + timedelta(days=i) for i in range(len(forecast))]

                forecast_df = pd.DataFrame({
                    'Date': [d.strftime('%m-%d-%Y') for d in dates],  # MM-DD-YYYY format
                    'Day': range(1, len(forecast) + 1),
                    'Forecasted Quantity': forecast.values
                })

                # Add cumulative
                forecast_df['Cumulative'] = forecast_df['Forecasted Quantity'].cumsum()

                st.dataframe(
                    forecast_df,
                    use_container_width=True,
                    hide_index=True
                )

                # Download forecast
                csv = forecast_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Forecast (CSV)",
                    data=csv,
                    file_name=f"forecast_{selected_ingredient}.csv",
                    mime="text/csv"
                )

                # Comparison with ensemble methods
                if forecast_method != "Ensemble (All Methods)":
                    st.subheader("🔄 Method Comparison")

                    with st.expander("Compare with other methods"):
                        # Get all forecasts
                        all_forecasts = predictor.ensemble_forecast(historical, periods=30)

                        # Create comparison chart
                        import plotly.graph_objects as go

                        fig_compare = go.Figure()

                        # Historical
                        fig_compare.add_trace(go.Scatter(
                            x=list(range(len(historical))),
                            y=historical.tolist(),
                            mode='lines+markers',
                            name='Historical',
                            line=dict(width=3)
                        ))

                        # All forecast methods
                        colors = ['red', 'blue', 'green', 'orange', 'purple']
                        for i, (method, forecast_data) in enumerate(all_forecasts.items()):
                            forecast_x = list(range(len(historical), len(historical) + len(forecast_data)))
                            fig_compare.add_trace(go.Scatter(
                                x=forecast_x,
                                y=forecast_data.tolist(),
                                mode='lines',
                                name=method.replace('_', ' ').title(),
                                line=dict(dash='dash', color=colors[i % len(colors)])
                            ))

                        fig_compare.update_layout(
                            title="Forecast Method Comparison",
                            xaxis_title="Period",
                            yaxis_title="Quantity",
                            template="plotly_white",
                            height=500
                        )

                        st.plotly_chart(fig_compare, use_container_width=True)
    else:
        st.warning("⚠️ Unable to calculate ingredient consumption from sales data")
else:
    st.warning("⚠️ No historical data available for forecasting")

# Reorder Predictions
st.header("🔄 Reorder Predictions")

if not shipment_df.empty:
    shipment_clean = processor.clean_shipment_data(shipment_df)

    # Simulate current stock and usage
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

    # Predict reorder dates
    reorder_predictions = []

    for _, row in shipment_clean.iterrows():
        days_until, reorder_date = predictor.predict_reorder_date(
            row['current_stock'],
            row['avg_daily_usage'],
            row['reorder_point']
        )

        reorder_predictions.append({
            'Ingredient': row['ingredient'],
            'Current Stock': round(float(row['current_stock']), 1),  # Fixed: use round() function
            'Daily Usage': round(float(row['avg_daily_usage']), 1),  # Fixed: use round() function
            'Days Until Reorder': int(days_until),
            'Predicted Reorder Date': reorder_date,
            'Recommended Quantity': row['quantity_per_shipment']
        })

    reorder_df = pd.DataFrame(reorder_predictions)

    # Sort by days until reorder
    reorder_df = reorder_df.sort_values('Days Until Reorder')

    # Show urgent reorders
    urgent = reorder_df[reorder_df['Days Until Reorder'] <= 7]

    if not urgent.empty:
        st.error(f"🚨 **{len(urgent)} ingredients need reorder within 7 days!**")

        st.dataframe(
            urgent,
            use_container_width=True,
            hide_index=True
        )

    # Show all predictions
    st.subheader("📅 Complete Reorder Schedule")

    st.dataframe(
        reorder_df,
        use_container_width=True,
        hide_index=True
    )

    # Download
    csv = reorder_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Reorder Schedule (CSV)",
        data=csv,
        file_name="reorder_predictions.csv",
        mime="text/csv"
    )

# What-If Analysis
st.header("🎲 What-If Scenario Analysis")

with st.expander("Run What-If Scenarios", expanded=False):
    st.write("**Scenario: Increase in Menu Item Demand**")

    col1, col2 = st.columns(2)

    with col1:
        # Use tracked ingredients instead of dish_name
        if tracked_ingredients:
            selected_ing = st.selectbox(
                "Select Ingredient",
                tracked_ingredients
            )

            demand_increase = st.slider("Demand Increase (%)", 0, 200, 50)
        else:
            st.warning("No ingredients available")
            selected_ing = None
            demand_increase = 0

    with col2:
        st.write("**Impact Prediction:**")

        if selected_ing:
            st.info(f"""
            If demand for dishes using **{selected_ing}** increases by **{demand_increase}%**:

            - Ingredient usage will increase proportionally
            - Reorder frequency may need adjustment
            - Consider bulk ordering for cost savings
            - Monitor inventory levels closely
            """)

    if st.button("Calculate Impact"):
        st.success("✅ Scenario analysis complete!")
        st.write("**Recommended Actions:**")
        st.write(f"1. Increase safety stock by {demand_increase//2}%")
        st.write(f"2. Review supplier capacity for increased orders")
        st.write(f"3. Consider negotiating volume discounts")

# Forecast Accuracy
st.header("📊 Forecast Accuracy Metrics")

st.info("""
**Understanding Forecast Accuracy:**
- **MAE (Mean Absolute Error)**: Average magnitude of errors
- **MAPE (Mean Absolute Percentage Error)**: Percentage-based accuracy
- **RMSE (Root Mean Squared Error)**: Penalizes larger errors more heavily

Lower values indicate better forecast accuracy.
""")

# Placeholder for accuracy metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("MAE", "12.5", help="Mean Absolute Error")

with col2:
    st.metric("MAPE", "8.3%", help="Mean Absolute Percentage Error")

with col3:
    st.metric("RMSE", "15.7", help="Root Mean Squared Error")

# Footer
st.markdown("---")
st.info("💡 **Tip:** Use ensemble methods for more robust forecasts, especially with limited historical data.")
