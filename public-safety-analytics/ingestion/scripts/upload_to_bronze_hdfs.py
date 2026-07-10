import subprocess
import sys

def run_command(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f" Error executing command:\n{result.stderr}")
        sys.exit(result.returncode)
    else:
        print(f" Success:\n{result.stdout}")

def main():
    print("=" * 80)
    print(" UPLOADING LOCAL PARQUET TO HDFS BRONZE LAYER")
    print("=" * 80)

    local_file_path = "/home/jovyan/bronze_layer/raw_data_2025/combined_2025_data_2025.parquet"
    
    hdfs_bronze_dir = "hdfs://namenode:9000/user/hive/warehouse/bronze/crime_api/2025"
    hdfs_file_path = f"{hdfs_bronze_dir}/combined_2025_data_2025.parquet"

    print(f"\n1️ Creating HDFS directory: {hdfs_bronze_dir}")
    run_command(f"hdfs dfs -mkdir -p {hdfs_bronze_dir}")

    print(f"\n2️ Uploading local file to HDFS")
    print(f"   Source: {local_file_path}")
    print(f"   Destination: {hdfs_file_path}")
    run_command(f"hdfs dfs -put -f {local_file_path} {hdfs_file_path}")

    print(f"\n3️ Verifying upload...")
    run_command(f"hdfs dfs -ls {hdfs_file_path}")

    print("\n UPLOAD COMPLETE!")

if __name__ == "__main__":
    main()
