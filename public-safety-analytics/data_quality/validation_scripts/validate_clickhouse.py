import clickhouse_connect
import sys

def run_validation():
    print("========================================")
    print(" Public Safety Data Quality Validation")
    print("========================================\n")
    
    try:
        client = clickhouse_connect.get_client(
            host="localhost", 
            port=8123, 
            username="clickhouse", 
            password="clickhouse",
            database="public_safety"
        )
    except Exception as e:
        print(f" Failed to connect to ClickHouse: {e}")
        sys.exit(1)

    print(" Connected to ClickHouse")
    passed = True

    count_query = "SELECT COUNT(*) FROM fact_incidents"
    total_rows = client.query(count_query).result_set[0][0]
    print(f"\n Total Rows in fact_incidents: {total_rows:,}")
    if total_rows == 0:
        print(" FAILED: Fact table is empty!")
        passed = False
    else:
        print(" PASSED: Fact table has data.")

    null_query = """
        SELECT COUNT(*) 
        FROM fact_incidents 
        WHERE incident_id IS NULL OR type_id IS NULL OR location_id IS NULL OR incident_date IS NULL
    """
    null_count = client.query(null_query).result_set[0][0]
    print(f"\nnull count: {null_count}")
    if null_count > 0:
        print(f" FAILED: Found {null_count} records with null primary/foreign keys or dates.")
        passed = False
    else:
        print(" PASSED: No null critical fields inserted.")

    coord_query = """
        SELECT COUNT(*)
        FROM fact_incidents
        WHERE (latitude < 20.0 OR latitude > 50.0) 
           OR (longitude < -130.0 OR longitude > -60.0)
    """
    out_of_bounds = client.query(coord_query).result_set[0][0]
    if out_of_bounds > 0:
        print(f" WARNING: Found {out_of_bounds} records with out-of-bounds coordinates (assuming US data).")
    else:
        print(" PASSED: Latitude and Longitude values are within expected ranges.")

    print("\n========================================")
    if passed:
        print(" ALL CRITICAL DATA QUALITY CHECKS PASSED!")
    else:
        print(" SOME CHECKS FAILED. PLEASE REVIEW PIPELINE.")
    print("========================================\n")

if __name__ == "__main__":
    run_validation()
