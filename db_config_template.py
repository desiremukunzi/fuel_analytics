# Configuration template for database connection
# Copy this file to db_config.py and fill in your actual credentials

DB_CONFIG = {
    'host': 'your-database-host.com',
    'port': 3306,
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database_name'
}

PAYMENTS_QUERY = """
    SELECT 
        id, station_id, motorcyclist_id, source, payer_phone,
        fuel_type, liter, pump_price, amount, motari_code,
        cashback_wallet_enabled, sp_txn_id, payment_status,
        payment_method_id, created_at, updated_at
    FROM DailyTransactionPayments
    WHERE payment_status IN (200, 500)
    ORDER BY created_at DESC
"""
