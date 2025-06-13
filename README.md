# 📊 Scalable Ad Campaign Analytics Pipeline :

Develop a scalable, modular data pipeline to fetch campaign delivery data from mock APIs, transform and store it efficiently, and visualize performance through interactive, geo-filtered dashboards.

# 🧭 Overview :

This project provides an end-to-end analytics solution by:

  1. Ingesting mock ad data via APIs
  2. Performing transformation and enrichment of data
  3. Modeling data using Athena using SQL queries for futher analysis
  4. Visualizing results via interactive dashboards on streamlit

# 🧰 Features :

  1. 🔁 Automated ETL: Ingest → Clean → Model → Visualize
  2. 🌍 Geo-Filtered Insights: Filter performance by country, state, city, or ZIP
  3. 📈 Marketing KPIs: Compute CTR, CPC, CPM, and Conversion Rate fro more insights
  4. 🔄 Incremental Updates: Automatically processes new data via S3 triggers
  5. 📦 Data Format: Converting raw JSON to processed Parquet for efficiency

# ⚙️ Technical Stack :

  Languages
  
  1. Python
  2. sql
  3. Pyspark

  AWS Services

  1.  AWS Lambda (serverless compute)
  2.  Amazon API Gateway (HTTP triggers)
  3.  Amazon S3 (data lake)
  4.  AWS Glue (ETL jobs)
  5.  Amazon Athena (SQL querying)
  6.  Amazon QuickSight / Streamlit (dashboards)
  7.  AWS EventBridge (scheduler)
  8.  Amazon CloudWatch (monitoring)
  9.  AWS IAM (role-based access)

# Architecture Diagram

![Architechture_diagram](https://github.com/zayconik/adtech_project/blob/main/Architechture.png)


# Steps : 

## 🔍 Data Generation & Insights & Relationships :

A script is created using Flask API for generating mock json data .Hosted the API on railway 

    https://adtechmockapi-production.up.railway.app/campaign-data

  ### 1. Campaign id → Ad id Relationship :

  1. Each campaign_id is associated with multiple ad_ids.
  2. This reflects real-world scenarios where a single marketing campaign runs several creatives to test and optimize performance.

  ### 2. Ad ID → Brand Mapping :

  1. Each ad_id belongs to a single brand, which remains consistent regardless of the campaign it appears in.
  2. This enables brand-level performance analysis, such as identifying top-performing creatives for a brand.
     
  ### 3. Geographical Distribution :

  1. Ads are shown in different countries, states, cities, and zip codes.
  2. Each record contains full location context, allowing for granular geo-based analytics (e.g., regional CTR, CPM, conversion rate).

## 📷 Sample Data:

    {
      "campaign_id": "cmp123",
      "ad_id": "ad001",
      "date": "2024-05-20",
      "brand": "BrandA",
      "country": "US",
      "state": "California",
      "city": "Los Angeles",
      "zipcode": "90001",
      "impressions": 10000,
      "clicks": 350,
      "spend": 275.50,
      "conversions": 20
    }

## 🛠️ Data Ingestion :

  ### AWS Lambda Function (Ingestion Script) :

  Using severless function 
  
  1. Calls the mock API
  2. Calls the mock API
  3. Stores the raw data in Amazon S3 under the raw/ prefix

  ### Trigger Mechanisms :

  1. On-Demand via API Gateway (HTTP call)
  2. Scheduled using EventBridge (e.g., every hour)

  ### Storage in Amazon S3 :
  
  1. The Lambda function writes each incoming JSON response into a uniquely named folder ( Folder structure /raw/{date}/{UTC timestamp}.
  2. This raw data is unprocessed and will be used later for transformation.

## 🔄 Data Transformation & Automation :

### 🧹 Data Transformation with AWS Glue :

A serverless AWS Glue job is responsible for transforming the raw JSON files stored in S3 into clean, enriched Parquet datasets ready for analysis.

  ### Key Steps in the Glue Job:

  1. Null Handling

     | Column        | Null Handling Strategy | 
     |---------------|------------------------|
     | campaign_id   |   "unknown_campaign"   |
     | ad_id         |      "unknown_ad"      |
     | date        |      Replace with current date      |
     | brand        |      "Unknown"      |
     | country        |      "Unknown"      |
     | state        |      "Unknown"      |
     | city         |      "Unknown"      |
     | Zipcode        |      "0000"      |
     | impressions|      Drop the row     |
     | Cilcks        |       Drop the row    |
     | Conversion        |       Drop the row     |
     | Spend       |       Take the median value     |

2. Logical Filtering :

   Removes rows where business logic doesn’t hold :
   
        conversions ≤ clicks ≤ impressions
3. Spend Imputation (Hierarchical Median Strategy) :

   If spend is null, it's imputed using the most granular median available :

   1. Median by (ad_id, country)
   2. Median by ad_id
   3. Median by (brand, country)
   4. Median by brand
   5. Rows with no valid median are dropped

4. Derived Metric Computation :

   1. CTR = clicks / impressions
   2. CPC = spend / clicks
   3. CPM = (spend / impressions) × 1000
   4. Conversion Rate = conversions / clicks

## ⚙️ Automation with AWS Lambda :

To make the transformation process automatic, an AWS Lambda function is configured to trigger every time a new file arrives in the S3 raw/ folder.

1. Event Source :
   
    Triggered by S3 event notification on file upload.
   
3. Dynamic File Detection :

    Extracts file path from the event payload.


5. Glue Job Trigger :

   Launches the Glue job (ad-tech-glue) with the new file path as a parameter.

## 🧾 Athena Data Modeling :

After the data is cleaned and transformed using AWS Glue, it is stored as partitioned Parquet files in S3. Amazon Athena is used to query this data using standard SQL, enabling fast, serverless analytics without requiring a data warehouse setup.

  1. Main Table: processed_campaign_data :
     
     This external table is defined over the processed/ S3 location where Glue outputs the cleaned data.

     
  2. Logical Views :

     1. campaign_summary

        1. Gives aggregated insights per campaign_id
        2. Sums overall spends for particular ad_id
          
                CREATE OR REPLACE VIEW "campaign_summary" AS 
                SELECT
                campaign_id
                , SUM(impressions) total_impressions
                , SUM(clicks) total_clicks
                , SUM(spend) total_spend
                , SUM(conversions) total_conversions
                , (CASE WHEN (SUM(impressions) > 0) THEN ((SUM(clicks) * 1E0) / SUM(impressions)) ELSE 0 END) ctr
                , (CASE WHEN (SUM(clicks) > 0) THEN ((SUM(spend) * 1E0) / SUM(clicks)) ELSE 0 END) cpc
                , (CASE WHEN (SUM(impressions) > 0) THEN (((SUM(spend) * 1E0) / SUM(impressions)) * 1000) ELSE 0 END) cpm
                , (CASE WHEN (SUM(clicks) > 0) THEN ((SUM(conversions) * 1E0) / SUM(clicks)) ELSE 0 END) conversion_rate
                FRO
                processed_campaign_data
                GROUP BY campaign_id

     2. campaign_performance
    
        1. Geo-level breakdown: Country → State → City → Zip
        2. Helps identify high/low-performing regions

                CREATE OR REPLACE VIEW "campaign_performance" AS 
                SELECT
                campaign_id
                , brand
                , country
                , state
                , city
                , zipcode
                , date
                , SUM(impressions) impressions
                , SUM(clicks) clicks
                , SUM(conversions) conversions
                , SUM(spend) spend
                , (CASE WHEN (SUM(impressions) > 0) THEN ((SUM(clicks) * 1E0) / SUM(impressions)) ELSE 0 END) ctr
                , (CASE WHEN (SUM(clicks) > 0) THEN (SUM(spend) / SUM(clicks)) ELSE 0 END) cpc
                , (CASE WHEN (SUM(impressions) > 0) THEN (SUM(spend) / (SUM(impressions) / 1000)) ELSE 0 END) cpm
                , (CASE WHEN (SUM(clicks) > 0) THEN ((SUM(conversions) * 1E0) / SUM(clicks)) ELSE 0 END) conversion_rate
                FROM
                adtech_db.processed_campaign_data
                GROUP BY campaign_id, brand, country, state, city, zipcode, date

     3. creative_performance
    
        1. Insights at Ad_ID level
        2. Metrics: Impressions, Clicks, Spend, CTR, CPC, CPM

                CREATE OR REPLACE VIEW "creative_performance" AS 
                SELECT
                ad_id
                , campaign_id
                , brand
                , country
                , state
                , city
                , zipcode
                , date
                , SUM(impressions) impressions
                , SUM(clicks) clicks
                , SUM(conversions) conversions
                , SUM(spend) spend
                , (CASE WHEN (SUM(impressions) > 0) THEN ((SUM(clicks) * 1E0) / SUM(impressions)) ELSE 0 END) ctr
                , (CASE WHEN (SUM(clicks) > 0) THEN (SUM(spend) / SUM(clicks)) ELSE 0 END) cpc
                , (CASE WHEN (SUM(impressions) > 0) THEN (SUM(spend) / (SUM(impressions) / 1000)) ELSE 0 END) cpm
                , (CASE WHEN (SUM(clicks) > 0) THEN ((SUM(conversions) * 1E0) / SUM(clicks)) ELSE 0 END) conversion_rate
                FROM
                adtech_db.processed_campaign_data



# 📊 ETL Flow Diagram :

          Mock API → Lambda (Ingestion) → S3 (raw/)
                       ↓
                S3 Event Notification
                       ↓
          Lambda (Trigger Glue) → AWS Glue (Transform)
                       ↓
              S3 (processed/ in Parquet)
                       ↓
                Athena Table + Views
                       ↓
                Streamlit  Dashboards


# Live DashBoard :

## 1. Campaign summary dashboard :
   ![Campaign summary_diagram](https://github.com/zayconik/adtech_project/blob/main/Campaign_summary.png)


## 2. Creative performance dashboard :
   ![Creative performance_diagram](https://github.com/zayconik/adtech_project/blob/main/Creative_performance.png)

   
## 3. Daily Campaign Performance :
   ![Creative performance_diagram](https://github.com/zayconik/adtech_project/blob/main/Daily_campaign_performance.png)



# 🚀 Future Enhancements :

1. 💾 Metadata Storage in DynamoDB
2. 📬 SNS Notifications
3. 🧪 Redshift Support




  





    
