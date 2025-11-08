#!/usr/bin/env python3
"""
Add new API endpoint to get customers in a specific segment
"""

print("="*80)
print("ADDING SEGMENT CUSTOMERS ENDPOINT")
print("="*80)
print()

# Read the API file
with open('jalikoi_analytics_api_ml.py', 'r', encoding='utf-8') as f:
    api_content = f.read()

# Create backup
with open('jalikoi_analytics_api_ml.py.backup_segment_customers', 'w', encoding='utf-8') as f:
    f.write(api_content)

print("✓ Backup created")

# New endpoint code
new_endpoint = '''

@app.get("/api/ml/segment-customers/{segment_name}")
async def get_segment_customers(
    segment_name: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(1000, description="Maximum customers to return")
):
    """
    Get detailed customer list for a specific segment
    
    Returns customer details including phone numbers from motorcyclists table
    """
    if not ML_AVAILABLE or ml_engine.segmentation_model is None:
        raise HTTPException(
            status_code=503,
            detail="Segmentation model not available. Train models first."
        )
    
    try:
        # Determine date range
        today = datetime.now().date()
        if not start_date or not end_date:
            start_date = str(today - timedelta(days=30))
            end_date = str(today)
        
        # Fetch transaction data
        df = engine.fetch_data_from_db(start_date, end_date)
        
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Preprocess and calculate metrics
        df = engine.preprocess_data(df)
        customer_metrics = calc_customer_metrics(df)
        
        # Get segment predictions
        predictions = ml_engine.predict_segments(customer_metrics)
        
        # Filter by segment name
        segment_customers = predictions[predictions['segment_name'] == segment_name]
        
        if len(segment_customers) == 0:
            return {
                "success": True,
                "segment_name": segment_name,
                "total_customers": 0,
                "customers": []
            }
        
        # Get customer IDs
        customer_ids = segment_customers['motorcyclist_id'].tolist()
        
        # Fetch customer details from motorcyclists table
        from database_connector import JalikoiDatabaseConnector
        from db_config import DB_CONFIG
        
        customer_ids_str = ','.join(map(str, customer_ids[:limit]))
        
        customer_query = f"""
            SELECT 
                id as motorcyclist_id,
                motari_phone,
                created_at
            FROM motorcyclists
            WHERE id IN ({customer_ids_str})
            ORDER BY created_at DESC
        """
        
        with JalikoiDatabaseConnector(DB_CONFIG) as db:
            customers_df = db.fetch_data(customer_query)
        
        if customers_df is None or customers_df.empty:
            # If motorcyclists table doesn't have data, return basic info
            customers_list = []
            for _, row in segment_customers.head(limit).iterrows():
                customers_list.append({
                    'motorcyclist_id': int(row['motorcyclist_id']),
                    'motari_phone': 'N/A',
                    'created_at': 'N/A',
                    'ml_segment': int(row['ml_segment'])
                })
        else:
            # Merge with segment data
            merged = segment_customers.merge(
                customers_df,
                on='motorcyclist_id',
                how='left'
            )
            
            customers_list = []
            for _, row in merged.head(limit).iterrows():
                customers_list.append({
                    'motorcyclist_id': int(row['motorcyclist_id']),
                    'motari_phone': str(row['motari_phone']) if pd.notna(row['motari_phone']) else 'N/A',
                    'created_at': str(row['created_at']) if pd.notna(row['created_at']) else 'N/A',
                    'ml_segment': int(row['ml_segment'])
                })
        
        return {
            "success": True,
            "segment_name": segment_name,
            "total_customers": len(segment_customers),
            "customers_returned": len(customers_list),
            "customers": customers_list
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
'''

# Find where to insert (after the segments endpoint)
insert_position = api_content.find('@app.get("/api/ml/anomalies")')

if insert_position == -1:
    print("⚠️  Could not find insertion point")
    print("Looking for alternative position...")
    insert_position = api_content.find('@app.post("/api/ml/train")')

if insert_position == -1:
    print("⚠️  Could not find any ML endpoints")
    print("Manual insertion required")
    print()
    print("Add this code after the @app.get('/api/ml/segments') endpoint:")
    print("-"*80)
    print(new_endpoint)
    print("-"*80)
else:
    # Insert the new endpoint
    api_content_new = (
        api_content[:insert_position] + 
        new_endpoint + 
        '\n\n' +
        api_content[insert_position:]
    )
    
    # Save
    with open('jalikoi_analytics_api_ml.py', 'w', encoding='utf-8') as f:
        f.write(api_content_new)
    
    print("✓ New endpoint added to API")
    print()
    print("Endpoint: GET /api/ml/segment-customers/{segment_name}")
    print()

print()
print("="*80)
print("✅ BACKEND ENDPOINT ADDED!")
print("="*80)
print()
print("Test it:")
print("  curl http://localhost:8000/api/ml/segment-customers/Premium%20VIPs")
print()
print("Next: Update frontend to use this endpoint")
print()
