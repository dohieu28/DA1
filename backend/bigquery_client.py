from google.cloud import bigquery
from config import GOOGLE_CLOUD_PROJECT, BIGQUERY_DATASET

client = bigquery.Client(project=GOOGLE_CLOUD_PROJECT)
dataset_ref = f"{GOOGLE_CLOUD_PROJECT}.{BIGQUERY_DATASET}"

def insert_raw_csi(csi_data):
    table_id = f"{dataset_ref}.raw_csi"
    rows_to_insert = [csi_data]
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"Errors inserting raw CSI: {errors}")
    else:
        print("Raw CSI data inserted into BigQuery")

def insert_position(position):
    table_id = f"{dataset_ref}.positions_cloud"
    rows_to_insert = [position]
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"Errors inserting position: {errors}")
    else:
        print("Position data inserted into BigQuery")

def get_position_history(mac, limit=10):
    query = f"""
        SELECT mac, x, y, timestamp
        FROM `{dataset_ref}.positions_cloud`
        WHERE mac = @mac
        ORDER BY timestamp DESC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("mac", "STRING", mac),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()
    return [{"mac": row.mac, "x": row.x, "y": row.y, "timestamp": str(row.timestamp)} for row in results]

def get_references():
    query = f"""
        SELECT reference_id, type, name, x, y, radius
        FROM `{dataset_ref}.map_references`
    """
    query_job = client.query(query)
    results = query_job.result()
    return [{"reference_id": row.reference_id, "type": row.type, "name": row.name, "x": row.x, "y": row.y, "radius": row.radius} for row in results]

def get_users():
    query = f"""
        SELECT user_id, username, role_id
        FROM `{dataset_ref}.users`
    """
    query_job = client.query(query)
    results = query_job.result()
    return [{"user_id": row.user_id, "username": row.username, "role_id": row.role_id} for row in results]

def get_devices():
    query = f"""
        SELECT device_id, mac, name, status
        FROM `{dataset_ref}.devices`
    """
    query_job = client.query(query)
    results = query_job.result()
    return [{"device_id": row.device_id, "mac": row.mac, "name": row.name, "status": row.status} for row in results]

def get_performance():
    query = f"""
        SELECT AVG(rssi) as avg_rssi, COUNT(*) as total_records
        FROM `{dataset_ref}.raw_csi`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
    """
    query_job = client.query(query)
    results = query_job.result()
    row = next(results)
    return {"avg_rssi": row.avg_rssi, "total_records": row.total_records}