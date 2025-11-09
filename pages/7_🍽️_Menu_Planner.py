"""
Interactive Menu Planning Tool
Strategic menu design with real-time ingredient impact analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_loader import DataLoader
from data_processor import DataProcessor
from menu_planner import MenuPlanner
from visualizations import InventoryVisualizations

# Page config
st.set_page_config(page_title="Menu Planner - Mai Shen Yun", page_icon="🍽️", layout="wide")

st.title("🍽️ Interactive Menu Planning Tool", anchor=False)
st.markdown("### Design Your Menu • See Ingredient Impact • Optimize Costs")
st.markdown("---")

# Initialize
loader = DataLoader()
processor = DataProcessor()
planner = MenuPlanner()
viz = InventoryVisualizations()

# Load data
ingredient_df = loader.load_ingredient_data()
shipment_df = loader.load_shipment_data()
all_sheets = loader.load_all_sheets()
monthly_item = all_sheets['item']

# Clean recipe data
recipe_clean = processor.clean_ingredient_data(ingredient_df)

# Get available dishes
available_dishes = recipe_clean['dish_name'].tolist() if not recipe_clean.empty else []

# Prepare inventory data
shipment_clean = processor.clean_shipment_data(shipment_df)
if not shipment_clean.empty:
    np.random.seed(42)
    shipment_clean['current_stock'] = shipment_clean['quantity_per_shipment'] * np.random.uniform(0.5, 3.0, len(shipment_clean))
    shipment_clean['avg_daily_usage'] = shipment_clean.apply(
        lambda row: row['quantity_per_shipment'] * row['num_shipments'] / 30,
        axis=1
    )

# Initialize session state
if 'current_menu' not in st.session_state:
    # Start with top 10 most popular dishes
    if not monthly_item.empty and 'Item Name' in monthly_item.columns:
        monthly_item['Count'] = pd.to_numeric(monthly_item['Count'], errors='coerce').fillna(0)
        top_dishes = monthly_item.groupby('Item Name')['Count'].sum().sort_values(ascending=False).head(10)
        st.session_state.current_menu = [dish for dish in top_dishes.index if dish in available_dishes]
    else:
        st.session_state.current_menu = available_dishes[:10] if available_dishes else []

if 'planned_menu' not in st.session_state:
    st.session_state.planned_menu = st.session_state.current_menu.copy()

# Initialize counter for unique keys (to clear multiselects after operations)
if 'operation_counter' not in st.session_state:
    st.session_state.operation_counter = 0

# Sidebar - Planning Mode
with st.sidebar:
    st.header("🎯 Planning Mode", anchor=False)

    planning_mode = st.selectbox(
        "Select Mode",
        ["Menu Builder", "Seasonal Planning", "Cost Optimization", "What-If Analysis"]
    )

    st.markdown("---")

    st.subheader("Expected Monthly Sales", anchor=False)
    default_sales = st.slider("Default Sales per Dish", 50, 500, 100, 25)

    st.markdown("---")

    st.info(f"""
    **Current Status**
    - 📋 Menu Items: {len(st.session_state.planned_menu)}
    - 🍽️ Available Dishes: {len(available_dishes)}
    """)

# Main Content - Menu Builder Mode
if planning_mode == "Menu Builder":
    st.header("🍽️ Menu Builder", anchor=False)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Current Menu", anchor=False)

        if st.session_state.current_menu:
            st.info(f"**{len(st.session_state.current_menu)} dishes** on current menu")

            # Display current menu in a nice format
            for i, dish in enumerate(st.session_state.current_menu[:15], 1):
                st.write(f"{i}. {dish}")

            if len(st.session_state.current_menu) > 15:
                st.caption(f"...and {len(st.session_state.current_menu) - 15} more")
        else:
            st.warning("No dishes in current menu")

    with col2:
        st.subheader("Planned Menu", anchor=False)

        st.info(f"**{len(st.session_state.planned_menu)} dishes** in planned menu")

        # Display planned menu
        with st.expander("📋 View Planned Menu Items", expanded=True):
            if st.session_state.planned_menu:
                for i, dish in enumerate(st.session_state.planned_menu[:15], 1):
                    st.write(f"{i}. {dish}")
                if len(st.session_state.planned_menu) > 15:
                    st.caption(f"...and {len(st.session_state.planned_menu) - 15} more")
            else:
                st.write("No dishes in planned menu")

        st.write("---")

        # Add dishes
        available_to_add = [d for d in available_dishes if d not in st.session_state.planned_menu]

        if available_to_add:
            dishes_to_add = st.multiselect(
                "➕ Add Dishes",
                available_to_add,
                key=f"dishes_to_add_{st.session_state.operation_counter}"
            )

            if st.button("➕ Add Selected Dishes", disabled=len(dishes_to_add)==0):
                if dishes_to_add:
                    st.session_state.planned_menu.extend(dishes_to_add)
                    st.session_state.operation_counter += 1
                    st.success(f"✅ Added {len(dishes_to_add)} dishes!")
                    st.rerun()

        # Remove dishes
        if st.session_state.planned_menu:
            st.write("---")
            dishes_to_remove = st.multiselect(
                "➖ Remove Dishes",
                st.session_state.planned_menu,
                key=f"dishes_to_remove_{st.session_state.operation_counter}"
            )

            if st.button("➖ Remove Selected Dishes", disabled=len(dishes_to_remove)==0):
                if dishes_to_remove:
                    for dish in dishes_to_remove:
                        st.session_state.planned_menu.remove(dish)
                    st.session_state.operation_counter += 1
                    st.success(f"✅ Removed {len(dishes_to_remove)} dishes!")
                    st.rerun()

        st.write("---")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Reset to Current"):
                st.session_state.planned_menu = st.session_state.current_menu.copy()
                st.session_state.operation_counter += 1
                st.success("↺ Reset to current menu!")
                st.rerun()

        with col_b:
            if st.button("✅ Apply Changes"):
                st.session_state.current_menu = st.session_state.planned_menu.copy()
                st.session_state.operation_counter += 1
                st.success("✅ Menu updated!")
                st.rerun()

    st.markdown("---")

    # Impact Analysis
    st.header("📊 Ingredient Impact Analysis", anchor=False)

    if st.session_state.planned_menu and not recipe_clean.empty:
        # Calculate requirements
        current_sales = {dish: default_sales for dish in st.session_state.current_menu}
        planned_sales = {dish: default_sales for dish in st.session_state.planned_menu}

        comparison = planner.compare_menus(
            recipe_clean,
            st.session_state.current_menu,
            st.session_state.planned_menu,
            current_sales,
            planned_sales
        )

        # Display changes
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Dishes Added", len(comparison['dishes_added']))
            if comparison['dishes_added']:
                with st.expander("View Added Dishes"):
                    for dish in comparison['dishes_added']:
                        st.write(f"➕ {dish}")

        with col2:
            st.metric("Dishes Removed", len(comparison['dishes_removed']))
            if comparison['dishes_removed']:
                with st.expander("View Removed Dishes"):
                    for dish in comparison['dishes_removed']:
                        st.write(f"➖ {dish}")

        with col3:
            st.metric("Dishes Unchanged", len(comparison['dishes_unchanged']))

        st.markdown("---")

        # Ingredient changes
        st.subheader("Ingredient Requirement Changes", anchor=False)

        comp_df = comparison['comparison_df']

        if not comp_df.empty:
            # Show all changes, sorted by absolute change
            all_changes = comp_df[abs(comp_df['change']) > 0.1].sort_values('change', key=abs, ascending=False)

            if not all_changes.empty:
                st.success(f"📊 Showing changes for {len(all_changes)} ingredients")

                # Create visualization for top 10 changes
                top_changes = all_changes.head(10)

                fig = go.Figure()

                fig.add_trace(go.Bar(
                    name='Current Menu',
                    y=top_changes['ingredient'],
                    x=top_changes['monthly_requirement_current'],
                    orientation='h',
                    marker_color='#4ECDC4',
                    text=top_changes['monthly_requirement_current'].round(0),
                    textposition='inside'
                ))

                fig.add_trace(go.Bar(
                    name='Planned Menu',
                    y=top_changes['ingredient'],
                    x=top_changes['monthly_requirement_planned'],
                    orientation='h',
                    marker_color='#FF6B6B',
                    text=top_changes['monthly_requirement_planned'].round(0),
                    textposition='inside'
                ))

                fig.update_layout(
                    title="Top 10 Ingredient Requirement Changes: Current vs Planned",
                    xaxis_title="Monthly Requirement (units)",
                    yaxis_title="Ingredient",
                    barmode='group',
                    template="plotly_white",
                    height=400,
                    showlegend=True
                )

                st.plotly_chart(fig, use_container_width=True)

                # Quick summary
                increases = all_changes[all_changes['change'] > 0]
                decreases = all_changes[all_changes['change'] < 0]

                col_summary1, col_summary2 = st.columns(2)
                with col_summary1:
                    if not increases.empty:
                        st.info(f"📈 **Increases:** {len(increases)} ingredients need more")
                        for _, row in increases.head(3).iterrows():
                            st.write(f"  • {row['ingredient']}: +{row['change']:.0f} units (+{row['change_pct']:.0f}%)")

                with col_summary2:
                    if not decreases.empty:
                        st.info(f"📉 **Decreases:** {len(decreases)} ingredients need less")
                        for _, row in decreases.head(3).iterrows():
                            st.write(f"  • {row['ingredient']}: {row['change']:.0f} units ({row['change_pct']:.0f}%)")

                # Detailed table
                with st.expander("📋 View Complete Ingredient Changes"):
                    display_df = all_changes[['ingredient', 'monthly_requirement_current', 'monthly_requirement_planned', 'change', 'change_pct']].copy()
                    display_df.columns = ['Ingredient', 'Current Need', 'Planned Need', 'Change', 'Change %']

                    # Format columns
                    display_df['Current Need'] = display_df['Current Need'].round(1)
                    display_df['Planned Need'] = display_df['Planned Need'].round(1)
                    display_df['Change'] = display_df['Change'].round(1)
                    display_df['Change %'] = display_df['Change %'].round(1)

                    st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ No ingredient changes detected - menus are identical")

        # Availability check
        st.markdown("---")
        st.subheader("🔍 Inventory Availability Check", anchor=False)

        if not shipment_clean.empty:
            planned_req = planner.calculate_ingredient_requirements(recipe_clean, st.session_state.planned_menu, planned_sales)

            if not planned_req.empty:
                availability = planner.check_ingredient_availability(planned_req, shipment_clean)

                col1, col2, col3 = st.columns(3)

                with col1:
                    if availability['status'] == 'ok':
                        st.success(f"✅ All ingredients available")
                    elif availability['status'] == 'warning':
                        st.warning(f"⚠️ {availability['total_warnings']} warnings")
                    else:
                        st.error(f"🚨 {availability['total_issues']} critical issues")

                with col2:
                    st.metric("Critical Issues", availability['total_issues'])

                with col3:
                    st.metric("Warnings", availability['total_warnings'])

                # Display issues
                if availability['issues']:
                    st.error("**Critical Ingredient Shortages:**")
                    for issue in availability['issues']:
                        st.write(f"- **{issue['ingredient']}**: Short {issue['shortage']:.1f} units (need {issue['required']:.1f}, have {issue['available']:.1f})")

                if availability['warnings']:
                    with st.expander("⚠️ View Warnings"):
                        for warning in availability['warnings']:
                            st.write(f"- **{warning['ingredient']}**: Limited buffer ({warning['buffer']:.1f} units)")

    else:
        st.warning("Add dishes to your planned menu to see impact analysis")

# Seasonal Planning Mode
elif planning_mode == "Seasonal Planning":
    st.header("🌸 Seasonal Menu Planning", anchor=False)

    season = st.selectbox(
        "Select Season",
        ["Spring", "Summer", "Fall", "Winter"]
    )

    if st.button("🌟 Generate Seasonal Recommendations"):
        seasonal_menu = planner.generate_seasonal_menu(
            recipe_clean,
            season,
            available_dishes
        )

        st.success(f"✅ Generated {season} menu recommendations!")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(f"🍽️ Recommended {season} Menu", anchor=False)

            recommended = seasonal_menu['recommended_dishes'][:15]

            for i, dish in enumerate(recommended, 1):
                score_info = next((d for d in seasonal_menu['dish_scores'] if d['dish'] == dish), None)
                if score_info:
                    fit = score_info['seasonal_fit']
                    icon = "🌟" if fit == 'high' else "⭐" if fit == 'medium' else "✨"
                    st.write(f"{i}. {icon} {dish} ({fit} seasonal fit)")

            if st.button(f"✅ Apply {season} Menu"):
                st.session_state.planned_menu = recommended
                st.success(f"{season} menu applied!")
                st.rerun()

        with col2:
            st.subheader("Seasonal Ingredients", anchor=False)
            st.info(f"**Preferred for {season}:**")
            for ing in seasonal_menu['preferred_ingredients']:
                st.write(f"🌱 {ing}")

# Cost Optimization Mode
elif planning_mode == "Cost Optimization":
    st.header("💰 Cost Optimization", anchor=False)

    # Simulate ingredient costs
    np.random.seed(42)
    ingredient_costs = {ing: np.random.uniform(3, 15) for ing in shipment_clean['ingredient'].tolist()}

    if st.session_state.planned_menu:
        planned_sales = {dish: default_sales for dish in st.session_state.planned_menu}

        cost_analysis = planner.calculate_menu_cost(
            recipe_clean,
            st.session_state.planned_menu,
            planned_sales,
            ingredient_costs
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Monthly Cost", f"${cost_analysis['total_cost']:,.2f}")

        with col2:
            st.metric("Avg Cost per Dish", f"${cost_analysis['avg_cost_per_dish']:,.2f}")

        with col3:
            st.metric("Menu Items", len(st.session_state.planned_menu))

        st.markdown("---")

        # Cost breakdown
        st.subheader("💵 Ingredient Cost Breakdown", anchor=False)

        breakdown = pd.DataFrame(cost_analysis['breakdown']).head(10)

        fig = go.Figure(data=[
            go.Bar(
                y=breakdown['ingredient'],
                x=breakdown['total_cost'],
                orientation='h',
                marker_color='#FF6B6B',
                text=breakdown['total_cost'].apply(lambda x: f"${x:.0f}"),
                textposition='auto'
            )
        ])

        fig.update_layout(
            title="Top 10 Most Expensive Ingredients",
            xaxis_title="Monthly Cost ($)",
            yaxis_title="Ingredient",
            template="plotly_white",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 View Complete Cost Breakdown"):
            full_breakdown = pd.DataFrame(cost_analysis['breakdown'])
            full_breakdown['total_cost'] = full_breakdown['total_cost'].round(2)
            full_breakdown['unit_cost'] = full_breakdown['unit_cost'].round(2)
            full_breakdown['quantity'] = full_breakdown['quantity'].round(1)
            st.dataframe(full_breakdown, use_container_width=True, hide_index=True)

    else:
        st.warning("Add dishes to your menu to see cost analysis")

# What-If Analysis Mode
elif planning_mode == "What-If Analysis":
    st.header("🎲 What-If Scenario Analysis", anchor=False)

    st.info("""
    **Test different scenarios:**
    - See what happens if a dish becomes more popular
    - Analyze the impact of removing underperforming items
    - Plan for special events or promotions
    """)

    scenario_type = st.selectbox(
        "Select Scenario",
        ["Popularity Surge", "Dish Removal", "Special Event"]
    )

    if scenario_type == "Popularity Surge":
        st.subheader("📈 Popularity Surge Scenario", anchor=False)

        if st.session_state.planned_menu:
            surge_dish = st.selectbox("Select Dish", st.session_state.planned_menu)
            surge_multiplier = st.slider("Sales Increase Multiplier", 1.0, 5.0, 2.0, 0.5)

            st.write(f"**Scenario:** {surge_dish} sales increase by {(surge_multiplier - 1) * 100:.0f}%")

            # Calculate impact
            base_sales = {dish: default_sales for dish in st.session_state.planned_menu}
            surge_sales = base_sales.copy()
            surge_sales[surge_dish] = int(default_sales * surge_multiplier)

            base_req = planner.calculate_ingredient_requirements(recipe_clean, st.session_state.planned_menu, base_sales)
            surge_req = planner.calculate_ingredient_requirements(recipe_clean, st.session_state.planned_menu, surge_sales)

            # Merge and compare
            comparison = pd.merge(base_req, surge_req, on='ingredient', suffixes=('_base', '_surge'))
            comparison['increase'] = comparison['monthly_requirement_surge'] - comparison['monthly_requirement_base']
            comparison['increase_pct'] = (comparison['increase'] / comparison['monthly_requirement_base']) * 100

            significant = comparison[comparison['increase_pct'] > 5].sort_values('increase', ascending=False)

            if not significant.empty:
                st.warning(f"⚠️ **Impact on {len(significant)} ingredients:**")

                for _, row in significant.head(5).iterrows():
                    st.write(f"- **{row['ingredient']}**: +{row['increase']:.1f} units (+{row['increase_pct']:.1f}%)")

                # Check availability
                availability = planner.check_ingredient_availability(surge_req, shipment_clean)

                if availability['issues']:
                    st.error(f"🚨 **{len(availability['issues'])} ingredients would run short!**")
                    for issue in availability['issues']:
                        st.write(f"- {issue['ingredient']}: Short by {issue['shortage']:.1f} units")
                else:
                    st.success("✅ Current inventory can support this surge!")

    elif scenario_type == "Dish Removal":
        st.subheader("➖ Dish Removal Scenario", anchor=False)

        if st.session_state.planned_menu:
            dishes_to_remove = st.multiselect(
                "Select Dishes to Remove",
                st.session_state.planned_menu
            )

            if dishes_to_remove:
                remaining_dishes = [d for d in st.session_state.planned_menu if d not in dishes_to_remove]

                base_sales = {dish: default_sales for dish in st.session_state.planned_menu}
                new_sales = {dish: default_sales for dish in remaining_dishes}

                base_req = planner.calculate_ingredient_requirements(recipe_clean, st.session_state.planned_menu, base_sales)
                new_req = planner.calculate_ingredient_requirements(recipe_clean, remaining_dishes, new_sales)

                st.success(f"✅ Removing {len(dishes_to_remove)} dishes")

                # Calculate freed capacity
                freed = base_req[~base_req['ingredient'].isin(new_req['ingredient'])]

                if not freed.empty:
                    st.info(f"💡 **Ingredients no longer needed:** {', '.join(freed['ingredient'].tolist())}")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Menu Size", f"{len(remaining_dishes)} dishes")
                    st.metric("Removed", len(dishes_to_remove))

                with col2:
                    st.metric("Unique Ingredients", len(new_req))
                    st.metric("Simplified By", len(freed))

    else:  # Special Event
        st.subheader("🎉 Special Event Planning", anchor=False)

        event_name = st.text_input("Event Name", "Holiday Special")
        expected_increase = st.slider("Expected Overall Sales Increase (%)", 0, 200, 50, 10)

        if st.button("📊 Calculate Event Impact"):
            multiplier = 1 + (expected_increase / 100)

            base_sales = {dish: default_sales for dish in st.session_state.planned_menu}
            event_sales = {dish: int(default_sales * multiplier) for dish in st.session_state.planned_menu}

            base_req = planner.calculate_ingredient_requirements(recipe_clean, st.session_state.planned_menu, base_sales)
            event_req = planner.calculate_ingredient_requirements(recipe_clean, st.session_state.planned_menu, event_sales)

            st.success(f"✅ {event_name} - {expected_increase}% increase")

            # Total increase
            total_increase = event_req['monthly_requirement'].sum() - base_req['monthly_requirement'].sum()

            st.metric("Additional Ingredients Needed", f"{total_increase:.0f} total units")

            # Top impacted ingredients
            comparison = pd.merge(base_req, event_req, on='ingredient', suffixes=('_base', '_event'))
            comparison['increase'] = comparison['monthly_requirement_event'] - comparison['monthly_requirement_base']

            top_impact = comparison.nlargest(5, 'increase')

            st.write("**Most Impacted Ingredients:**")
            for _, row in top_impact.iterrows():
                st.write(f"- {row['ingredient']}: +{row['increase']:.1f} units")

# Footer
st.markdown("---")
st.info("💡 **Tip:** Use the Menu Planner to design your menu strategically, considering ingredient availability and costs. All changes are temporary until you click 'Apply Changes'.")

# Export functionality
if st.session_state.planned_menu:
    st.subheader("📥 Export Menu Plan", anchor=False)

    col1, col2 = st.columns(2)

    with col1:
        planned_sales = {dish: default_sales for dish in st.session_state.planned_menu}
        requirements = planner.calculate_ingredient_requirements(recipe_clean, st.session_state.planned_menu, planned_sales)

        if not requirements.empty:
            csv = requirements.to_csv(index=False)
            st.download_button(
                label="📄 Download Ingredient Requirements (CSV)",
                data=csv,
                file_name="menu_ingredient_requirements.csv",
                mime="text/csv"
            )

    with col2:
        menu_df = pd.DataFrame({'Dish Name': st.session_state.planned_menu})
        menu_csv = menu_df.to_csv(index=False)
        st.download_button(
            label="📋 Download Menu List (CSV)",
            data=menu_csv,
            file_name="planned_menu.csv",
            mime="text/csv"
        )
