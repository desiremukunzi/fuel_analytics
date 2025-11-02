#!/usr/bin/env python3
"""
Jalikoi Customer Analytics with Visualizations (RWF Currency)
==============================================================
Enhanced version with beautiful charts and graphs
Currency: Rwandan Francs (RWF)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Set style for beautiful charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11

# Color palette
COLORS = {
    'primary': '#2E86AB',
    'success': '#06D6A0',
    'warning': '#F77F00',
    'danger': '#D62828',
    'info': '#023E8A',
    'excellent': '#06D6A0',
    'good': '#2E86AB',
    'warning': '#F77F00',
    'critical': '#D62828'
}

class JalikoiAnalyticsVisualized:
    """Enhanced analytics with visualizations and RWF currency"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.currency = "RWF"
        self.df = pd.read_csv(data_path)
        self._preprocess_data()
        self._engineer_features()
        
    def _preprocess_data(self):
        """Clean and prepare data"""
        self.df['created_at'] = pd.to_datetime(self.df['created_at'], format='%d/%m/%Y %H:%M')
        self.df['date'] = self.df['created_at'].dt.date
        self.df['hour'] = self.df['created_at'].dt.hour
        self.df['day_of_week'] = self.df['created_at'].dt.dayofweek
        self.df['day_name'] = self.df['created_at'].dt.day_name()
        
        self.df_success = self.df[self.df['payment_status'] == 200].copy()
        self.reference_date = self.df['created_at'].max()
        
    def _engineer_features(self):
        """Create customer-level features"""
        customer_metrics = self.df_success.groupby('motorcyclist_id').agg({
            'id': 'count',
            'amount': ['sum', 'mean', 'std', 'min', 'max'],
            'liter': ['sum', 'mean'],
            'station_id': lambda x: x.nunique(),
            'created_at': ['min', 'max'],
            'payment_method_id': 'first',
            'source': lambda x: (x == 'APP').sum() / len(x)
        }).reset_index()
        
        customer_metrics.columns = [
            'motorcyclist_id', 'transaction_count', 'total_spent', 'avg_transaction',
            'std_transaction', 'min_transaction', 'max_transaction',
            'total_liters', 'avg_liters', 'station_diversity', 
            'first_transaction', 'last_transaction', 'payment_method', 'app_usage_rate'
        ]
        
        customer_metrics['recency_days'] = (
            self.reference_date - customer_metrics['last_transaction']
        ).dt.total_seconds() / (24 * 3600)
        
        customer_metrics['customer_age_days'] = (
            customer_metrics['last_transaction'] - customer_metrics['first_transaction']
        ).dt.total_seconds() / (24 * 3600)
        customer_metrics['customer_age_days'] = customer_metrics['customer_age_days'].replace(0, 0.1)
        
        customer_metrics['frequency'] = (
            customer_metrics['transaction_count'] / customer_metrics['customer_age_days']
        )
        
        failure_rates = self.df.groupby('motorcyclist_id').agg({
            'payment_status': lambda x: (x == 500).sum() / len(x)
        }).reset_index()
        failure_rates.columns = ['motorcyclist_id', 'failure_rate']
        
        customer_metrics = customer_metrics.merge(failure_rates, on='motorcyclist_id', how='left')
        customer_metrics['failure_rate'] = customer_metrics['failure_rate'].fillna(0)
        
        self.customer_metrics = customer_metrics
        self._calculate_all_scores()
        
    def _calculate_all_scores(self):
        """Calculate CLV, churn risk, and segments"""
        # CLV
        days_ahead = 180
        self.customer_metrics['predicted_transactions'] = (
            self.customer_metrics['frequency'] * days_ahead
        )
        self.customer_metrics['predicted_clv_6m'] = (
            self.customer_metrics['predicted_transactions'] * 
            self.customer_metrics['avg_transaction']
        )
        churn_factor = np.clip(1 - (self.customer_metrics['recency_days'] / 30), 0.1, 1.0)
        self.customer_metrics['predicted_clv_6m_adjusted'] = (
            self.customer_metrics['predicted_clv_6m'] * churn_factor
        )
        
        clv_percentiles = self.customer_metrics['predicted_clv_6m_adjusted'].quantile([0.33, 0.67])
        def categorize_clv(value):
            if value >= clv_percentiles.iloc[1]:
                return 'High Value'
            elif value >= clv_percentiles.iloc[0]:
                return 'Medium Value'
            else:
                return 'Low Value'
        self.customer_metrics['clv_category'] = (
            self.customer_metrics['predicted_clv_6m_adjusted'].apply(categorize_clv)
        )
        
        # Churn risk
        recency_score = np.clip((self.customer_metrics['recency_days'] / 7) * 20, 0, 40)
        freq_percentile = self.customer_metrics['frequency'].rank(pct=True)
        frequency_score = (1 - freq_percentile) * 30
        failure_score = self.customer_metrics['failure_rate'] * 20
        txn_percentile = self.customer_metrics['transaction_count'].rank(pct=True)
        commitment_score = (1 - txn_percentile) * 10
        
        self.customer_metrics['churn_risk_score'] = (
            recency_score + frequency_score + failure_score + commitment_score
        )
        
        def categorize_churn(score):
            if score >= 60:
                return 'High Risk'
            elif score >= 35:
                return 'Medium Risk'
            else:
                return 'Low Risk'
        self.customer_metrics['churn_risk'] = (
            self.customer_metrics['churn_risk_score'].apply(categorize_churn)
        )
        
        # RFM Segmentation
        def score_metric(series, reverse=False):
            percentiles = series.rank(pct=True)
            if reverse:
                percentiles = 1 - percentiles
            return np.ceil(percentiles * 5).clip(1, 5)
        
        self.customer_metrics['R_score'] = score_metric(self.customer_metrics['recency_days'], reverse=True)
        self.customer_metrics['F_score'] = score_metric(self.customer_metrics['transaction_count'])
        self.customer_metrics['M_score'] = score_metric(self.customer_metrics['total_spent'])
        
        def assign_segment(row):
            R, F, M = row['R_score'], row['F_score'], row['M_score']
            if R >= 4 and F >= 4 and M >= 4:
                return 'Champions'
            elif R >= 3 and F >= 3 and M >= 3:
                return 'Loyal Customers'
            elif R >= 4 and F <= 2:
                return 'Potential Loyalists'
            elif R <= 2 and F >= 3 and M >= 3:
                return 'At Risk'
            elif R <= 2 and F >= 4 and M >= 4:
                return "Can't Lose Them"
            elif R <= 2 and F <= 2 and M <= 2:
                return 'Lost'
            elif R == 3 and F <= 2:
                return 'Hibernating'
            else:
                return 'Need Attention'
        
        self.customer_metrics['segment'] = self.customer_metrics.apply(assign_segment, axis=1)
        
    def create_visualizations(self):
        """Create all visualization charts"""
        print("\n" + "="*80)
        print("CREATING VISUALIZATIONS")
        print("="*80)
        
        # Create figure directory
        import os
        os.makedirs('outputs/charts', exist_ok=True)
        
        # 1. Revenue Overview Dashboard
        self._create_revenue_dashboard()
        
        # 2. Customer Segmentation Pie Chart
        self._create_segmentation_chart()
        
        # 3. CLV Distribution
        self._create_clv_distribution()
        
        # 4. Churn Risk Analysis
        self._create_churn_analysis()
        
        # 5. Peak Hours Heatmap
        self._create_peak_hours_heatmap()
        
        # 6. Station Performance
        self._create_station_performance()
        
        # 7. Transaction Trends
        self._create_transaction_trends()
        
        # 8. Customer Health Dashboard
        self._create_health_dashboard()
        
        print("\n✅ All visualizations created in: outputs/charts/")
        
    def _create_revenue_dashboard(self):
        """Create comprehensive revenue overview"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Jalikoi Revenue Analytics Dashboard ({self.currency})', 
                     fontsize=18, fontweight='bold', y=0.995)
        
        # 1. Total Revenue by Customer
        ax1 = axes[0, 0]
        top_customers = self.customer_metrics.nlargest(10, 'total_spent')
        bars = ax1.barh(range(len(top_customers)), top_customers['total_spent'], 
                        color=COLORS['primary'])
        ax1.set_yticks(range(len(top_customers)))
        ax1.set_yticklabels([f"Customer {id}" for id in top_customers['motorcyclist_id']])
        ax1.set_xlabel(f'Total Revenue ({self.currency})')
        ax1.set_title('Top 10 Customers by Revenue', fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (idx, row) in enumerate(top_customers.iterrows()):
            ax1.text(row['total_spent'], i, f" {row['total_spent']:,.0f}", 
                    va='center', fontsize=9)
        
        # 2. Revenue Distribution by Segment
        ax2 = axes[0, 1]
        segment_revenue = self.customer_metrics.groupby('segment')['total_spent'].sum().sort_values()
        colors_seg = [COLORS['success'], COLORS['info'], COLORS['warning'], COLORS['danger']][:len(segment_revenue)]
        segment_revenue.plot(kind='barh', ax=ax2, color=colors_seg)
        ax2.set_xlabel(f'Total Revenue ({self.currency})')
        ax2.set_title('Revenue by Customer Segment', fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # 3. CLV Projection
        ax3 = axes[1, 0]
        clv_data = self.customer_metrics.groupby('clv_category')['predicted_clv_6m_adjusted'].sum()
        clv_order = ['High Value', 'Medium Value', 'Low Value']
        clv_data = clv_data.reindex([c for c in clv_order if c in clv_data.index])
        colors_clv = [COLORS['success'], COLORS['info'], COLORS['warning']][:len(clv_data)]
        bars = ax3.bar(range(len(clv_data)), clv_data.values, color=colors_clv)
        ax3.set_xticks(range(len(clv_data)))
        ax3.set_xticklabels(clv_data.index, rotation=0)
        ax3.set_ylabel(f'Projected 6-Month Revenue ({self.currency})')
        ax3.set_title('Customer Lifetime Value Projection', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(clv_data.values):
            ax3.text(i, v, f'\n{v/1e6:.1f}M', ha='center', va='bottom', fontweight='bold')
        
        # 4. Revenue Metrics Summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        total_revenue = self.customer_metrics['total_spent'].sum()
        avg_revenue = self.customer_metrics['total_spent'].mean()
        projected_revenue = self.customer_metrics['predicted_clv_6m_adjusted'].sum()
        total_customers = len(self.customer_metrics)
        
        summary_text = f"""
        KEY REVENUE METRICS
        ═══════════════════════════════════════
        
        Total Revenue (Historical)
        {total_revenue:,.0f} {self.currency}
        
        Projected Revenue (6 Months)
        {projected_revenue:,.0f} {self.currency}
        
        Average Customer Value
        {avg_revenue:,.0f} {self.currency}
        
        Total Active Customers
        {total_customers} customers
        
        Revenue Per Customer (6M)
        {projected_revenue/total_customers:,.0f} {self.currency}
        
        Growth Potential
        +{((projected_revenue/total_revenue - 1) * 100):.0f}% over current
        """
        
        ax4.text(0.1, 0.9, summary_text, fontsize=12, fontfamily='monospace',
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        plt.savefig('outputs/charts/01_revenue_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Revenue Dashboard created")
        
    def _create_segmentation_chart(self):
        """Create customer segmentation visualization"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        fig.suptitle('Customer Segmentation Analysis', fontsize=16, fontweight='bold')
        
        # 1. Segment Distribution (Count)
        ax1 = axes[0]
        segment_counts = self.customer_metrics['segment'].value_counts()
        colors = plt.cm.Set3(range(len(segment_counts)))
        wedges, texts, autotexts = ax1.pie(segment_counts.values, labels=segment_counts.index,
                                            autopct='%1.1f%%', startangle=90, colors=colors,
                                            textprops={'fontsize': 11})
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax1.set_title('Customer Distribution by Segment', fontweight='bold', pad=20)
        
        # 2. Segment Value (Revenue)
        ax2 = axes[1]
        segment_revenue = self.customer_metrics.groupby('segment')['total_spent'].sum()
        colors = plt.cm.Set2(range(len(segment_revenue)))
        wedges, texts, autotexts = ax2.pie(segment_revenue.values, labels=segment_revenue.index,
                                            autopct=lambda pct: f'{pct:.1f}%\n{pct/100*segment_revenue.sum():,.0f} {self.currency}',
                                            startangle=90, colors=colors,
                                            textprops={'fontsize': 9})
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax2.set_title('Revenue Distribution by Segment', fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig('outputs/charts/02_customer_segmentation.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Customer Segmentation chart created")
        
    def _create_clv_distribution(self):
        """Create CLV distribution visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Customer Lifetime Value Analysis ({self.currency})', fontsize=16, fontweight='bold')
        
        # 1. CLV Distribution Histogram
        ax1 = axes[0, 0]
        ax1.hist(self.customer_metrics['predicted_clv_6m_adjusted']/1e6, bins=10, 
                color=COLORS['primary'], edgecolor='black', alpha=0.7)
        ax1.set_xlabel(f'Projected CLV - 6 Months (Millions {self.currency})')
        ax1.set_ylabel('Number of Customers')
        ax1.set_title('CLV Distribution', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. CLV vs Transaction Count
        ax2 = axes[0, 1]
        scatter = ax2.scatter(self.customer_metrics['transaction_count'], 
                             self.customer_metrics['predicted_clv_6m_adjusted']/1e6,
                             c=self.customer_metrics['churn_risk_score'],
                             cmap='RdYlGn_r', s=100, alpha=0.6, edgecolors='black')
        ax2.set_xlabel('Transaction Count')
        ax2.set_ylabel(f'Projected CLV (Millions {self.currency})')
        ax2.set_title('CLV vs Transaction Frequency', fontweight='bold')
        ax2.grid(alpha=0.3)
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Churn Risk Score', rotation=270, labelpad=20)
        
        # 3. Top Customers Table
        ax3 = axes[1, 0]
        ax3.axis('tight')
        ax3.axis('off')
        
        top_clv = self.customer_metrics.nlargest(8, 'predicted_clv_6m_adjusted')[
            ['motorcyclist_id', 'predicted_clv_6m_adjusted', 'transaction_count', 'segment']
        ].copy()
        top_clv['predicted_clv_6m_adjusted'] = top_clv['predicted_clv_6m_adjusted'].apply(
            lambda x: f"{x/1e6:.1f}M"
        )
        top_clv.columns = ['Customer ID', f'6M CLV ({self.currency})', 'Transactions', 'Segment']
        
        table = ax3.table(cellText=top_clv.values, colLabels=top_clv.columns,
                         cellLoc='center', loc='center',
                         colColours=[COLORS['primary']]*4)
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax3.set_title('Top 8 Customers by CLV', fontweight='bold', pad=20)
        
        # 4. CLV Category Summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        high_value = self.customer_metrics[self.customer_metrics['clv_category'] == 'High Value']
        med_value = self.customer_metrics[self.customer_metrics['clv_category'] == 'Medium Value']
        low_value = self.customer_metrics[self.customer_metrics['clv_category'] == 'Low Value']
        
        summary = f"""
        CLV CATEGORY INSIGHTS
        ═══════════════════════════════════════
        
        🏆 HIGH VALUE CUSTOMERS
           Count: {len(high_value)} customers
           Total CLV: {high_value['predicted_clv_6m_adjusted'].sum():,.0f} {self.currency}
           Avg CLV: {high_value['predicted_clv_6m_adjusted'].mean():,.0f} {self.currency}
        
        💎 MEDIUM VALUE CUSTOMERS
           Count: {len(med_value)} customers
           Total CLV: {med_value['predicted_clv_6m_adjusted'].sum():,.0f} {self.currency}
           Avg CLV: {med_value['predicted_clv_6m_adjusted'].mean():,.0f} {self.currency}
        
        💰 LOW VALUE CUSTOMERS
           Count: {len(low_value)} customers
           Total CLV: {low_value['predicted_clv_6m_adjusted'].sum():,.0f} {self.currency}
           Avg CLV: {low_value['predicted_clv_6m_adjusted'].mean():,.0f} {self.currency}
        
        ═══════════════════════════════════════
        
        📊 TOTAL PROJECTED (6 Months)
           {self.customer_metrics['predicted_clv_6m_adjusted'].sum():,.0f} {self.currency}
        """
        
        ax4.text(0.1, 0.9, summary, fontsize=10, fontfamily='monospace',
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        
        plt.tight_layout()
        plt.savefig('outputs/charts/03_clv_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ CLV Analysis chart created")
        
    def _create_churn_analysis(self):
        """Create churn risk visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Churn Risk Analysis', fontsize=16, fontweight='bold')
        
        # 1. Churn Risk Distribution
        ax1 = axes[0, 0]
        churn_dist = self.customer_metrics['churn_risk'].value_counts()
        risk_order = ['High Risk', 'Medium Risk', 'Low Risk']
        churn_dist = churn_dist.reindex([r for r in risk_order if r in churn_dist.index], fill_value=0)
        colors_risk = [COLORS['danger'], COLORS['warning'], COLORS['success']][:len(churn_dist)]
        bars = ax1.bar(range(len(churn_dist)), churn_dist.values, color=colors_risk, edgecolor='black')
        ax1.set_xticks(range(len(churn_dist)))
        ax1.set_xticklabels(churn_dist.index)
        ax1.set_ylabel('Number of Customers')
        ax1.set_title('Churn Risk Distribution', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(churn_dist.values):
            ax1.text(i, v, f'\n{v}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Churn Risk Score Distribution
        ax2 = axes[0, 1]
        ax2.hist(self.customer_metrics['churn_risk_score'], bins=15, 
                color=COLORS['warning'], edgecolor='black', alpha=0.7)
        ax2.axvline(35, color=COLORS['danger'], linestyle='--', linewidth=2, label='Medium Risk Threshold')
        ax2.axvline(60, color='red', linestyle='--', linewidth=2, label='High Risk Threshold')
        ax2.set_xlabel('Churn Risk Score')
        ax2.set_ylabel('Number of Customers')
        ax2.set_title('Churn Risk Score Distribution', fontweight='bold')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. CLV at Risk by Churn Category
        ax3 = axes[1, 0]
        risk_clv = self.customer_metrics.groupby('churn_risk')['predicted_clv_6m_adjusted'].sum()
        risk_clv = risk_clv.reindex([r for r in risk_order if r in risk_clv.index], fill_value=0)
        bars = ax3.barh(range(len(risk_clv)), risk_clv.values/1e6, color=colors_risk, edgecolor='black')
        ax3.set_yticks(range(len(risk_clv)))
        ax3.set_yticklabels(risk_clv.index)
        ax3.set_xlabel(f'Revenue at Risk - 6 Months (Millions {self.currency})')
        ax3.set_title('Revenue at Risk by Churn Category', fontweight='bold')
        ax3.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(risk_clv.values):
            ax3.text(v/1e6, i, f' {v/1e6:.1f}M', va='center', fontsize=10, fontweight='bold')
        
        # 4. High-Risk Customers Alert
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        high_risk = self.customer_metrics[self.customer_metrics['churn_risk'] == 'High Risk']
        medium_risk = self.customer_metrics[self.customer_metrics['churn_risk'] == 'Medium Risk']
        high_value_at_risk = self.customer_metrics[
            (self.customer_metrics['clv_category'] == 'High Value') &
            (self.customer_metrics['churn_risk'].isin(['High Risk', 'Medium Risk']))
        ]
        
        alert_text = f"""
        🚨 CHURN RISK ALERTS
        ═══════════════════════════════════════
        
        HIGH RISK CUSTOMERS
           Count: {len(high_risk)} customers
           Revenue at Risk: {high_risk['predicted_clv_6m_adjusted'].sum():,.0f} {self.currency}
           → ACTION: Immediate personal outreach
           → OFFER: 20% retention discount
        
        MEDIUM RISK CUSTOMERS
           Count: {len(medium_risk)} customers
           Revenue at Risk: {medium_risk['predicted_clv_6m_adjusted'].sum():,.0f} {self.currency}
           → ACTION: Re-engagement campaign
           → OFFER: 10% special offer
        
        ⚠️  CRITICAL SITUATION
           High-Value Customers at Risk: {len(high_value_at_risk)}
           Potential Loss: {high_value_at_risk['predicted_clv_6m_adjusted'].sum():,.0f} {self.currency}
        
        ═══════════════════════════════════════
        
        💡 RETENTION PRIORITY
           Focus on High-Value + High-Risk customers
           Expected Save Rate: 60-80%
           Potential Savings: {high_value_at_risk['predicted_clv_6m_adjusted'].sum()*0.7:,.0f} {self.currency}
        """
        
        color = 'lightyellow' if len(high_value_at_risk) == 0 else 'lightcoral'
        ax4.text(0.05, 0.95, alert_text, fontsize=9, fontfamily='monospace',
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor=color, alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('outputs/charts/04_churn_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Churn Analysis chart created")
        
    def _create_peak_hours_heatmap(self):
        """Create peak hours visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Peak Hours & Transaction Timing Analysis', fontsize=16, fontweight='bold')
        
        # 1. Hourly Transaction Volume
        ax1 = axes[0, 0]
        hourly = self.df_success.groupby('hour')['id'].count()
        ax1.bar(hourly.index, hourly.values, color=COLORS['primary'], edgecolor='black')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Number of Transactions')
        ax1.set_title('Transaction Volume by Hour', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_xticks(range(0, 24))
        
        # Highlight peak hours
        peak_hours = hourly.nlargest(3).index
        for hour in peak_hours:
            ax1.axvspan(hour-0.5, hour+0.5, alpha=0.3, color='yellow')
        
        # 2. Hourly Revenue
        ax2 = axes[0, 1]
        hourly_revenue = self.df_success.groupby('hour')['amount'].sum()
        ax2.plot(hourly_revenue.index, hourly_revenue.values/1000, marker='o', 
                linewidth=2, markersize=8, color=COLORS['success'])
        ax2.fill_between(hourly_revenue.index, hourly_revenue.values/1000, alpha=0.3, color=COLORS['success'])
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel(f'Revenue (Thousands {self.currency})')
        ax2.set_title('Revenue by Hour', fontweight='bold')
        ax2.grid(alpha=0.3)
        ax2.set_xticks(range(0, 24))
        
        # 3. Day of Week Analysis
        ax3 = axes[1, 0]
        daily = self.df_success.groupby('day_name')['amount'].sum()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily = daily.reindex([d for d in day_order if d in daily.index])
        colors_days = [COLORS['primary'] if v == daily.max() else COLORS['info'] for v in daily.values]
        ax3.bar(range(len(daily)), daily.values/1000, color=colors_days, edgecolor='black')
        ax3.set_xticks(range(len(daily)))
        ax3.set_xticklabels(daily.index, rotation=45, ha='right')
        ax3.set_ylabel(f'Total Revenue (Thousands {self.currency})')
        ax3.set_title('Revenue by Day of Week', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Peak Hours Summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        peak_hour = hourly.idxmax()
        peak_revenue_hour = hourly_revenue.idxmax()
        total_peak_3hrs = hourly.nlargest(3).sum()
        total_txns = hourly.sum()
        peak_concentration = (total_peak_3hrs / total_txns) * 100
        
        summary = f"""
        ⏰ PEAK HOURS INSIGHTS
        ═══════════════════════════════════════
        
        BUSIEST HOUR (Volume)
           {peak_hour}:00 - {peak_hour+1}:00
           {hourly.max()} transactions
        
        HIGHEST REVENUE HOUR
           {peak_revenue_hour}:00 - {peak_revenue_hour+1}:00
           {hourly_revenue.max():,.0f} {self.currency}
        
        TOP 3 PEAK HOURS
           {', '.join([f'{h}:00' for h in peak_hours])}
           {total_peak_3hrs} transactions ({peak_concentration:.1f}% of total)
        
        ═══════════════════════════════════════
        
        💡 OPTIMIZATION RECOMMENDATIONS
        
        1. STAFF FOR PEAK (15:00-18:00)
           → Full team deployment
           → Maximum fuel inventory
           → Fast transaction processing
        
        2. SHIFT TRAFFIC TO OFF-PEAK
           → 7% discount before 14:00
           → Could reduce congestion by 15%
           → Better margins + customer satisfaction
        
        3. MAINTENANCE WINDOW
           → 8:00-11:00 (lowest volume)
           → Restocking and system updates
        """
        
        ax4.text(0.05, 0.95, summary, fontsize=9, fontfamily='monospace',
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
        
        plt.tight_layout()
        plt.savefig('outputs/charts/05_peak_hours_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Peak Hours Analysis chart created")
        
    def _create_station_performance(self):
        """Create station performance visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Station Performance Analysis ({self.currency})', fontsize=16, fontweight='bold')
        
        # Station metrics
        station_metrics = self.df_success.groupby('station_id').agg({
            'id': 'count',
            'amount': ['sum', 'mean'],
            'motorcyclist_id': 'nunique'
        })
        station_metrics.columns = ['transactions', 'revenue', 'avg_transaction', 'unique_customers']
        
        # 1. Revenue by Station
        ax1 = axes[0, 0]
        station_revenue = station_metrics['revenue'].sort_values()
        colors_station = plt.cm.Greens(np.linspace(0.4, 0.9, len(station_revenue)))
        ax1.barh(range(len(station_revenue)), station_revenue.values/1000, 
                color=colors_station, edgecolor='black')
        ax1.set_yticks(range(len(station_revenue)))
        ax1.set_yticklabels([f"Station {id}" for id in station_revenue.index])
        ax1.set_xlabel(f'Total Revenue (Thousands {self.currency})')
        ax1.set_title('Revenue by Station', fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(station_revenue.values):
            ax1.text(v/1000, i, f' {v/1000:.0f}K', va='center', fontsize=9)
        
        # 2. Transactions by Station
        ax2 = axes[0, 1]
        station_txns = station_metrics['transactions'].sort_values()
        colors_txn = plt.cm.Blues(np.linspace(0.4, 0.9, len(station_txns)))
        ax2.barh(range(len(station_txns)), station_txns.values, 
                color=colors_txn, edgecolor='black')
        ax2.set_yticks(range(len(station_txns)))
        ax2.set_yticklabels([f"Station {id}" for id in station_txns.index])
        ax2.set_xlabel('Number of Transactions')
        ax2.set_title('Transaction Volume by Station', fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # 3. Average Transaction Value
        ax3 = axes[1, 0]
        avg_txn = station_metrics['avg_transaction'].sort_values()
        colors_avg = plt.cm.Oranges(np.linspace(0.4, 0.9, len(avg_txn)))
        bars = ax3.bar(range(len(avg_txn)), avg_txn.values/1000, 
                      color=colors_avg, edgecolor='black')
        ax3.set_xticks(range(len(avg_txn)))
        ax3.set_xticklabels([f"Stn {id}" for id in avg_txn.index])
        ax3.set_ylabel(f'Avg Transaction (Thousands {self.currency})')
        ax3.set_title('Average Transaction Value by Station', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(avg_txn.values):
            ax3.text(i, v/1000, f'{v/1000:.1f}K', ha='center', va='bottom', fontsize=9)
        
        # 4. Station Performance Summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        top_revenue_station = station_metrics['revenue'].idxmax()
        top_volume_station = station_metrics['transactions'].idxmax()
        top_avg_station = station_metrics['avg_transaction'].idxmax()
        
        summary = f"""
        🏪 STATION PERFORMANCE SUMMARY
        ═══════════════════════════════════════
        
        TOP REVENUE STATION
           Station {top_revenue_station}
           Revenue: {station_metrics.loc[top_revenue_station, 'revenue']:,.0f} {self.currency}
           Transactions: {station_metrics.loc[top_revenue_station, 'transactions']:.0f}
        
        BUSIEST STATION (Volume)
           Station {top_volume_station}
           Transactions: {station_metrics.loc[top_volume_station, 'transactions']:.0f}
           Customers: {station_metrics.loc[top_volume_station, 'unique_customers']:.0f}
        
        HIGHEST AVG TRANSACTION
           Station {top_avg_station}
           Avg: {station_metrics.loc[top_avg_station, 'avg_transaction']:,.0f} {self.currency}
           → Premium customer base
        
        ═══════════════════════════════════════
        
        💡 STATION RECOMMENDATIONS
        
        1. Best Performer (Station {top_revenue_station})
           → Model for other stations
           → Share best practices
        
        2. High Volume Stations
           → Ensure adequate staffing
           → Optimize for speed
        
        3. Station-Specific Promotions
           → Loyalty programs per station
           → Cross-promote to balance load
        """
        
        ax4.text(0.05, 0.95, summary, fontsize=9, fontfamily='monospace',
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('outputs/charts/06_station_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Station Performance chart created")
        
    def _create_transaction_trends(self):
        """Create transaction trend visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Transaction Trends & Patterns ({self.currency})', fontsize=16, fontweight='bold')
        
        # 1. Daily Transaction Count
        ax1 = axes[0, 0]
        daily_txns = self.df_success.groupby('date')['id'].count()
        ax1.plot(daily_txns.index, daily_txns.values, marker='o', linewidth=2, 
                color=COLORS['primary'], markersize=6)
        ax1.fill_between(daily_txns.index, daily_txns.values, alpha=0.3, color=COLORS['primary'])
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Number of Transactions')
        ax1.set_title('Daily Transaction Volume', fontweight='bold')
        ax1.grid(alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Daily Revenue
        ax2 = axes[0, 1]
        daily_revenue = self.df_success.groupby('date')['amount'].sum()
        ax2.plot(daily_revenue.index, daily_revenue.values/1000, marker='s', linewidth=2, 
                color=COLORS['success'], markersize=6)
        ax2.fill_between(daily_revenue.index, daily_revenue.values/1000, alpha=0.3, color=COLORS['success'])
        ax2.set_xlabel('Date')
        ax2.set_ylabel(f'Revenue (Thousands {self.currency})')
        ax2.set_title('Daily Revenue Trend', fontweight='bold')
        ax2.grid(alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Transaction Size Distribution
        ax3 = axes[1, 0]
        ax3.hist(self.df_success['amount']/1000, bins=20, color=COLORS['info'], 
                edgecolor='black', alpha=0.7)
        ax3.axvline(self.df_success['amount'].mean()/1000, color='red', 
                   linestyle='--', linewidth=2, label=f'Mean: {self.df_success["amount"].mean()/1000:.1f}K')
        ax3.axvline(self.df_success['amount'].median()/1000, color='green', 
                   linestyle='--', linewidth=2, label=f'Median: {self.df_success["amount"].median()/1000:.1f}K')
        ax3.set_xlabel(f'Transaction Amount (Thousands {self.currency})')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Transaction Size Distribution', fontweight='bold')
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Payment Channel Distribution
        ax4 = axes[1, 1]
        channel_dist = self.df_success['source'].value_counts()
        colors_channel = [COLORS['primary'], COLORS['success']][:len(channel_dist)]
        wedges, texts, autotexts = ax4.pie(channel_dist.values, labels=channel_dist.index,
                                           autopct='%1.1f%%', startangle=90, colors=colors_channel,
                                           textprops={'fontsize': 12})
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax4.set_title('Transaction Distribution by Channel\n(APP vs USSD)', fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig('outputs/charts/07_transaction_trends.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Transaction Trends chart created")
        
    def _create_health_dashboard(self):
        """Create customer health dashboard"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Customer Health & Risk Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Overall Health Distribution
        ax1 = axes[0, 0]
        
        # Calculate health scores
        recency_score = 100 - np.clip((self.customer_metrics['recency_days'] / 7) * 40, 0, 100)
        frequency_score = np.clip(self.customer_metrics['frequency'] * 20, 0, 50)
        value_score = (self.customer_metrics['total_spent'].rank(pct=True) * 50)
        health_scores = (recency_score + frequency_score + value_score) / 2
        
        def categorize_health(score):
            if score >= 70:
                return 'Excellent'
            elif score >= 50:
                return 'Good'
            elif score >= 30:
                return 'Warning'
            else:
                return 'Critical'
        
        health_status = health_scores.apply(categorize_health)
        health_dist = health_status.value_counts()
        
        status_order = ['Excellent', 'Good', 'Warning', 'Critical']
        health_dist = health_dist.reindex([s for s in status_order if s in health_dist.index], fill_value=0)
        colors_health = [COLORS['excellent'], COLORS['good'], COLORS['warning'], COLORS['critical']][:len(health_dist)]
        
        bars = ax1.bar(range(len(health_dist)), health_dist.values, color=colors_health, edgecolor='black')
        ax1.set_xticks(range(len(health_dist)))
        ax1.set_xticklabels(health_dist.index)
        ax1.set_ylabel('Number of Customers')
        ax1.set_title('Customer Health Status Distribution', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels and percentages
        total = health_dist.sum()
        for i, v in enumerate(health_dist.values):
            pct = (v/total)*100 if total > 0 else 0
            ax1.text(i, v, f'{v}\n({pct:.0f}%)', ha='center', va='bottom', fontweight='bold')
        
        # 2. RFM Score Heatmap
        ax2 = axes[0, 1]
        rfm_matrix = self.customer_metrics.groupby(['R_score', 'F_score']).size().unstack(fill_value=0)
        sns.heatmap(rfm_matrix, annot=True, fmt='d', cmap='YlGnBu', ax=ax2, cbar_kws={'label': 'Customer Count'})
        ax2.set_xlabel('Frequency Score')
        ax2.set_ylabel('Recency Score')
        ax2.set_title('RFM Analysis Heatmap', fontweight='bold')
        
        # 3. Segment Health Matrix
        ax3 = axes[1, 0]
        ax3.axis('off')
        
        segment_health = []
        for segment in self.customer_metrics['segment'].unique():
            seg_data = self.customer_metrics[self.customer_metrics['segment'] == segment]
            segment_health.append({
                'Segment': segment,
                'Count': len(seg_data),
                'Avg CLV': f"{seg_data['predicted_clv_6m_adjusted'].mean()/1e6:.1f}M",
                'At Risk': sum(seg_data['churn_risk'].isin(['High Risk', 'Medium Risk']))
            })
        
        seg_df = pd.DataFrame(segment_health)
        
        table = ax3.table(cellText=seg_df.values, colLabels=seg_df.columns,
                         cellLoc='center', loc='center',
                         colColours=[COLORS['primary']]*4)
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        ax3.set_title('Segment Health Matrix', fontweight='bold', pad=20, fontsize=14)
        
        # 4. Key Metrics Summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        excellent_count = health_dist.get('Excellent', 0)
        critical_count = health_dist.get('Critical', 0)
        high_risk_count = (self.customer_metrics['churn_risk'] == 'High Risk').sum()
        avg_health = health_scores.mean()
        
        summary = f"""
        📊 HEALTH DASHBOARD SUMMARY
        ═══════════════════════════════════════
        
        OVERALL HEALTH
           Average Health Score: {avg_health:.1f}/100
           Excellent Health: {excellent_count} customers
           Critical Health: {critical_count} customers
        
        RISK STATUS
           High Churn Risk: {high_risk_count} customers
           Medium Churn Risk: {(self.customer_metrics['churn_risk'] == 'Medium Risk').sum()} customers
        
        SEGMENTS
           Total Segments: {self.customer_metrics['segment'].nunique()}
           Champions: {(self.customer_metrics['segment'] == 'Champions').sum()}
           At Risk: {(self.customer_metrics['segment'] == 'At Risk').sum()}
        
        ═══════════════════════════════════════
        
        🎯 IMMEDIATE ACTIONS NEEDED
        
        1. Contact {critical_count} Critical Health customers
        2. Launch retention for {high_risk_count} High Risk
        3. Reward {excellent_count} Excellent customers
        4. Monitor segment movements weekly
        
        ✅ Health Status: {'🟢 GOOD' if avg_health >= 60 else '🟡 NEEDS ATTENTION'}
        """
        
        color = 'lightgreen' if avg_health >= 60 else 'lightyellow'
        ax4.text(0.05, 0.95, summary, fontsize=9, fontfamily='monospace',
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor=color, alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('outputs/charts/08_health_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Customer Health Dashboard created")
        
    def run_complete_analysis(self):
        """Run complete analysis with visualizations"""
        print("\n" + "="*80)
        print("JALIKOI ANALYTICS - COMPLETE ANALYSIS WITH VISUALIZATIONS")
        print(f"Currency: {self.currency} (Rwandan Francs)")
        print("="*80)
        
        # Print key metrics
        total_revenue = self.customer_metrics['total_spent'].sum()
        projected_revenue = self.customer_metrics['predicted_clv_6m_adjusted'].sum()
        total_customers = len(self.customer_metrics)
        
        print(f"\n📊 KEY METRICS:")
        print(f"   Total Revenue: {total_revenue:,.0f} {self.currency}")
        print(f"   Projected 6M Revenue: {projected_revenue:,.0f} {self.currency}")
        print(f"   Total Customers: {total_customers}")
        print(f"   Avg Customer Value: {total_revenue/total_customers:,.0f} {self.currency}")
        
        # Create all visualizations
        self.create_visualizations()
        
        # Export data
        output_file = 'outputs/jalikoi_customer_insights_rwf.xlsx'
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            self.customer_metrics.to_excel(writer, sheet_name='Customer_Insights', index=False)
            
            segment_summary = self.customer_metrics.groupby('segment').agg({
                'motorcyclist_id': 'count',
                'total_spent': 'sum',
                'predicted_clv_6m_adjusted': 'sum'
            }).round(2)
            segment_summary.to_excel(writer, sheet_name='Segment_Summary')
        
        print(f"\n✅ Excel report saved: {output_file}")
        print(f"✅ All visualizations saved in: outputs/charts/")
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)


def main():
    analytics = JalikoiAnalyticsVisualized('uploads/payments.csv')
    analytics.run_complete_analysis()


if __name__ == "__main__":
    main()