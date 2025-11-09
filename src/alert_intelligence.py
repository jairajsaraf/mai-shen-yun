"""
Intelligent Alert System
Proactive monitoring and alerting for inventory management
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class AlertIntelligence:
    """Advanced alert detection and prioritization system"""

    # Alert priority levels
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    # Alert categories
    STOCKOUT = "stockout_risk"
    OVERSTOCK = "overstock"
    PRICE_ANOMALY = "price_anomaly"
    CONSUMPTION_SPIKE = "consumption_spike"
    CONSUMPTION_DROP = "consumption_drop"
    REORDER_TIMING = "reorder_timing"
    TREND_CHANGE = "trend_change"

    def __init__(self):
        self.alerts = []

    def detect_stockout_risk(self, inventory_df: pd.DataFrame,
                            timeframes: List[int] = [3, 7, 14]) -> List[Dict]:
        """
        Predict stock-out risk for multiple timeframes

        Args:
            inventory_df: DataFrame with current_stock, avg_daily_usage columns
            timeframes: List of days to forecast (e.g., [3, 7, 14])

        Returns:
            List of alert dictionaries
        """
        alerts = []

        if inventory_df.empty:
            return alerts

        for _, row in inventory_df.iterrows():
            ingredient = row.get('ingredient', 'Unknown')
            current_stock = row.get('current_stock', 0)
            daily_usage = row.get('avg_daily_usage', 0)

            if daily_usage <= 0:
                continue

            days_remaining = current_stock / daily_usage

            for timeframe in timeframes:
                if days_remaining <= timeframe:
                    # Determine priority based on urgency
                    if days_remaining <= 1:
                        priority = self.CRITICAL
                        action = f"🚨 ORDER IMMEDIATELY - Less than 1 day of stock remaining"
                    elif days_remaining <= 3:
                        priority = self.CRITICAL
                        action = f"⚠️ Order today - Stock will run out in {days_remaining:.1f} days"
                    elif days_remaining <= 7:
                        priority = self.HIGH
                        action = f"📋 Plan order this week - {days_remaining:.1f} days remaining"
                    else:
                        priority = self.MEDIUM
                        action = f"📅 Monitor closely - {days_remaining:.1f} days of stock"

                    alerts.append({
                        'ingredient': ingredient,
                        'category': self.STOCKOUT,
                        'priority': priority,
                        'title': f"Stock-out Risk: {ingredient}",
                        'message': f"Current stock will last {days_remaining:.1f} days at current usage rate ({daily_usage:.1f} units/day)",
                        'timeframe': f"{timeframe}-day forecast",
                        'action': action,
                        'current_value': current_stock,
                        'threshold': daily_usage * timeframe,
                        'days_remaining': days_remaining,
                        'timestamp': datetime.now()
                    })
                    break  # Only create one alert per ingredient

        return alerts

    def detect_overstock(self, inventory_df: pd.DataFrame,
                        threshold_days: int = 60) -> List[Dict]:
        """
        Detect items with excessive inventory

        Args:
            inventory_df: DataFrame with current_stock, avg_daily_usage
            threshold_days: Days of stock considered excessive

        Returns:
            List of alert dictionaries
        """
        alerts = []

        if inventory_df.empty:
            return alerts

        for _, row in inventory_df.iterrows():
            ingredient = row.get('ingredient', 'Unknown')
            current_stock = row.get('current_stock', 0)
            daily_usage = row.get('avg_daily_usage', 0)

            if daily_usage <= 0:
                continue

            days_of_stock = current_stock / daily_usage

            if days_of_stock > threshold_days:
                # Calculate capital tied up (simplified)
                excess_stock = current_stock - (daily_usage * 30)  # 30 days is optimal

                priority = self.HIGH if days_of_stock > 90 else self.MEDIUM

                alerts.append({
                    'ingredient': ingredient,
                    'category': self.OVERSTOCK,
                    'priority': priority,
                    'title': f"Overstock Alert: {ingredient}",
                    'message': f"Current stock will last {days_of_stock:.1f} days (exceeds {threshold_days} day threshold)",
                    'action': f"💰 Consider reducing next order by {excess_stock:.1f} units to optimize cash flow",
                    'current_value': current_stock,
                    'optimal_value': daily_usage * 30,
                    'excess_amount': excess_stock,
                    'days_of_stock': days_of_stock,
                    'timestamp': datetime.now()
                })

        return alerts

    def detect_consumption_anomalies(self, consumption_df: pd.DataFrame,
                                     std_threshold: float = 2.0) -> List[Dict]:
        """
        Detect unusual spikes or drops in consumption patterns

        Args:
            consumption_df: DataFrame with monthly consumption data
            std_threshold: Number of standard deviations for anomaly

        Returns:
            List of alert dictionaries
        """
        alerts = []

        if consumption_df.empty or len(consumption_df) < 3:
            return alerts

        # Get ingredient columns (excluding 'month')
        ingredient_cols = [col for col in consumption_df.columns if col != 'month']

        for ingredient in ingredient_cols:
            if ingredient not in consumption_df.columns:
                continue

            usage = consumption_df[ingredient].values

            if len(usage) < 3:
                continue

            # Calculate statistics
            mean = np.mean(usage)
            std = np.std(usage)

            if std == 0:
                continue

            # Check most recent value
            latest = usage[-1]
            z_score = (latest - mean) / std

            # Spike detection
            if z_score > std_threshold:
                percent_increase = ((latest - mean) / mean) * 100

                priority = self.CRITICAL if z_score > 3 else self.HIGH

                alerts.append({
                    'ingredient': ingredient,
                    'category': self.CONSUMPTION_SPIKE,
                    'priority': priority,
                    'title': f"Consumption Spike: {ingredient}",
                    'message': f"Usage increased {percent_increase:.1f}% above normal ({latest:.1f} vs avg {mean:.1f})",
                    'action': f"🔍 Investigate cause: menu changes, seasonal demand, or data error. Consider increasing safety stock.",
                    'current_value': latest,
                    'average_value': mean,
                    'z_score': z_score,
                    'timestamp': datetime.now()
                })

            # Drop detection
            elif z_score < -std_threshold:
                percent_decrease = ((mean - latest) / mean) * 100

                priority = self.MEDIUM

                alerts.append({
                    'ingredient': ingredient,
                    'category': self.CONSUMPTION_DROP,
                    'priority': priority,
                    'title': f"Consumption Drop: {ingredient}",
                    'message': f"Usage decreased {percent_decrease:.1f}% below normal ({latest:.1f} vs avg {mean:.1f})",
                    'action': f"📊 Check if menu items using this ingredient are still popular. Adjust ordering accordingly.",
                    'current_value': latest,
                    'average_value': mean,
                    'z_score': abs(z_score),
                    'timestamp': datetime.now()
                })

        return alerts

    def detect_optimal_reorder_timing(self, inventory_df: pd.DataFrame) -> List[Dict]:
        """
        Smart reorder timing alerts based on lead time and buffer

        Args:
            inventory_df: DataFrame with inventory data

        Returns:
            List of alert dictionaries
        """
        alerts = []

        if inventory_df.empty:
            return alerts

        for _, row in inventory_df.iterrows():
            ingredient = row.get('ingredient', 'Unknown')
            current_stock = row.get('current_stock', 0)
            daily_usage = row.get('avg_daily_usage', 0)
            lead_time_days = row.get('lead_time_days', 7)
            reorder_point = row.get('reorder_point', 0)

            if daily_usage <= 0:
                continue

            days_remaining = current_stock / daily_usage

            # Optimal reorder window: between reorder point and reorder point + buffer
            buffer_days = 3
            optimal_window_start = lead_time_days + buffer_days
            optimal_window_end = lead_time_days + buffer_days + 7

            if optimal_window_start <= days_remaining <= optimal_window_end:
                # We're in the optimal reorder window
                priority = self.MEDIUM

                alerts.append({
                    'ingredient': ingredient,
                    'category': self.REORDER_TIMING,
                    'priority': priority,
                    'title': f"Optimal Reorder Window: {ingredient}",
                    'message': f"Perfect time to reorder - {days_remaining:.1f} days remaining (lead time: {lead_time_days} days)",
                    'action': f"✅ Place order now to maintain optimal inventory levels",
                    'current_value': current_stock,
                    'reorder_point': reorder_point,
                    'days_remaining': days_remaining,
                    'lead_time': lead_time_days,
                    'timestamp': datetime.now()
                })

        return alerts

    def detect_price_anomalies(self, cost_df: pd.DataFrame,
                               threshold_pct: float = 20.0) -> List[Dict]:
        """
        Detect unusual price changes (if historical cost data available)

        Args:
            cost_df: DataFrame with ingredient costs over time
            threshold_pct: Percentage change threshold

        Returns:
            List of alert dictionaries
        """
        alerts = []

        # This is a placeholder - would need historical price data
        # For now, we'll simulate some price anomalies

        return alerts

    def generate_all_alerts(self, inventory_df: pd.DataFrame,
                           consumption_df: pd.DataFrame = None) -> List[Dict]:
        """
        Run all alert detection algorithms

        Args:
            inventory_df: Current inventory DataFrame
            consumption_df: Historical consumption DataFrame (optional)

        Returns:
            Comprehensive list of all alerts, sorted by priority
        """
        all_alerts = []

        # Stock-out risk alerts
        all_alerts.extend(self.detect_stockout_risk(inventory_df))

        # Overstock alerts
        all_alerts.extend(self.detect_overstock(inventory_df))

        # Optimal reorder timing
        all_alerts.extend(self.detect_optimal_reorder_timing(inventory_df))

        # Consumption anomalies (if data available)
        if consumption_df is not None and not consumption_df.empty:
            all_alerts.extend(self.detect_consumption_anomalies(consumption_df))

        # Sort by priority
        priority_order = {
            self.CRITICAL: 0,
            self.HIGH: 1,
            self.MEDIUM: 2,
            self.LOW: 3,
            self.INFO: 4
        }

        all_alerts.sort(key=lambda x: priority_order.get(x['priority'], 999))

        self.alerts = all_alerts
        return all_alerts

    def get_alert_summary(self, alerts: List[Dict] = None) -> Dict:
        """
        Get summary statistics for alerts

        Args:
            alerts: List of alerts (uses self.alerts if not provided)

        Returns:
            Dictionary with alert counts by priority and category
        """
        if alerts is None:
            alerts = self.alerts

        summary = {
            'total': len(alerts),
            'by_priority': {
                self.CRITICAL: 0,
                self.HIGH: 0,
                self.MEDIUM: 0,
                self.LOW: 0,
                self.INFO: 0
            },
            'by_category': {}
        }

        for alert in alerts:
            priority = alert.get('priority', self.INFO)
            category = alert.get('category', 'unknown')

            if priority in summary['by_priority']:
                summary['by_priority'][priority] += 1

            if category not in summary['by_category']:
                summary['by_category'][category] = 0
            summary['by_category'][category] += 1

        return summary

    def get_critical_alerts(self, alerts: List[Dict] = None) -> List[Dict]:
        """Get only critical and high priority alerts"""
        if alerts is None:
            alerts = self.alerts

        return [a for a in alerts if a.get('priority') in [self.CRITICAL, self.HIGH]]

    def get_actionable_insights(self, alerts: List[Dict] = None) -> List[str]:
        """
        Generate actionable insights from alerts

        Returns:
            List of recommended actions
        """
        if alerts is None:
            alerts = self.alerts

        insights = []

        # Group alerts by category
        stockout_alerts = [a for a in alerts if a.get('category') == self.STOCKOUT and a.get('priority') in [self.CRITICAL, self.HIGH]]
        overstock_alerts = [a for a in alerts if a.get('category') == self.OVERSTOCK]
        spike_alerts = [a for a in alerts if a.get('category') == self.CONSUMPTION_SPIKE]

        if stockout_alerts:
            ingredients = [a['ingredient'] for a in stockout_alerts[:3]]
            insights.append(f"🚨 URGENT: Order {len(stockout_alerts)} critical ingredients today: {', '.join(ingredients)}")

        if overstock_alerts:
            total_excess = sum(a.get('excess_amount', 0) for a in overstock_alerts)
            insights.append(f"💰 Reduce overstock to free up ${total_excess * 10:.0f} in working capital")

        if spike_alerts:
            insights.append(f"📊 {len(spike_alerts)} ingredients showing unusual consumption patterns - review menu changes")

        if not insights:
            insights.append("✅ All inventory levels are optimal - no immediate action required")

        return insights
