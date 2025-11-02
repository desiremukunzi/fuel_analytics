#!/usr/bin/env python3
"""
Jalikoi Daily Customer Monitoring System
=========================================

Run this script daily to monitor customer health and trigger interventions.

Usage:
    python3 daily_monitoring.py [--alert-threshold 60] [--export-csv]

Features:
- Real-time churn detection
- High-value customer alerts
- Automated segment updates
- Performance dashboard
- Export action items for team
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import json


class DailyMonitor:
    """Daily monitoring and alerting system"""
    
    def __init__(self, data_path, alert_threshold=60):
        self.data_path = data_path
        self.alert_threshold = alert_threshold
        self.alerts = []
        self.today = datetime.now()
        
    def load_data(self):
        """Load and prepare payment data"""
        self.df = pd.read_csv(self.data_path)
        self.df['created_at'] = pd.to_datetime(self.df['created_at'], format='%d/%m/%Y %H:%M')
        self.df_success = self.df[self.df['payment_status'] == 200].copy()
        
    def calculate_customer_health(self):
        """Calculate real-time health scores for all customers"""
        
        # Get customer metrics
        customers = self.df_success.groupby('motorcyclist_id').agg({
            'id': 'count',
            'amount': ['sum', 'mean'],
            'created_at': ['min', 'max'],
            'station_id': 'nunique'
        }).reset_index()
        
        customers.columns = ['motorcyclist_id', 'txn_count', 'total_spent', 
                            'avg_txn', 'first_date', 'last_date', 'stations_used']
        
        # Calculate health indicators
        customers['days_since_last'] = (self.today - customers['last_date']).dt.total_seconds() / (24 * 3600)
        customers['customer_age_days'] = (customers['last_date'] - customers['first_date']).dt.total_seconds() / (24 * 3600)
        customers['customer_age_days'] = customers['customer_age_days'].replace(0, 0.1)
        customers['frequency'] = customers['txn_count'] / customers['customer_age_days']
        
        # Health score (0-100, higher = better)
        recency_score = 100 - np.clip((customers['days_since_last'] / 7) * 40, 0, 100)
        frequency_score = np.clip(customers['frequency'] * 20, 0, 50)
        value_score = (customers['total_spent'].rank(pct=True) * 50)
        
        customers['health_score'] = (recency_score + frequency_score + value_score) / 2
        customers['health_status'] = customers['health_score'].apply(
            lambda x: 'Critical' if x < 30 else ('Warning' if x < 50 else ('Good' if x < 70 else 'Excellent'))
        )
        
        # Calculate CLV
        customers['projected_clv_6m'] = customers['frequency'] * 180 * customers['avg_txn']
        
        self.customers = customers
        return customers
    
    def detect_critical_issues(self):
        """Identify critical customer issues requiring immediate attention"""
        
        critical_customers = self.customers[self.customers['health_status'] == 'Critical']
        warning_customers = self.customers[self.customers['health_status'] == 'Warning']
        
        # High-value customers at risk
        high_value_at_risk = self.customers[
            (self.customers['projected_clv_6m'] > self.customers['projected_clv_6m'].quantile(0.7)) &
            (self.customers['health_status'].isin(['Critical', 'Warning']))
        ]
        
        # Generate alerts
        if len(critical_customers) > 0:
            self.alerts.append({
                'level': 'CRITICAL',
                'type': 'CHURN_RISK',
                'count': len(critical_customers),
                'message': f'{len(critical_customers)} customers in CRITICAL health status',
                'action': 'Immediate personal outreach required',
                'customers': critical_customers['motorcyclist_id'].tolist()
            })
        
        if len(high_value_at_risk) > 0:
            self.alerts.append({
                'level': 'HIGH',
                'type': 'HIGH_VALUE_RISK',
                'count': len(high_value_at_risk),
                'message': f'{len(high_value_at_risk)} high-value customers showing warning signs',
                'action': 'Launch retention campaign',
                'potential_revenue_loss': high_value_at_risk['projected_clv_6m'].sum(),
                'customers': high_value_at_risk['motorcyclist_id'].tolist()
            })
        
        # Customers who haven't transacted in unusual time
        avg_days_between = self.customers['days_since_last'].median()
        unusual_absence = self.customers[
            self.customers['days_since_last'] > (avg_days_between * 2)
        ]
        
        if len(unusual_absence) > 0:
            self.alerts.append({
                'level': 'MEDIUM',
                'type': 'UNUSUAL_ABSENCE',
                'count': len(unusual_absence),
                'message': f'{len(unusual_absence)} customers absent longer than usual',
                'action': 'Send re-engagement campaign',
                'customers': unusual_absence['motorcyclist_id'].tolist()
            })
        
    def analyze_recent_trends(self):
        """Analyze last 24 hours and last 7 days"""
        
        yesterday = self.today - timedelta(days=1)
        last_week = self.today - timedelta(days=7)
        
        # Yesterday's performance
        yesterday_txns = self.df_success[self.df_success['created_at'] >= yesterday]
        yesterday_revenue = yesterday_txns['amount'].sum()
        yesterday_count = len(yesterday_txns)
        
        # Last week average
        last_week_txns = self.df_success[self.df_success['created_at'] >= last_week]
        daily_avg_revenue = last_week_txns.groupby(last_week_txns['created_at'].dt.date)['amount'].sum().mean()
        daily_avg_count = last_week_txns.groupby(last_week_txns['created_at'].dt.date)['id'].count().mean()
        
        # Trends
        revenue_trend = ((yesterday_revenue / daily_avg_revenue) - 1) * 100 if daily_avg_revenue > 0 else 0
        volume_trend = ((yesterday_count / daily_avg_count) - 1) * 100 if daily_avg_count > 0 else 0
        
        self.trends = {
            'yesterday_revenue': yesterday_revenue,
            'yesterday_count': yesterday_count,
            'revenue_trend': revenue_trend,
            'volume_trend': volume_trend,
            'avg_daily_revenue_7d': daily_avg_revenue,
            'avg_daily_count_7d': daily_avg_count
        }
        
        # Alert if significant drop
        if revenue_trend < -20:
            self.alerts.append({
                'level': 'HIGH',
                'type': 'REVENUE_DROP',
                'message': f'Revenue down {abs(revenue_trend):.1f}% vs 7-day average',
                'action': 'Investigate cause: station issues, payment problems, or external factors',
                'yesterday_revenue': yesterday_revenue,
                'expected_revenue': daily_avg_revenue
            })
        
        if volume_trend < -20:
            self.alerts.append({
                'level': 'HIGH',
                'type': 'VOLUME_DROP',
                'message': f'Transaction volume down {abs(volume_trend):.1f}% vs 7-day average',
                'action': 'Check system availability and customer engagement',
                'yesterday_count': yesterday_count,
                'expected_count': daily_avg_count
            })
    
    def generate_priority_actions(self):
        """Generate prioritized action list for the day"""
        
        actions = []
        
        # Sort alerts by priority
        alert_priority = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4}
        sorted_alerts = sorted(self.alerts, key=lambda x: alert_priority.get(x['level'], 99))
        
        for idx, alert in enumerate(sorted_alerts, 1):
            actions.append({
                'priority': idx,
                'level': alert['level'],
                'type': alert['type'],
                'action': alert['action'],
                'details': alert.get('message', ''),
                'affected_customers': alert.get('count', 0)
            })
        
        # Add proactive actions
        excellent_customers = self.customers[self.customers['health_status'] == 'Excellent']
        if len(excellent_customers) > 0:
            actions.append({
                'priority': len(actions) + 1,
                'level': 'PROACTIVE',
                'type': 'REWARD_LOYALTY',
                'action': 'Thank and reward excellent customers',
                'details': f'{len(excellent_customers)} customers in excellent health',
                'affected_customers': len(excellent_customers)
            })
        
        return actions
    
    def print_dashboard(self):
        """Print daily monitoring dashboard to console"""
        
        print("\n" + "="*80)
        print(f"JALIKOI DAILY MONITORING DASHBOARD - {self.today.strftime('%B %d, %Y')}")
        print("="*80)
        
        # Overall health
        print("\n📊 OVERALL HEALTH SUMMARY")
        print("-" * 80)
        health_dist = self.customers['health_status'].value_counts()
        total = len(self.customers)
        for status in ['Excellent', 'Good', 'Warning', 'Critical']:
            count = health_dist.get(status, 0)
            pct = (count / total) * 100 if total > 0 else 0
            emoji = {'Excellent': '🟢', 'Good': '🔵', 'Warning': '🟡', 'Critical': '🔴'}
            print(f"{emoji.get(status, '⚪')} {status:12s}: {count:3d} customers ({pct:5.1f}%)")
        
        # Recent trends
        print("\n📈 RECENT PERFORMANCE (Last 24 Hours vs 7-Day Average)")
        print("-" * 80)
        print(f"Revenue:      KES {self.trends['yesterday_revenue']:>12,.2f} "
              f"({self.trends['revenue_trend']:+.1f}%)")
        print(f"Transactions: {self.trends['yesterday_count']:>16d} "
              f"({self.trends['volume_trend']:+.1f}%)")
        
        # Alerts
        if self.alerts:
            print("\n🚨 ALERTS REQUIRING ATTENTION")
            print("-" * 80)
            for alert in self.alerts:
                level_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}
                print(f"\n{level_emoji.get(alert['level'], '⚪')} {alert['level']} - {alert['type']}")
                print(f"   {alert['message']}")
                print(f"   Action: {alert['action']}")
                if 'customers' in alert and len(alert['customers']) <= 5:
                    print(f"   Affected: {', '.join(map(str, alert['customers']))}")
                elif 'customers' in alert:
                    print(f"   Affected: {len(alert['customers'])} customers")
        else:
            print("\n✅ NO CRITICAL ALERTS")
            print("-" * 80)
            print("All systems operating normally. Continue monitoring.")
        
        # Top performers
        print("\n🏆 TOP 5 CUSTOMERS (By 6-Month CLV)")
        print("-" * 80)
        top_5 = self.customers.nlargest(5, 'projected_clv_6m')[
            ['motorcyclist_id', 'projected_clv_6m', 'health_status', 'days_since_last']
        ]
        print(top_5.to_string(index=False))
        
        print("\n" + "="*80)
    
    def export_action_items(self, filename='daily_action_items.csv'):
        """Export action items for team"""
        
        actions = self.generate_priority_actions()
        actions_df = pd.DataFrame(actions)
        
        output_path = f'outputs/{filename}'
        actions_df.to_csv(output_path, index=False)
        
        print(f"\n✅ Action items exported to: {output_path}")
        return output_path
    
    def export_customer_list(self, filename='customer_health_report.csv'):
        """Export detailed customer health report"""
        
        output_path = f'outputs/{filename}'
        self.customers.to_csv(output_path, index=False)
        
        print(f"✅ Customer health report exported to: {output_path}")
        return output_path
    
    def run_daily_check(self, export_csv=False):
        """Run complete daily monitoring routine"""
        
        self.load_data()
        self.calculate_customer_health()
        self.detect_critical_issues()
        self.analyze_recent_trends()
        self.print_dashboard()
        
        if export_csv:
            self.export_action_items()
            self.export_customer_list()
        
        return {
            'alerts': self.alerts,
            'customer_health': self.customers.to_dict('records'),
            'trends': self.trends
        }


def main():
    """Main execution"""
    
    parser = argparse.ArgumentParser(description='Jalikoi Daily Customer Monitoring')
    parser.add_argument('--data', default='uploads/payments.csv',
                       help='Path to payment data CSV')
    parser.add_argument('--alert-threshold', type=int, default=60,
                       help='Churn risk threshold (0-100)')
    parser.add_argument('--export-csv', action='store_true',
                       help='Export CSV reports')
    parser.add_argument('--json-output', action='store_true',
                       help='Output results as JSON')
    
    args = parser.parse_args()
    
    # Run monitoring
    monitor = DailyMonitor(args.data, args.alert_threshold)
    results = monitor.run_daily_check(export_csv=args.export_csv)
    
    # JSON output for integration with other systems
    if args.json_output:
        # Convert NumPy types to native Python types for JSON serialization
        def convert_to_json_serializable(obj):
            """Convert NumPy/Pandas types to native Python types"""
            if isinstance(obj, dict):
                return {k: convert_to_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_json_serializable(item) for item in obj]
            elif hasattr(obj, 'item'):  # NumPy types
                return obj.item()
            elif hasattr(obj, 'tolist'):  # NumPy arrays
                return obj.tolist()
            elif pd.isna(obj):  # Handle NaN values
                return None
            else:
                return obj
        
        json_output = {
            'timestamp': datetime.now().isoformat(),
            'alerts': convert_to_json_serializable(results['alerts']),
            'summary': {
                'total_customers': int(len(results['customer_health'])),
                'critical_customers': int(sum(1 for c in results['customer_health'] 
                                        if c['health_status'] == 'Critical')),
                'yesterday_revenue': float(results['trends']['yesterday_revenue']),
                'revenue_trend': float(results['trends']['revenue_trend'])
            }
        }
        
        with open('outputs/monitoring_results.json', 'w') as f:
            json.dump(json_output, f, indent=2)
        
        print("\n✅ JSON results saved to: outputs/monitoring_results.json")


if __name__ == "__main__":
    main()