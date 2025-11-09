"""
Interactive Menu Planning System
Strategic menu optimization and ingredient impact analysis
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class MenuPlanner:
    """Advanced menu planning and optimization system"""

    def __init__(self):
        self.current_menu = []
        self.planned_menu = []
        self.ingredient_mapping = {
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

    def calculate_ingredient_requirements(self, recipe_df: pd.DataFrame,
                                         dish_list: List[str],
                                         expected_sales: Dict[str, int] = None) -> pd.DataFrame:
        """
        Calculate total ingredient requirements for a given menu

        Args:
            recipe_df: DataFrame with recipe data
            dish_list: List of dish names to include in menu
            expected_sales: Dictionary of dish -> expected monthly sales

        Returns:
            DataFrame with ingredient requirements
        """
        if recipe_df.empty or not dish_list:
            return pd.DataFrame()

        # Default expected sales to 100 per dish if not provided
        if expected_sales is None:
            expected_sales = {dish: 100 for dish in dish_list}

        # Initialize requirements dictionary
        requirements = {}
        for tracked_ing in set(self.ingredient_mapping.values()):
            requirements[tracked_ing] = 0

        # Calculate requirements for each dish
        for dish in dish_list:
            # Find matching recipe
            recipe_match = recipe_df[recipe_df['dish_name'].str.contains(dish.split()[0], case=False, na=False)]

            if not recipe_match.empty:
                recipe = recipe_match.iloc[0]
                quantity = expected_sales.get(dish, 100)

                # Add ingredient usage
                for recipe_col, tracked_ing in self.ingredient_mapping.items():
                    if recipe_col in recipe.index and pd.notna(recipe[recipe_col]):
                        usage = recipe[recipe_col] * quantity
                        requirements[tracked_ing] += usage

        # Convert to DataFrame
        requirements_df = pd.DataFrame([
            {'ingredient': ing, 'monthly_requirement': req}
            for ing, req in requirements.items()
            if req > 0
        ]).sort_values('monthly_requirement', ascending=False)

        return requirements_df

    def compare_menus(self, recipe_df: pd.DataFrame,
                     current_dishes: List[str],
                     planned_dishes: List[str],
                     current_sales: Dict[str, int] = None,
                     planned_sales: Dict[str, int] = None) -> Dict:
        """
        Compare two menu configurations

        Args:
            recipe_df: Recipe DataFrame
            current_dishes: Current menu dishes
            planned_dishes: Planned menu dishes
            current_sales: Expected sales for current menu
            planned_sales: Expected sales for planned menu

        Returns:
            Comparison dictionary with changes
        """
        current_req = self.calculate_ingredient_requirements(recipe_df, current_dishes, current_sales)
        planned_req = self.calculate_ingredient_requirements(recipe_df, planned_dishes, planned_sales)

        # Merge requirements
        comparison = pd.merge(
            current_req,
            planned_req,
            on='ingredient',
            how='outer',
            suffixes=('_current', '_planned')
        ).fillna(0)

        # Calculate changes
        comparison['change'] = comparison['monthly_requirement_planned'] - comparison['monthly_requirement_current']
        comparison['change_pct'] = np.where(
            comparison['monthly_requirement_current'] > 0,
            (comparison['change'] / comparison['monthly_requirement_current']) * 100,
            100
        )

        return {
            'comparison_df': comparison,
            'dishes_added': list(set(planned_dishes) - set(current_dishes)),
            'dishes_removed': list(set(current_dishes) - set(planned_dishes)),
            'dishes_unchanged': list(set(current_dishes) & set(planned_dishes))
        }

    def check_ingredient_availability(self, requirements_df: pd.DataFrame,
                                     inventory_df: pd.DataFrame) -> Dict:
        """
        Check if current inventory can support menu requirements

        Args:
            requirements_df: Required ingredients DataFrame
            inventory_df: Current inventory DataFrame

        Returns:
            Availability analysis
        """
        if requirements_df.empty or inventory_df.empty:
            return {'status': 'unknown', 'issues': []}

        issues = []
        warnings = []

        for _, req_row in requirements_df.iterrows():
            ingredient = req_row['ingredient']
            required = req_row['monthly_requirement']

            # Find in inventory
            inv_match = inventory_df[inventory_df['ingredient'] == ingredient]

            if not inv_match.empty:
                inv_row = inv_match.iloc[0]
                current_stock = inv_row.get('current_stock', 0)
                daily_usage = inv_row.get('avg_daily_usage', 0)

                # Assume monthly = 30 days
                available_monthly = current_stock + (daily_usage * 30)

                if available_monthly < required:
                    shortage = required - available_monthly
                    issues.append({
                        'ingredient': ingredient,
                        'required': required,
                        'available': available_monthly,
                        'shortage': shortage,
                        'severity': 'critical' if shortage > required * 0.5 else 'moderate'
                    })
                elif available_monthly < required * 1.2:  # Less than 20% buffer
                    warnings.append({
                        'ingredient': ingredient,
                        'required': required,
                        'available': available_monthly,
                        'buffer': available_monthly - required
                    })

        status = 'critical' if issues else 'warning' if warnings else 'ok'

        return {
            'status': status,
            'issues': issues,
            'warnings': warnings,
            'total_issues': len(issues),
            'total_warnings': len(warnings)
        }

    def optimize_menu_for_ingredients(self, recipe_df: pd.DataFrame,
                                     inventory_df: pd.DataFrame,
                                     dish_candidates: List[str],
                                     max_dishes: int = 20) -> Dict:
        """
        Optimize menu based on ingredient availability

        Args:
            recipe_df: Recipe DataFrame
            inventory_df: Inventory DataFrame
            dish_candidates: Candidate dishes to choose from
            max_dishes: Maximum dishes to include

        Returns:
            Optimized menu recommendation
        """
        if recipe_df.empty or inventory_df.empty:
            return {'optimized_menu': [], 'score': 0, 'reason': 'Insufficient data'}

        dish_scores = []

        for dish in dish_candidates:
            # Calculate ingredient requirements for this dish
            req = self.calculate_ingredient_requirements(recipe_df, [dish], {dish: 100})

            if req.empty:
                continue

            # Score based on ingredient availability
            availability_score = 0
            total_ingredients = 0

            for _, ing_row in req.iterrows():
                ingredient = ing_row['ingredient']
                required = ing_row['monthly_requirement']

                inv_match = inventory_df[inventory_df['ingredient'] == ingredient]

                if not inv_match.empty:
                    current_stock = inv_match.iloc[0].get('current_stock', 0)
                    # Higher score if we have good stock
                    availability_score += min(current_stock / (required + 1), 10)
                    total_ingredients += 1

            avg_score = availability_score / max(total_ingredients, 1)

            dish_scores.append({
                'dish': dish,
                'score': avg_score,
                'num_ingredients': total_ingredients
            })

        # Sort by score and select top dishes
        dish_scores_sorted = sorted(dish_scores, key=lambda x: x['score'], reverse=True)
        optimized_menu = [d['dish'] for d in dish_scores_sorted[:max_dishes]]

        return {
            'optimized_menu': optimized_menu,
            'dish_scores': dish_scores_sorted[:max_dishes],
            'total_candidates': len(dish_candidates),
            'selected_count': len(optimized_menu)
        }

    def suggest_dish_substitutions(self, recipe_df: pd.DataFrame,
                                  inventory_df: pd.DataFrame,
                                  dish_to_replace: str,
                                  candidate_dishes: List[str]) -> List[Dict]:
        """
        Suggest alternative dishes that use available ingredients

        Args:
            recipe_df: Recipe DataFrame
            inventory_df: Inventory DataFrame
            dish_to_replace: Dish to find substitution for
            candidate_dishes: List of potential substitutes

        Returns:
            List of recommended substitutions
        """
        recommendations = []

        # Get requirements for dish to replace
        original_req = self.calculate_ingredient_requirements(recipe_df, [dish_to_replace], {dish_to_replace: 100})

        for candidate in candidate_dishes:
            if candidate == dish_to_replace:
                continue

            candidate_req = self.calculate_ingredient_requirements(recipe_df, [candidate], {candidate: 100})

            if candidate_req.empty:
                continue

            # Calculate ingredient overlap
            original_ings = set(original_req['ingredient'].tolist())
            candidate_ings = set(candidate_req['ingredient'].tolist())

            overlap = len(original_ings & candidate_ings)
            similarity = overlap / max(len(original_ings | candidate_ings), 1)

            # Check availability
            availability = self.check_ingredient_availability(candidate_req, inventory_df)

            recommendations.append({
                'dish': candidate,
                'similarity': similarity,
                'availability_status': availability['status'],
                'shared_ingredients': overlap,
                'total_ingredients': len(candidate_ings),
                'issues': len(availability['issues'])
            })

        # Sort by similarity and availability
        recommendations.sort(key=lambda x: (x['availability_status'] == 'ok', x['similarity']), reverse=True)

        return recommendations[:5]  # Top 5 recommendations

    def calculate_menu_cost(self, recipe_df: pd.DataFrame,
                          dish_list: List[str],
                          expected_sales: Dict[str, int],
                          ingredient_costs: Dict[str, float]) -> Dict:
        """
        Calculate total cost for menu

        Args:
            recipe_df: Recipe DataFrame
            dish_list: List of dishes
            expected_sales: Expected sales per dish
            ingredient_costs: Cost per unit per ingredient

        Returns:
            Cost analysis
        """
        requirements = self.calculate_ingredient_requirements(recipe_df, dish_list, expected_sales)

        if requirements.empty:
            return {'total_cost': 0, 'breakdown': []}

        breakdown = []
        total_cost = 0

        for _, row in requirements.iterrows():
            ingredient = row['ingredient']
            quantity = row['monthly_requirement']
            unit_cost = ingredient_costs.get(ingredient, 5.0)  # Default $5/unit
            cost = quantity * unit_cost

            breakdown.append({
                'ingredient': ingredient,
                'quantity': quantity,
                'unit_cost': unit_cost,
                'total_cost': cost
            })

            total_cost += cost

        return {
            'total_cost': total_cost,
            'breakdown': sorted(breakdown, key=lambda x: x['total_cost'], reverse=True),
            'avg_cost_per_dish': total_cost / len(dish_list) if dish_list else 0
        }

    def generate_seasonal_menu(self, recipe_df: pd.DataFrame,
                              season: str,
                              base_dishes: List[str],
                              seasonal_preferences: Dict[str, List[str]] = None) -> Dict:
        """
        Generate seasonal menu recommendations

        Args:
            recipe_df: Recipe DataFrame
            season: Season name (spring, summer, fall, winter)
            base_dishes: Base menu dishes
            seasonal_preferences: Ingredient preferences by season

        Returns:
            Seasonal menu recommendation
        """
        if seasonal_preferences is None:
            seasonal_preferences = {
                'spring': ['Green Onion', 'Cilantro', 'Egg'],
                'summer': ['Green Onion', 'Cilantro', 'Chicken'],
                'fall': ['Pork', 'Rice', 'Bokchoy'],
                'winter': ['Beef', 'Rice Noodles', 'Ramen']
            }

        preferred_ingredients = seasonal_preferences.get(season.lower(), [])

        # Score dishes based on seasonal ingredients
        dish_scores = []

        for dish in base_dishes:
            req = self.calculate_ingredient_requirements(recipe_df, [dish], {dish: 100})

            if req.empty:
                continue

            # Calculate seasonal score
            seasonal_score = 0
            for _, ing_row in req.iterrows():
                if ing_row['ingredient'] in preferred_ingredients:
                    seasonal_score += 1

            dish_scores.append({
                'dish': dish,
                'seasonal_score': seasonal_score,
                'seasonal_fit': 'high' if seasonal_score >= 2 else 'medium' if seasonal_score >= 1 else 'low'
            })

        # Sort by seasonal fit
        dish_scores_sorted = sorted(dish_scores, key=lambda x: x['seasonal_score'], reverse=True)

        return {
            'season': season,
            'recommended_dishes': [d['dish'] for d in dish_scores_sorted],
            'dish_scores': dish_scores_sorted,
            'preferred_ingredients': preferred_ingredients
        }
