from pyspark.sql.functions import explode, col, lit, trim, lower, to_date, to_timestamp

file_path = "abfss://bronze@sthealthonelakehouseci.dfs.core.windows.net/onedrive_landing/hospitals_departments.json"
df_raw_file = spark.read.option("multiline", "true").json(file_path)


# Explode the 'hospitals' array into separate rows (only hospitals)
df_hospitals_file = df_raw_file.select(explode(col("hospitals")).alias("hospital")).select("hospital.*")

# Trim and convert to lowercase for all string columns in files data
df_hospitals_file = (df_hospitals_file.select(
    col("hospital_id").cast("long"),
    lower(trim(col("name"))).alias("name"),
    lower(trim(col("address"))).alias("address"),
    lower(trim(col("city"))).alias("city"),
    lower(trim(col("region"))).alias("region"),
    col("capacity").cast("int"),
    to_date(col("opened_date"), "yyyy-MM-dd").alias("opened_date"),
    to_timestamp(col("created_at"), "yyyy-MM-dd HH:mm:ss").alias("created_at"),
    to_timestamp(col("updated_at"), "yyyy-MM-dd HH:mm:ss").alias("updated_at")
).withColumn("source", lit("file")) 
    .withColumn("valid_from", col("updated_at"))
    .withColumn("valid_to", lit(None).cast("timestamp"))
    .withColumn("is_current", lit(1).cast("int"))
)


target_path = "abfss://silver@sthealthonelakehouseci.dfs.core.windows.net/corporate_hr/hospitals/"
table_name = "healthone_lakehouse.silver.hospitals"

(df_hospitals_file
    .write
    .format("delta")
    .mode("overwrite")             
    .option("overwriteSchema", "true")  
    .save(target_path)
)


# Register the delta files as a table in Unity Catalog so the team can query it via SQL
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {table_name}
    USING DELTA
    LOCATION '{target_path}'
""")

# Pack small files and group records by hospital_id
# Speeds up daily MERGE queries by skipping files that don't match the incoming IDs
spark.sql(f"""
    OPTIMIZE {table_name}
    ZORDER BY (hospital_id)
""")
