"""
Mai Shen Yun - Inventory Management Dashboard
Main Application Entry Point
"""

import streamlit as st
import pandas as pd
import sys
import base64
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from data_loader import DataLoader
from visualizations import InventoryVisualizations

def get_base64_image(image_path):
    """Read and encode image file to base64 string"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# Page configuration
st.set_page_config(
    page_title="Mai Shen Yun - Inventory Dashboard",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load banner image with base64 encoding
banner_base64 = get_base64_image("assets/banner.png")

# Build CSS with background image or gradient fallback
if banner_base64:
    banner_background = f"background-image: url(data:image/png;base64,{banner_base64}); background-size: cover; background-position: center;"
else:
    # Fallback to gradient if image not found
    banner_background = "background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);"

# Custom CSS
st.markdown(f"""
    <style>
    /* Banner styling */
    .banner-container {{
        position: relative;
        {banner_background}
        padding: 3rem 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }}

    .banner-overlay {{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.3);
        z-index: 0;
    }}

    .banner-content {{
        position: relative;
        z-index: 1;
    }}

    .main-header {{
        font-size: 4rem;
        font-weight: 900;
        color: white;
        text-align: center;
        padding: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        letter-spacing: 2px;
        margin: 0;
    }}

    .sub-header {{
        font-size: 1.5rem;
        color: rgba(255, 255, 255, 0.95);
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 300;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.4);
    }}

    .banner-tagline {{
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        margin-top: 1rem;
        font-style: italic;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.4);
    }}

    .metric-card {{
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }}

    .stAlert {{
        margin-top: 1rem;
    }}
    </style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""

    # Branded Banner Header (with PNG background if available, gradient fallback otherwise)
    st.markdown('''
    <div class="banner-container">
        <div class="banner-overlay"></div>
        <div class="banner-content">
            <h1 class="main-header">🍜 Mai Shen Yun</h1>
            <p class="sub-header">Intelligent Inventory Management Dashboard</p>
            <p class="banner-tagline">Data-Driven Decisions • Real-Time Intelligence • Optimized Operations</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # Initialize data loader
    data_loader = DataLoader()
    viz = InventoryVisualizations()

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/restaurant-menu.png", width=100)
        st.title("Navigation", anchor=False)
        st.info("""
        **Welcome to Mai Shen Yun Dashboard!**

        Use the navigation menu to explore:
        - 📊 Overview - Executive summary
        - 📦 Inventory - Stock management
        - 📈 Analytics - Trend analysis
        - 🔮 Predictions - Forecasting
        - 💰 Cost Analysis - Financial insights
        """)

    # Data summary
    st.header("📋 Data Summary", anchor=False)

    col1, col2, col3, col4 = st.columns(4)

    summary = data_loader.get_data_summary()

    with col1:
        status = "✅ Available" if summary['ingredients_available'] else "❌ Missing"
        st.metric("Recipe Data", status)

    with col2:
        status = "✅ Available" if summary['shipments_available'] else "❌ Missing"
        st.metric("Shipment Data", status)

    with col3:
        st.metric("Available Months", summary['total_months'])

    with col4:
        total_sales_records = sum(summary['total_records'].values())
        st.metric("Sales Records", f"{total_sales_records:,}")

    # Display available months
    if summary['available_months']:
        st.success(f"**Data available for:** {', '.join(summary['available_months'])}")
    else:
        st.warning("No monthly data found")

    # Data sheets info
    st.info(f"""
    📊 **Data Structure**: Each month contains 3 sheets of data
    - Sheet 1 (Group): {summary['total_records']['group']} records
    - Sheet 2 (Category): {summary['total_records']['category']} records
    - Sheet 3 (Item): {summary['total_records']['item']} records
    """)

    # Quick insights section
    st.header("🎯 Quick Insights", anchor=False)

    # Load data for quick insights
    ingredient_df = data_loader.load_ingredient_data()
    shipment_df = data_loader.load_shipment_data()

    if not ingredient_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📋 Recipe Database", anchor=False)
            # Count total ingredients (columns excluding dish_name)
            total_ingredients = len([col for col in ingredient_df.columns if col != 'Item name'])
            st.info(f"Total ingredient types: **{total_ingredients}**")

            if 'Item name' in ingredient_df.columns:
                st.write(f"Total dishes on menu: **{len(ingredient_df)}**")
                st.write("**Sample menu items:**")
                sample_items = ingredient_df['Item name'].head(5).tolist()
                for item in sample_items:
                    st.write(f"- {item}")

        with col2:
            st.subheader("📦 Shipments", anchor=False)
            if not shipment_df.empty:
                st.info(f"Tracked ingredients: **{len(shipment_df)}** (some ingredients may be aggregated)")

                if 'frequency' in shipment_df.columns:
                    freq_counts = shipment_df['frequency'].value_counts()
                    st.write("**Shipment frequencies:**")
                    for freq, count in freq_counts.items():
                        st.write(f"- {freq.title()}: {count} ingredients")

                # Note about mismatch
                st.warning("""
                ℹ️ **Note**: There are 18 ingredients in recipes but 14 tracked shipments.
                Some ingredients may be combined (e.g., "Peas + Carrot") or purchased less frequently.
                """)

    # Getting started guide
    st.header("🚀 Getting Started", anchor=False)

    with st.expander("ℹ️ How to use this dashboard", expanded=False):
        st.markdown("""
        ### Navigation Guide

        1. **📊 Overview Page**
           - View executive summary and KPIs
           - See critical alerts and recommendations
           - Monitor overall inventory health

        2. **📦 Inventory Management**
           - Track real-time inventory levels
           - View stock status for each ingredient
           - Identify items needing reorder

        3. **📈 Analytics**
           - Analyze usage trends over time
           - Discover seasonal patterns
           - View top/bottom performing ingredients

        4. **🔮 Predictions**
           - Forecast future demand
           - Get reorder recommendations
           - Plan for upcoming needs

        5. **💰 Cost Analysis**
           - Monitor spending patterns
           - Identify cost-saving opportunities
           - Optimize inventory value

        ### Tips
        - Use filters to focus on specific ingredients or time periods
        - Hover over charts for detailed information
        - Download data for further analysis
        - Check alerts regularly for actionable insights
        """)

    # System information
    st.header("ℹ️ System Information", anchor=False)

    with st.expander("View system details"):
        st.write("**Dashboard Version:** 1.0.0")
        st.write("**Framework:** Streamlit")
        st.write("**Data Source:** Local files (Excel & CSV)")
        st.write("**Last Updated:** 2025-11-08")

        # Display file information
        st.write("**Loaded Files:**")
        st.json({
            "Recipe Data": "MSY Data - Ingredient.csv (17 dishes, 18 ingredients)",
            "Shipment Data": "MSY Data - Shipment.csv (14 ingredients)",
            "Monthly Sales Data": f"{summary['total_months']} months ({', '.join(summary['available_months'])})",
            "Sheets per Month": 3
        })

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Mai Shen Yun Inventory Management System | Built with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
