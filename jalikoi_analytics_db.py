#!/usr/bin/env python3
"""
Jalikoi Customer Analytics with MySQL Database Connection
==========================================================
Direct database connection with visualizations
Currency: Rwandan Francs (RWF)
Data Source: MySQL Database (Real-time)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Import database connector
try:
    from database_connector import JalikoiDatabaseConnector, load_payments_from_database
    from db_config import DB_CONFIG, PAYMENTS_QUERY
    DATABASE_MODE = True
except ImportError:
    DATABASE_MODE = False
    print("⚠️  Database modules not found. Will fall back to CSV mode.")
    print("   To enable database mode:")
    print("   1. Create db_config.py from db_config_template.py")
    print("   2. Install: pip install mysql-connector-python pymysql sqlalchemy")

# Set style for beautiful charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Color palette
COLORS = {
    'primary': '#2E86AB',
    'success': '#06D6A0',
    'warning': '#F77F00',
    'danger': '#D62828',
    'info': '#023E8A',
}

class JalikoiAnalyticsVisualized:
    """Enhanced analytics with visualizations and RWF currency"""
    
    def __init__(self, data_source, use_database=True):
        """
        Initialize analytics
        
        Args:
            data_source: Database config dict or CSV file path
            use_database (bool): True to use database, False for CSV
        """
        self.currency = "RWF"
        self.use_database = use_database and DATABASE_MODE
        
        # Load data from database or CSV
        if self.use_database and isinstance(data_source, dict):
            print("\n" + "="*80)
            print("LOADING DATA FROM MYSQL DATABASE")
            print("="*80)
            self.df = self._load_from_database(data_source)
        else:
            print("\n" + "="*80)
            print("LOADING DATA FROM CSV FILE")
            print("="*80)
            if isinstance(data_source, str):
                self.df = pd.read_csv(data_source)
                print(f"✅ Loaded {len(self.df)} records from CSV")
            else:
                self.df = data_source
        
        if self.df is None or self.df.empty:
            raise ValueError("No data loaded! Check your database connection or CSV file.")
        
        self._preprocess_data()
        self._engineer_features()
    
    def _load_from_database(self, config):
        """Load data from MySQL database"""
        try:
            with JalikoiDatabaseConnector(config) as db:
                print("📊 Checking database...")
                df = db.fetch_data(PAYMENTS_QUERY)
                
                if df is not None and not df.empty:
                    print(f"✅ Successfully loaded {len(df)} records from database")
                    return df
                else:
                    print("❌ No data returned from database")
                    return None
                    
        except Exception as e:
            print(f"❌ Database error: {e}")
            print("   Falling back to CSV mode if available...")
            return None
        
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
        # CLV Calculation
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
        
        # Churn Risk Calculation
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
        import os
        os.makedirs('outputs/charts', exist_ok=True)
        
        print("\n" + "="*80)
        print("CREATING VISUALIZATIONS")
        print("="*80)
        
        self._create_revenue_dashboard()
        self._create_customer_segmentation()
        self._create_clv_analysis()
        self._create_churn_analysis()
        
        print("\n✅ All visualizations created in: outputs/charts/")
    
    def _create_revenue_dashboard(self):
        """Revenue overview dashboard"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Jalikoi Revenue Analytics Dashboard ({self.currency})', 
                     fontsize=18, fontweight='bold')
        
        # Top customers
        ax1 = axes[0, 0]
        top_customers = self.customer_metrics.nlargest(10, 'total_spent')
        ax1.barh(range(len(top_customers)), top_customers['total_spent'], color=COLORS['primary'])
        ax1.set_yticks(range(len(top_customers)))
        ax1.set_yticklabels([f"Customer {id}" for id in top_customers['motorcyclist_id']])
        ax1.set_xlabel(f'Total Revenue ({self.currency})')
        ax1.set_title('Top 10 Customers by Revenue', fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Segment revenue
        ax2 = axes[0, 1]
        segment_revenue = self.customer_metrics.groupby('segment')['total_spent'].sum().sort_values()
        segment_revenue.plot(kind='barh', ax=ax2, color=COLORS['success'])
        ax2.set_xlabel(f'Total Revenue ({self.currency})')
        ax2.set_title('Revenue by Customer Segment', fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # CLV projection
        ax3 = axes[1, 0]
        clv_data = self.customer_metrics.groupby('clv_category')['predicted_clv_6m_adjusted'].sum()
        clv_order = ['High Value', 'Medium Value', 'Low Value']
        clv_data = clv_data.reindex([c for c in clv_order if c in clv_data.index])
        ax3.bar(range(len(clv_data)), clv_data.values, color=[COLORS['success'], COLORS['info'], COLORS['warning']][:len(clv_data)])
        ax3.set_xticks(range(len(clv_data)))
        ax3.set_xticklabels(clv_data.index)
        ax3.set_ylabel(f'Projected 6-Month Revenue ({self.currency})')
        ax3.set_title('Customer Lifetime Value Projection', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        # Summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        total_revenue = self.customer_metrics['total_spent'].sum()
        projected_revenue = self.customer_metrics['predicted_clv_6m_adjusted'].sum()
        summary_text = f"""
        KEY REVENUE METRICS
        
        Total Revenue: {total_revenue:,.0f} {self.currency}
        Projected 6M: {projected_revenue:,.0f} {self.currency}
        Total Customers: {len(self.customer_metrics)}
        Avg Customer Value: {total_revenue/len(self.customer_metrics):,.0f} {self.currency}
        """
        ax4.text(0.1, 0.5, summary_text, fontsize=12, fontfamily='monospace',
                verticalalignment='center')
        
        plt.tight_layout()
        plt.savefig('outputs/charts/01_revenue_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Revenue Dashboard created")
    
    def _create_customer_segmentation(self):
        """Customer segmentation pie charts"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        fig.suptitle('Customer Segmentation Analysis', fontsize=16, fontweight='bold')
        
        # Count distribution
        ax1 = axes[0]
        segment_counts = self.customer_metrics['segment'].value_counts()
        ax1.pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%', 
                startangle=90, colors=plt.cm.Set3(range(len(segment_counts))))
        ax1.set_title('Customer Distribution by Segment', fontweight='bold')
        
        # Revenue distribution
        ax2 = axes[1]
        segment_revenue = self.customer_metrics.groupby('segment')['total_spent'].sum()
        ax2.pie(segment_revenue.values, labels=segment_revenue.index, 
                autopct=lambda pct: f'{pct:.1f}%', startangle=90,
                colors=plt.cm.Set2(range(len(segment_revenue))))
        ax2.set_title('Revenue Distribution by Segment', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('outputs/charts/02_customer_segmentation.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Customer Segmentation created")
    
    def _create_clv_analysis(self):
        """CLV distribution and analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Customer Lifetime Value Analysis ({self.currency})', fontsize=16, fontweight='bold')
        
        # CLV histogram
        ax1 = axes[0, 0]
        ax1.hist(self.customer_metrics['predicted_clv_6m_adjusted']/1e6, bins=15, 
                color=COLORS['primary'], edgecolor='black', alpha=0.7)
        ax1.set_xlabel(f'Projected CLV - 6 Months (Millions {self.currency})')
        ax1.set_ylabel('Number of Customers')
        ax1.set_title('CLV Distribution', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # CLV vs Transactions
        ax2 = axes[0, 1]
        scatter = ax2.scatter(self.customer_metrics['transaction_count'], 
                             self.customer_metrics['predicted_clv_6m_adjusted']/1e6,
                             c=self.customer_metrics['churn_risk_score'],
                             cmap='RdYlGn_r', s=100, alpha=0.6)
        ax2.set_xlabel('Transaction Count')
        ax2.set_ylabel(f'Projected CLV (Millions {self.currency})')
        ax2.set_title('CLV vs Transaction Frequency', fontweight='bold')
        plt.colorbar(scatter, ax=ax2, label='Churn Risk Score')
        
        # Top customers table
        ax3 = axes[1, 0]
        ax3.axis('off')
        top_clv = self.customer_metrics.nlargest(8, 'predicted_clv_6m_adjusted')[
            ['motorcyclist_id', 'predicted_clv_6m_adjusted', 'transaction_count', 'segment']
        ].copy()
        top_clv['predicted_clv_6m_adjusted'] = top_clv['predicted_clv_6m_adjusted'].apply(lambda x: f"{x/1e6:.1f}M")
        top_clv.columns = ['Customer ID', f'6M CLV ({self.currency})', 'Transactions', 'Segment']
        table = ax3.table(cellText=top_clv.values, colLabels=top_clv.columns,
                         cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax3.set_title('Top 8 Customers by CLV', fontweight='bold', pad=20)
        
        # CLV summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        total_clv = self.customer_metrics['predicted_clv_6m_adjusted'].sum()
        summary = f"""
        CLV INSIGHTS
        
        Total Projected CLV (6M): {total_clv:,.0f} {self.currency}
        Average CLV per Customer: {total_clv/len(self.customer_metrics):,.0f} {self.currency}
        
        High Value Customers: {sum(self.customer_metrics['clv_category']=='High Value')}
        Medium Value Customers: {sum(self.customer_metrics['clv_category']=='Medium Value')}
        Low Value Customers: {sum(self.customer_metrics['clv_category']=='Low Value')}
        """
        ax4.text(0.1, 0.5, summary, fontsize=11, fontfamily='monospace', verticalalignment='center')
        
        plt.tight_layout()
        plt.savefig('outputs/charts/03_clv_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ CLV Analysis created")
    
    def _create_churn_analysis(self):
        """Churn risk visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Churn Risk Analysis', fontsize=16, fontweight='bold')
        
        # Churn distribution
        ax1 = axes[0, 0]
        churn_dist = self.customer_metrics['churn_risk'].value_counts()
        risk_order = ['High Risk', 'Medium Risk', 'Low Risk']
        churn_dist = churn_dist.reindex([r for r in risk_order if r in churn_dist.index], fill_value=0)
        colors_risk = [COLORS['danger'], COLORS['warning'], COLORS['success']][:len(churn_dist)]
        ax1.bar(range(len(churn_dist)), churn_dist.values, color=colors_risk, edgecolor='black')
        ax1.set_xticks(range(len(churn_dist)))
        ax1.set_xticklabels(churn_dist.index)
        ax1.set_ylabel('Number of Customers')
        ax1.set_title('Churn Risk Distribution', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Risk score histogram
        ax2 = axes[0, 1]
        ax2.hist(self.customer_metrics['churn_risk_score'], bins=15, 
                color=COLORS['warning'], edgecolor='black', alpha=0.7)
        ax2.axvline(35, color=COLORS['danger'], linestyle='--', linewidth=2, label='Medium Risk')
        ax2.axvline(60, color='red', linestyle='--', linewidth=2, label='High Risk')
        ax2.set_xlabel('Churn Risk Score')
        ax2.set_ylabel('Number of Customers')
        ax2.set_title('Churn Risk Score Distribution', fontweight='bold')
        ax2.legend()
        
        # Revenue at risk
        ax3 = axes[1, 0]
        risk_clv = self.customer_metrics.groupby('churn_risk')['predicted_clv_6m_adjusted'].sum()
        risk_clv = risk_clv.reindex([r for r in risk_order if r in risk_clv.index], fill_value=0)
        ax3.barh(range(len(risk_clv)), risk_clv.values/1e6, color=colors_risk, edgecolor='black')
        ax3.set_yticks(range(len(risk_clv)))
        ax3.set_yticklabels(risk_clv.index)
        ax3.set_xlabel(f'Revenue at Risk (Millions {self.currency})')
        ax3.set_title('Revenue at Risk by Churn Category', fontweight='bold')
        
        # Alert summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        high_risk = self.customer_metrics[self.customer_metrics['churn_risk'] == 'High Risk']
        summary = f"""
        CHURN ALERTS
        
        High Risk Customers: {len(high_risk)}
        Revenue at Risk: {high_risk['predicted_clv_6m_adjusted'].sum():,.0f} {self.currency}
        
        ACTION REQUIRED:
        • Contact high-risk customers immediately
        • Offer retention incentives
        • Investigate pain points
        """
        ax4.text(0.1, 0.5, summary, fontsize=11, fontfamily='monospace', verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))
        
        plt.tight_layout()
        plt.savefig('outputs/charts/04_churn_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Churn Analysis created")
    
    def run_complete_analysis(self):
        """Run complete analysis with visualizations"""
        print("\n" + "="*80)
        print("JALIKOI ANALYTICS - COMPLETE ANALYSIS")
        print(f"Currency: {self.currency} (Rwandan Francs)")
        print("="*80)
        
        # Print metrics
        total_revenue = self.customer_metrics['total_spent'].sum()
        projected_revenue = self.customer_metrics['predicted_clv_6m_adjusted'].sum()
        
        print(f"\n📊 KEY METRICS:")
        print(f"   Total Revenue: {total_revenue:,.0f} {self.currency}")
        print(f"   Projected 6M: {projected_revenue:,.0f} {self.currency}")
        print(f"   Total Customers: {len(self.customer_metrics)}")
        
        # Create visualizations
        self.create_visualizations()
        
        # Export Excel
        import os
        os.makedirs('outputs', exist_ok=True)
        output_file = 'outputs/jalikoi_insights_rwf.xlsx'
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            self.customer_metrics.to_excel(writer, sheet_name='Customer_Insights', index=False)
            segment_summary = self.customer_metrics.groupby('segment').agg({
                'motorcyclist_id': 'count',
                'total_spent': 'sum',
                'predicted_clv_6m_adjusted': 'sum'
            }).round(2)
            segment_summary.to_excel(writer, sheet_name='Segment_Summary')
        
        print(f"\n✅ Excel report saved: {output_file}")
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)


def main():
    """Main execution - supports both database and CSV modes"""
    print("\n" + "="*80)
    print("JALIKOI CUSTOMER ANALYTICS")
    print("Currency: RWF (Rwandan Francs)")
    print("="*80)
    
    # Try database mode first
    if DATABASE_MODE:
        try:
            print("\n🔗 Attempting to connect to MySQL database...")
            analytics = JalikoiAnalyticsVisualized(DB_CONFIG, use_database=True)
            print("✅ Using LIVE DATABASE data")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            print("   Falling back to CSV mode...")
            
            # Fall back to CSV
            csv_file = 'payments.csv'
            try:
                analytics = JalikoiAnalyticsVisualized(csv_file, use_database=False)
                print("✅ Using CSV file data")
            except Exception as e2:
                print(f"❌ Both database and CSV failed: {e2}")
                return
    else:
        # CSV mode only
        print("\n📁 Database mode not available, using CSV file...")
        csv_file = 'payments.csv'
        analytics = JalikoiAnalyticsVisualized(csv_file, use_database=False)
        print("✅ Using CSV file data")
    
    # Run analysis
    analytics.run_complete_analysis()


if __name__ == "__main__":
    main()
