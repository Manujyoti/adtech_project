import json
import requests
import boto3
from datetime import datetime
import pytz

BUCKET_NAME ='adtech-reporting-data'  #  replace with your actual S3 bucket name
API_URL = 'https://adtechmockapi-production.up.railway.app/campaign-data'  

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Step 1: Fetch the data
    response = requests.get(API_URL)
    data = response.json()  # Should be a list of dicts

    # Step 2: Generate folder path
    now = datetime.utcnow()
    date_str = now.strftime('%Y-%m-%d')     
    time_str = now.strftime('%H-%M')         
    folder_path = f"raw/{date_str}/{time_str}/"
    file_key = f"{folder_path}campaign_data.json"

    # Step 3: Convert to JSON Lines (NDJSON)
    json_lines = "\n".join(json.dumps(record) for record in data)

    # Step 4: Upload to S3

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Body=json_lines,
        ContentType='application/json'
    )

    return {
        'statusCode': 200,
        'body': f" JSON Lines written to S3: {file_key}"
    }