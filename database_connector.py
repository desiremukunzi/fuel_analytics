#!/usr/bin/env python3
"""
Jalikoi Database Connector
===========================
Handles MySQL database connections and data retrieval
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

class JalikoiDatabaseConnector:
    """
    Database connector for Jalikoi Analytics
    Supports MySQL/MariaDB databases
    """
    
    def __init__(self, config):
        """
        Initialize database connector
        
        Args:
            config (dict): Database configuration dictionary
        """
        self.config = config
        self.connection = None
        self.engine = None
        
    def connect(self):
        """Establish database connection"""
        try:
            # Remove SSL-related keys for basic connection
            conn_config = {
                k: v for k, v in self.config.items() 
                if k not in ['use_ssl', 'ssl_ca', 'ssl_cert', 'ssl_key']
            }
            
            # Add SSL configuration if enabled
            if self.config.get('use_ssl', False):
                ssl_config = {}
                if self.config.get('ssl_ca'):
                    ssl_config['ca'] = self.config['ssl_ca']
                if self.config.get('ssl_cert'):
                    ssl_config['cert'] = self.config['ssl_cert']
                if self.config.get('ssl_key'):
                    ssl_config['key'] = self.config['ssl_key']
                
                if ssl_config:
                    conn_config['ssl_disabled'] = False
                    conn_config['ssl'] = ssl_config
            
            self.connection = mysql.connector.connect(**conn_config)
            
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                print(f"✅ Connected to MySQL Server version {db_info}")
                
                cursor = self.connection.cursor()
                cursor.execute("SELECT DATABASE();")
                database = cursor.fetchone()[0]
                print(f"✅ Connected to database: {database}")
                cursor.close()
                
                return True
            
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return False
    
    def create_sqlalchemy_engine(self):
        """Create SQLAlchemy engine for pandas integration"""
        try:
            connection_string = (
                f"mysql+pymysql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
                f"?charset={self.config.get('charset', 'utf8mb4')}"
            )
            
            self.engine = create_engine(connection_string)
            print("✅ SQLAlchemy engine created")
            return self.engine
            
        except Exception as e:
            print(f"❌ Error creating SQLAlchemy engine: {e}")
            return None
    
    def fetch_data(self, query):
        """
        Execute SQL query and return results as DataFrame
        
        Args:
            query (str): SQL query to execute
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            if not self.connection or not self.connection.is_connected():
                print("⚠️ Not connected. Attempting to connect...")
                self.connect()
            
            print(f"📊 Executing query...")
            df = pd.read_sql(query, self.connection)
            print(f"✅ Retrieved {len(df)} records")
            
            return df
            
        except Error as e:
            print(f"❌ Error fetching data: {e}")
            return None
    
    def fetch_data_with_sqlalchemy(self, query):
        """
        Fetch data using SQLAlchemy (alternative method)
        
        Args:
            query (str): SQL query to execute
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            if not self.engine:
                self.create_sqlalchemy_engine()
            
            print(f"📊 Executing query with SQLAlchemy...")
            df = pd.read_sql(query, self.engine)
            print(f"✅ Retrieved {len(df)} records")
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
    
    def get_table_info(self, table_name):
        """
        Get information about a table
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            pd.DataFrame: Table structure information
        """
        try:
            query = f"DESCRIBE {table_name}"
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            columns = ['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']
            results = cursor.fetchall()
            cursor.close()
            
            df = pd.DataFrame(results, columns=columns)
            print(f"\n📋 Table Structure: {table_name}")
            print("="*60)
            print(df.to_string(index=False))
            print("="*60)
            
            return df
            
        except Error as e:
            print(f"❌ Error getting table info: {e}")
            return None
    
    def get_row_count(self, table_name, where_clause=""):
        """
        Get row count from table
        
        Args:
            table_name (str): Name of the table
            where_clause (str): Optional WHERE clause
            
        Returns:
            int: Number of rows
        """
        try:
            query = f"SELECT COUNT(*) FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count
            
        except Error as e:
            print(f"❌ Error getting row count: {e}")
            return 0
    
    def test_query(self, query, limit=5):
        """
        Test a query and show sample results
        
        Args:
            query (str): SQL query to test
            limit (int): Number of sample rows to display
            
        Returns:
            pd.DataFrame: Sample results
        """
        try:
            # Add LIMIT if not already present
            if 'LIMIT' not in query.upper():
                test_query = f"{query} LIMIT {limit}"
            else:
                test_query = query
            
            df = self.fetch_data(test_query)
            
            if df is not None and not df.empty:
                print(f"\n📊 Sample Data (First {len(df)} rows):")
                print("="*60)
                print(df.to_string(index=False))
                print("="*60)
                print(f"\n✅ Query successful! Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error testing query: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ Database connection closed")
        
        if self.engine:
            self.engine.dispose()
            print("✅ SQLAlchemy engine disposed")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def load_payments_from_database(config, query=None, table_name='payments'):
    """
    Convenience function to load payments data from database
    
    Args:
        config (dict): Database configuration
        query (str): Custom SQL query (optional)
        table_name (str): Table name if no custom query provided
        
    Returns:
        pd.DataFrame: Payment data
    """
    
    # Default query if none provided
    if query is None:
        query = f"""
            SELECT 
                id,
                station_id,
                motorcyclist_id,
                source,
                payer_phone,
                fuel_type,
                liter,
                pump_price,
                amount,
                motari_code,
                cashback_wallet_enabled,
                sp_txn_id,
                payment_status,
                payment_method_id,
                created_at,
                updated_at
            FROM {table_name}
            WHERE payment_status IN (200, 500)
            ORDER BY created_at DESC
        """
    
    # Connect and fetch data
    with JalikoiDatabaseConnector(config) as db:
        df = db.fetch_data(query)
    
    return df


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("JALIKOI DATABASE CONNECTOR - TEST SCRIPT")
    print("="*60)
    
    # Import configuration
    try:
        from db_config import DB_CONFIG, PAYMENTS_TABLE, PAYMENTS_QUERY
        
        print("\n1. Testing database connection...")
        connector = JalikoiDatabaseConnector(DB_CONFIG)
        
        if connector.connect():
            print("\n2. Getting table information...")
            connector.get_table_info(PAYMENTS_TABLE)
            
            print(f"\n3. Getting row count...")
            total_rows = connector.get_row_count(PAYMENTS_TABLE)
            success_rows = connector.get_row_count(PAYMENTS_TABLE, "payment_status = 200")
            failed_rows = connector.get_row_count(PAYMENTS_TABLE, "payment_status = 500")
            
            print(f"   Total transactions: {total_rows:,}")
            print(f"   Successful: {success_rows:,}")
            print(f"   Failed: {failed_rows:,}")
            
            print(f"\n4. Testing query with sample data...")
            connector.test_query(PAYMENTS_QUERY, limit=5)
            
            print("\n5. Closing connection...")
            connector.close()
            
            print("\n" + "="*60)
            print("✅ ALL TESTS PASSED!")
            print("="*60)
            print("\nYou can now run the analytics with:")
            print("  python jalikoi_analytics_db.py")
            
        else:
            print("\n❌ Connection failed. Please check your db_config.py")
            
    except ImportError:
        print("\n❌ db_config.py not found!")
        print("\nPlease:")
        print("1. Copy db_config_template.py to db_config.py")
        print("2. Edit db_config.py with your database credentials")
        print("3. Run this script again")
    except Exception as e:
        print(f"\n❌ Error: {e}")
