"""
Analytics Page
Trend analysis and business intelligence for the 14 tracked ingredients
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
st.set_page_config(page_title="Analytics - Mai Shen Yun", page_icon="📈", layout="wide")

st.title("📈 Advanced Analytics", anchor=False)
st.markdown("---")

# Initialize
loader = DataLoader()
processor = DataProcessor()
analytics = InventoryAnalytics()
viz = InventoryVisualizations()

# Load data
ingredient_df = loader.load_ingredient_data()  # Recipe data
shipment_df = loader.load_shipment_data()  # 14 tracked ingredients

# Load all sheets
all_sheets = loader.load_all_sheets()
monthly_item = all_sheets['item']  # Item-level sales data

# Clean shipment data to get the 14 ingredient names
shipment_clean = processor.clean_shipment_data(shipment_df)
tracked_ingredients = shipment_clean['ingredient'].tolist() if not shipment_clean.empty else []

# Sidebar
with st.sidebar:
    st.header("⚙️ Analysis Settings", anchor=False)

    analysis_type = st.selectbox(
        "Analysis Type",
        ["Ingredient Usage Trends", "Shipment Analysis", "Top/Bottom Performers", "Frequency Analysis"]
    )

    if not monthly_item.empty:
        months = loader.get_available_months()
        selected_months = st.multiselect(
            "Select Months",
            months,
            default=months
        )
    else:
        selected_months = []

    st.markdown("---")
    st.info(f"📊 Analyzing {len(tracked_ingredients)} tracked ingredients")

# Calculate ingredient usage from sales data
def calculate_ingredient_consumption(sales_df, recipe_df, ingredient_list):
    """
    Calculate ingredient consumption based on dish sales and recipes
    Returns: DataFrame with ingredient consumption per month
    """
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

# Ingredient Usage Trends Analysis
if analysis_type == "Ingredient Usage Trends":
    st.header("📊 Ingredient Usage Trends Over Time", anchor=False)

    if not monthly_item.empty and not ingredient_df.empty:
        # Calculate ingredient consumption from sales
        consumption_df = calculate_ingredient_consumption(monthly_item, ingredient_df, tracked_ingredients)

        if not consumption_df.empty:
            # Filter by selected months
            if selected_months and 'month' in consumption_df.columns:
                consumption_df = consumption_df[consumption_df['month'].isin(selected_months)]

            if not consumption_df.empty:
                # Dropdown to select ingredient (showing the 14 tracked ingredients)
                selected_ingredient = st.selectbox(
                    "Select Ingredient to Analyze",
                    tracked_ingredients,
                    help="Choose from the 14 tracked ingredients"
                )

                if selected_ingredient:
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Create trend chart
                        import plotly.graph_objects as go

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=consumption_df['month'].tolist(),
                            y=consumption_df[selected_ingredient].tolist(),
                            mode='lines+markers',
                            name=selected_ingredient,
                            line=dict(color='#FF6B6B', width=3),
                            marker=dict(size=10)
                        ))

                        fig.update_layout(
                            title=f"{selected_ingredient} - Monthly Usage Trend",
                            xaxis_title="Month",
                            yaxis_title="Usage",
                            template="plotly_white",
                            height=500,
                            hovermode='x unified'
                        )

                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.subheader("Statistics", anchor=False)

                        ingredient_data = consumption_df[selected_ingredient]

                        st.metric("Average", f"{ingredient_data.mean():.1f}")
                        st.metric("Max", f"{ingredient_data.max():.1f}")
                        st.metric("Min", f"{ingredient_data.min():.1f}")
                        st.metric("Std Dev", f"{ingredient_data.std():.1f}")

                        # Trend direction
                        if len(ingredient_data) >= 2:
                            trend = "📈 Increasing" if ingredient_data.iloc[-1] > ingredient_data.iloc[0] else "📉 Decreasing"
                            st.write(f"**Trend:** {trend}")

                # Top ingredients by total usage
                st.subheader("🔝 Top Ingredients by Total Usage", anchor=False)

                total_usage = consumption_df[tracked_ingredients].sum().sort_values(ascending=False)

                col1, col2 = st.columns([2, 1])

                with col1:
                    # Create bar chart
                    import plotly.graph_objects as go

                    top_10 = total_usage.head(10)

                    fig = go.Figure(data=[
                        go.Bar(
                            y=top_10.index.tolist(),
                            x=top_10.values.tolist(),
                            orientation='h',
                            marker_color='#FF6B6B',
                            text=[f"{x:.0f}" for x in top_10.values],
                            textposition='auto',
                        )
                    ])

                    fig.update_layout(
                        title="Top 10 Ingredients by Usage",
                        xaxis_title="Total Usage",
                        yaxis_title="Ingredient",
                        template="plotly_white",
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.dataframe(
                        pd.DataFrame({
                            'Ingredient': total_usage.head(10).index,
                            'Total Usage': total_usage.head(10).values
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
        else:
            st.warning("⚠️ Unable to calculate ingredient consumption from sales data")
    else:
        st.warning("⚠️ No sales or recipe data available for analysis")

# Shipment Analysis
elif analysis_type == "Shipment Analysis":
    st.header("📦 Shipment Analysis", anchor=False)

    if not shipment_clean.empty:
        st.subheader("Shipment Frequency Distribution", anchor=False)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Frequency chart
            freq_counts = shipment_clean['frequency'].value_counts()

            import plotly.graph_objects as go

            fig = go.Figure(data=[
                go.Pie(
                    labels=freq_counts.index,
                    values=freq_counts.values,
                    hole=0.4,
                    marker_colors=['#FF6B6B', '#4ECDC4', '#FFE66D']
                )
            ])

            fig.update_layout(
                title="Ingredients by Shipment Frequency",
                template="plotly_white",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("**Breakdown:**")
            for freq, count in freq_counts.items():
                st.metric(freq.title(), f"{count} ingredients")

        # Detailed shipment table
        st.subheader("📋 Detailed Shipment Information", anchor=False)

        display_df = shipment_clean[['ingredient', 'quantity_per_shipment', 'unit', 'num_shipments', 'frequency']].copy()
        display_df.columns = ['Ingredient', 'Qty per Shipment', 'Unit', 'Shipments/Month', 'Frequency']

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

# Top/Bottom Performers
elif analysis_type == "Top/Bottom Performers":
    st.header("🏆 Top & Bottom Performing Ingredients", anchor=False)

    if not monthly_item.empty and not ingredient_df.empty:
        # Calculate ingredient consumption
        consumption_df = calculate_ingredient_consumption(monthly_item, ingredient_df, tracked_ingredients)

        if not consumption_df.empty:
            total_usage = consumption_df[tracked_ingredients].sum().sort_values(ascending=False)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🥇 Top 5 Performers", anchor=False)
                top_5 = total_usage.head(5)

                for i, (ing, usage) in enumerate(top_5.items(), 1):
                    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📦"
                    st.write(f"{emoji} **{ing}**: {usage:.0f} units")

            with col2:
                st.subheader("📉 Bottom 5 Performers", anchor=False)
                bottom_5 = total_usage.tail(5).sort_values(ascending=True)

                for ing, usage in bottom_5.items():
                    st.write(f"• **{ing}**: {usage:.0f} units")

            # Full ranking
            with st.expander("📊 View Complete Ranking"):
                ranking_df = pd.DataFrame({
                    'Rank': range(1, len(total_usage) + 1),
                    'Ingredient': total_usage.index,
                    'Total Usage': total_usage.values
                })

                st.dataframe(
                    ranking_df,
                    use_container_width=True,
                    hide_index=True
                )

# Frequency Analysis
elif analysis_type == "Frequency Analysis":
    st.header("⏱️ Shipment Frequency Analysis", anchor=False)

    if not shipment_clean.empty:
        # Group by frequency
        freq_groups = shipment_clean.groupby('frequency')

        for freq in ['weekly', 'biweekly', 'monthly']:
            if freq in freq_groups.groups:
                group = freq_groups.get_group(freq)

                with st.expander(f"📦 {freq.title()} Shipments ({len(group)} ingredients)", expanded=True):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        # Calculate monthly consumption
                        group_copy = group.copy()
                        group_copy['monthly_quantity'] = group_copy['quantity_per_shipment'] * group_copy['num_shipments']

                        import plotly.graph_objects as go

                        fig = go.Figure(data=[
                            go.Bar(
                                x=group_copy['ingredient'].tolist(),
                                y=group_copy['monthly_quantity'].tolist(),
                                marker_color='#4ECDC4',
                                text=[f"{x:.0f}" for x in group_copy['monthly_quantity']],
                                textposition='auto'
                            )
                        ])

                        fig.update_layout(
                            title=f"Monthly Consumption - {freq.title()} Items",
                            xaxis_title="Ingredient",
                            yaxis_title="Monthly Quantity",
                            template="plotly_white",
                            height=300
                        )

                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.write("**Ingredients:**")
                        for ing in group['ingredient']:
                            st.write(f"• {ing}")

# Export analytics
st.markdown("---")
st.header("📥 Export Analytics", anchor=False)

col1, col2 = st.columns(2)

with col1:
    if not shipment_clean.empty:
        csv = shipment_clean.to_csv(index=False)
        st.download_button(
            label="Download Shipment Data (CSV)",
            data=csv,
            file_name="shipment_analytics.csv",
            mime="text/csv"
        )

with col2:
    if not monthly_item.empty and not ingredient_df.empty:
        consumption_df = calculate_ingredient_consumption(monthly_item, ingredient_df, tracked_ingredients)
        if not consumption_df.empty:
            csv = consumption_df.to_csv(index=False)
            st.download_button(
                label="Download Usage Data (CSV)",
                data=csv,
                file_name="ingredient_usage.csv",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.info("💡 **Tip:** Use these analytics to optimize ordering patterns and reduce costs based on actual consumption of the 14 tracked ingredients.")
