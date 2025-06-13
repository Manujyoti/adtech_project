import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col, round, lit, when, to_date, expr, current_date
from pyspark.sql.types import DoubleType

# Parse input arguments
args = getResolvedOptions(sys.argv, ['file_path'])
input_path = args['file_path']
#input_path = "s3://adtech-reporting-data/raw/2025-06-12/12-06/campaign_data.json"
parts = input_path.split('/')
date_str = parts[-3]
time_str = parts[-2]

# Glue setup
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Read data
df = spark.read.json(input_path)
if df.rdd.isEmpty():
    print(f"No data found at: {input_path}")
    sys.exit(0)

# Ensure ad_id and campaign_id are string
df = df.withColumn("ad_id", col("ad_id").cast("string"))
df = df.withColumn("campaign_id", col("campaign_id").cast("string"))

# Cast spend to double
df = df.withColumn("spend", col("spend").cast(DoubleType()))

# Drop rows if impressions, clicks, conversions are null
df = df.filter(col("impressions").isNotNull() & col("clicks").isNotNull() & col("conversions").isNotNull())

# Fill remaining nulls (not spend)
df = df.fillna({
    "campaign_id": "unknown_campaign",
    "ad_id": "unknown_ad",
    "brand": "Unknown",
    "country": "Unknown",
    "state": "Unknown",
    "city": "Unknown",
    "zipcode": "000000"
})

# Handle null dates with current_date()
df = df.withColumn("date", to_date(when(col("date").isNotNull(), col("date")).otherwise(current_date())))

# Filter out invalid logic rows
df = df.filter((col("impressions") > 0) & (col("clicks") > 0))
df = df.filter((col("clicks") <= col("impressions")) & (col("conversions") <= col("clicks")))

# ====== Spend Imputation Strategy ======
# 1. Median by (ad_id, country)
med1 = df.filter(col("spend").isNotNull()) \
    .groupBy("ad_id", "country") \
    .agg(expr("percentile_approx(spend, 0.5)").alias("med1"))
df = df.join(med1, on=["ad_id", "country"], how="left")

# 2. Median by ad_id
med2 = df.filter(col("spend").isNotNull()) \
    .groupBy("ad_id") \
    .agg(expr("percentile_approx(spend, 0.5)").alias("med2"))
df = df.join(med2, on="ad_id", how="left")

# 3. Median by (brand, country)
med3 = df.filter(col("spend").isNotNull()) \
    .groupBy("brand", "country") \
    .agg(expr("percentile_approx(spend, 0.5)").alias("med3"))
df = df.join(med3, on=["brand", "country"], how="left")

# 4. Median by brand
med4 = df.filter(col("spend").isNotNull()) \
    .groupBy("brand") \
    .agg(expr("percentile_approx(spend, 0.5)").alias("med4"))
df = df.join(med4, on="brand", how="left")

# Impute spend or drop
df = df.withColumn(
    "spend",
    when(col("spend").isNotNull(), col("spend"))
    .when(col("med1").isNotNull(), col("med1"))
    .when(col("med2").isNotNull(), col("med2"))
    .when(col("med3").isNotNull(), col("med3"))
    .when(col("med4").isNotNull(), col("med4"))
)

# Drop still-null spend
df = df.filter(col("spend").isNotNull())

# Drop temp medians
df = df.drop("med1", "med2", "med3", "med4")

# ====== Derived Metrics ======
df = df.withColumn("CTR", round(col("clicks") / col("impressions"), 4))
df = df.withColumn("CPC", round(col("spend") / col("clicks"), 2))
df = df.withColumn("CPM", round((col("spend") / col("impressions")) * 1000, 2))
df = df.withColumn("conversion_rate", round(col("conversions") / col("clicks"), 4))

# ====== Partition Info ======
df = df.withColumn("partition_date", lit(date_str)) \
       .withColumn("partition_time", lit(time_str))

# ====== Write to S3 in Parquet Format ======
output_path = "s3://adtech-reporting-data/processed/"
df.write.mode("append").partitionBy("partition_date", "partition_time").parquet(output_path)

print(f" Written to: {output_path} with partition_date={date_str}, time={time_str}")