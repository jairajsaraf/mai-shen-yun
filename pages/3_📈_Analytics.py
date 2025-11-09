"""
Analytics Page
Trend analysis and business intelligence
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

# Hide anchor links
st.markdown("""
    <style>
    .stHeadingContainer a {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Advanced Analytics")
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
    st.header("⚙️ Analysis Settings")

    analysis_type = st.selectbox(
        "Analysis Type",
        ["Usage Trends", "Seasonal Patterns", "ABC Classification", "Correlation Analysis"]
    )

    if not monthly_df.empty:
        months = loader.get_available_months()
        selected_months = st.multiselect(
            "Select Months",
            months,
            default=months
        )
    else:
        selected_months = []

    st.markdown("---")
    st.info("📊 Select different analysis types to explore your data")

# Usage Trends Analysis
if analysis_type == "Usage Trends":
    st.header("📊 Usage Trends Over Time")

    if not monthly_df.empty:
        # Process monthly data
        monthly_clean = processor.process_monthly_sales(monthly_df)

        # Filter by selected months
        if selected_months and 'month' in monthly_clean.columns:
            monthly_clean = monthly_clean[monthly_clean['month'].isin(selected_months)]

        if not monthly_clean.empty:
            # Get numeric columns (ingredients)
            numeric_cols = monthly_clean.select_dtypes(include=[np.number]).columns.tolist()

            if numeric_cols:
                # Aggregate by month
                if 'month' in monthly_clean.columns:
                    monthly_agg = monthly_clean.groupby('month')[numeric_cols].sum()

                    # Select ingredient to analyze
                    selected_ingredient = st.selectbox("Select Ingredient", numeric_cols)

                    if selected_ingredient:
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            # Create trend chart
                            fig = viz.plot_usage_trends(monthly_agg, selected_ingredient)
                            st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            st.subheader("Statistics")

                            ingredient_data = monthly_agg[selected_ingredient]

                            st.metric("Average", f"{ingredient_data.mean():.1f}")
                            st.metric("Max", f"{ingredient_data.max():.1f}")
                            st.metric("Min", f"{ingredient_data.min():.1f}")
                            st.metric("Std Dev", f"{ingredient_data.std():.1f}")

                            # Trend direction
                            if len(ingredient_data) >= 2:
                                trend = "📈 Increasing" if ingredient_data.iloc[-1] > ingredient_data.iloc[0] else "📉 Decreasing"
                                st.write(f"**Trend:** {trend}")

                    # Top ingredients by total usage
                    st.subheader("🔝 Top Ingredients by Usage")

                    total_usage = monthly_agg.sum().sort_values(ascending=False).head(10)

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        # Create bar chart
                        fig_top = viz.plot_top_ingredients(
                            pd.DataFrame({'ingredient': total_usage.index, 'usage': total_usage.values}),
                            n=10,
                            metric='usage'
                        )
                        st.plotly_chart(fig_top, use_container_width=True)

                    with col2:
                        st.dataframe(
                            pd.DataFrame({'Ingredient': total_usage.index, 'Total Usage': total_usage.values}),
                            use_container_width=True,
                            hide_index=True
                        )

    else:
        st.warning("⚠️ No monthly data available for trend analysis")

# Seasonal Patterns
elif analysis_type == "Seasonal Patterns":
    st.header("🌤️ Seasonal Pattern Analysis")

    if not monthly_df.empty:
        monthly_clean = processor.process_monthly_sales(monthly_df)

        if not monthly_clean.empty and 'month' in monthly_clean.columns:
            # Detect seasonal patterns
            seasonal_data = processor.detect_seasonal_patterns(monthly_clean)

            if not seasonal_data.empty:
                st.success(f"✅ Analyzed {len(seasonal_data)} months of data")

                # Create heatmap
                numeric_cols = seasonal_data.select_dtypes(include=[np.number]).columns.tolist()

                if len(numeric_cols) > 0:
                    # Limit to top ingredients for readability
                    top_ingredients = seasonal_data[numeric_cols].sum().nlargest(15).index.tolist()
                    heatmap_data = seasonal_data[top_ingredients]

                    fig = viz.plot_heatmap(heatmap_data, title="Seasonal Usage Patterns (Top 15 Ingredients)")
                    st.plotly_chart(fig, use_container_width=True)

                    # Insights
                    st.subheader("📊 Seasonal Insights")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Peak Usage Months:**")
                        for ingredient in top_ingredients[:5]:
                            peak_month = seasonal_data[ingredient].idxmax()
                            peak_value = seasonal_data[ingredient].max()
                            st.write(f"- **{ingredient}**: {peak_month} ({peak_value:.1f})")

                    with col2:
                        st.write("**Lowest Usage Months:**")
                        for ingredient in top_ingredients[:5]:
                            low_month = seasonal_data[ingredient].idxmin()
                            low_value = seasonal_data[ingredient].min()
                            st.write(f"- **{ingredient}**: {low_month} ({low_value:.1f})")

    else:
        st.warning("⚠️ No monthly data available for seasonal analysis")

# ABC Classification
elif analysis_type == "ABC Classification":
    st.header("🎯 ABC Classification Analysis")

    st.info("""
    **ABC Analysis** classifies inventory items based on their importance:
    - **A items**: Top 20% of items (80% of value) - Tight control and accurate records
    - **B items**: Next 30% of items (15% of value) - Moderate control
    - **C items**: Remaining 50% of items (5% of value) - Simple controls
    """)

    if not monthly_df.empty:
        monthly_clean = processor.process_monthly_sales(monthly_df)

        if not monthly_clean.empty:
            # Calculate total usage per ingredient
            numeric_cols = monthly_clean.select_dtypes(include=[np.number]).columns.tolist()

            if len(numeric_cols) > 0:
                total_usage = monthly_clean[numeric_cols].sum()

                # Create dataframe
                abc_df = pd.DataFrame({
                    'ingredient': total_usage.index,
                    'total_usage': total_usage.values
                })

                # Perform ABC classification
                abc_classified = analytics.identify_abc_classification(abc_df, 'total_usage')

                # Display results
                col1, col2 = st.columns([2, 1])

                with col1:
                    fig = viz.plot_abc_analysis(abc_classified)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("Classification Summary")

                    for cls in ['A', 'B', 'C']:
                        count = len(abc_classified[abc_classified['abc_class'] == cls])
                        pct = (count / len(abc_classified)) * 100
                        st.metric(f"Class {cls}", f"{count} items ({pct:.1f}%)")

                # Show items by class
                st.subheader("📋 Items by Class")

                tab1, tab2, tab3 = st.tabs(["Class A", "Class B", "Class C"])

                with tab1:
                    a_items = abc_classified[abc_classified['abc_class'] == 'A']
                    st.write("**High-value items requiring tight control:**")
                    st.dataframe(
                        a_items[['ingredient', 'total_usage', 'cumulative_percentage']],
                        use_container_width=True,
                        hide_index=True
                    )

                with tab2:
                    b_items = abc_classified[abc_classified['abc_class'] == 'B']
                    st.write("**Moderate-value items:**")
                    st.dataframe(
                        b_items[['ingredient', 'total_usage', 'cumulative_percentage']],
                        use_container_width=True,
                        hide_index=True
                    )

                with tab3:
                    c_items = abc_classified[abc_classified['abc_class'] == 'C']
                    st.write("**Low-value items with simple controls:**")
                    st.dataframe(
                        c_items[['ingredient', 'total_usage', 'cumulative_percentage']],
                        use_container_width=True,
                        hide_index=True
                    )

    else:
        st.warning("⚠️ No data available for ABC classification")

# Correlation Analysis
elif analysis_type == "Correlation Analysis":
    st.header("🔗 Correlation Analysis")

    st.info("Identify relationships between different ingredients to optimize procurement and identify usage patterns.")

    if not monthly_df.empty:
        monthly_clean = processor.process_monthly_sales(monthly_df)

        if not monthly_clean.empty:
            numeric_cols = monthly_clean.select_dtypes(include=[np.number]).columns.tolist()

            if len(numeric_cols) > 5:
                # Limit to top ingredients
                top_n = st.slider("Number of ingredients to analyze", 5, min(20, len(numeric_cols)), 10)

                total_usage = monthly_clean[numeric_cols].sum().nlargest(top_n)
                top_ingredients = total_usage.index.tolist()

                # Calculate correlation
                corr_data = monthly_clean[top_ingredients]

                if len(corr_data) > 1:
                    fig = viz.plot_correlation_matrix(corr_data)
                    st.plotly_chart(fig, use_container_width=True)

                    # Find strong correlations
                    st.subheader("🔍 Strong Correlations")

                    corr_matrix = corr_data.corr()

                    # Find pairs with high correlation (excluding diagonal)
                    strong_corr = []
                    for i in range(len(corr_matrix.columns)):
                        for j in range(i+1, len(corr_matrix.columns)):
                            corr_value = corr_matrix.iloc[i, j]
                            if abs(corr_value) > 0.7:  # Strong correlation threshold
                                strong_corr.append({
                                    'Ingredient 1': corr_matrix.columns[i],
                                    'Ingredient 2': corr_matrix.columns[j],
                                    'Correlation': f"{corr_value:.2f}"
                                })

                    if strong_corr:
                        st.dataframe(
                            pd.DataFrame(strong_corr),
                            use_container_width=True,
                            hide_index=True
                        )
                        st.info("💡 Ingredients with high positive correlation are often used together and can be ordered in sync.")
                    else:
                        st.write("No strong correlations found (threshold: |0.7|)")

    else:
        st.warning("⚠️ No data available for correlation analysis")

# Export analytics
st.markdown("---")
st.header("📥 Export Analytics")

col1, col2 = st.columns(2)

with col1:
    if not monthly_df.empty:
        csv = monthly_df.to_csv(index=False)
        st.download_button(
            label="Download Monthly Data (CSV)",
            data=csv,
            file_name="monthly_analytics.csv",
            mime="text/csv"
        )

with col2:
    if not shipment_df.empty:
        csv = shipment_df.to_csv(index=False)
        st.download_button(
            label="Download Shipment Data (CSV)",
            data=csv,
            file_name="shipment_analytics.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.info("💡 **Tip:** Use analytics insights to optimize ordering patterns and reduce costs.")
