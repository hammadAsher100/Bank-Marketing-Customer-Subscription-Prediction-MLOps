import os
import yaml
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Load parameters
with open("params.yaml", "r") as f:
    PARAMS = yaml.safe_load(f)

def create_spark_session():
    import platform
    builder = SparkSession.builder \
        .appName(PARAMS["pyspark"]["app_name"] + "_ETL") \
        .config("spark.executor.memory", PARAMS["pyspark"]["executor_memory"]) \
        .config("spark.driver.memory", PARAMS["pyspark"]["driver_memory"])
    
    # Windows-specific configuration to avoid Hadoop issues
    if platform.system() == "Windows":
        builder = builder \
            .config("spark.sql.shuffle.partitions", "4") \
            .config("spark.default.parallelism", "4")
    
    return builder.getOrCreate()

def clean_data(df):
    print("[PySpark ETL] Cleaning data...")
    # Impute unknowns for job and education with mode
    impute_cols = ["job", "education"]
    for col in impute_cols:
        mode_val_row = df.filter(df[col] != "unknown").groupby(col).count().orderBy("count", ascending=False).first()
        mode_val = mode_val_row[0] if mode_val_row else "unknown"
        df = df.withColumn(col, F.when(df[col] == "unknown", mode_val).otherwise(df[col]))
    
    # Drop zero duration
    df = df.filter(df["duration"] > 0)
    
    # Convert target 'y' to binary
    df = df.withColumn("y", F.when(df["y"] == "yes", 1).otherwise(0))
    
    return df

def feature_engineering(df):
    print("[PySpark ETL] Feature engineering...")
    # Calculate avg_duration for is_long_call
    avg_duration_row = df.select(F.mean("duration")).first()
    avg_duration = avg_duration_row[0] if avg_duration_row else 0
    
    # Create new features
    df = df.withColumn("contacted_before", F.when(df["pdays"] != -1, 1).otherwise(0))
    df = df.withColumn("is_long_call", F.when(df["duration"] > avg_duration, 1).otherwise(0))
    
    # pdays_clipped: replace -1 with 0, cap at 900
    df = df.withColumn("pdays_clipped", 
                       F.when(df["pdays"] == -1, 0)
                       .otherwise(F.when(df["pdays"] > 900, 900).otherwise(df["pdays"])))
    
    # call_intensity: log(1 + campaign * duration)
    df = df.withColumn("call_intensity", F.log1p(df["campaign"] * df["duration"]))
    
    # prev_success
    df = df.withColumn("prev_success", F.when(df["poutcome"] == "success", 1).otherwise(0))
    
    return df

def run_etl():
    spark = create_spark_session()
    
    raw_path = PARAMS["data"]["raw_path"]
    sep = PARAMS["data"].get("sep", ";")
    
    print(f"[PySpark ETL] Loading raw data from {raw_path}")
    df = spark.read.csv(raw_path, sep=sep, header=True, inferSchema=True)
    
    df = clean_data(df)
    df = feature_engineering(df)
    
    processed_path = PARAMS["pyspark"]["processed_path"]
    print(f"[PySpark ETL] Saving processed data to {processed_path}")
    
    # Use Pandas CSV write on Windows to avoid Hadoop issues
    import platform
    import pandas as pd
    if platform.system() == "Windows":
        # Convert Spark DataFrame to Pandas and save
        os.makedirs(processed_path, exist_ok=True)
        pdf = df.toPandas()
        csv_file = os.path.join(processed_path, "data.csv")
        pdf.to_csv(csv_file, index=False, sep=",")
        print(f"[PySpark ETL] Data saved as CSV to {csv_file}")
    else:
        df.write.mode("overwrite").parquet(processed_path)
    
    spark.stop()

if __name__ == "__main__":
    run_etl()
