import json
import boto3
import urllib.parse

glue = boto3.client('glue')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        file_path = f"s3://{bucket}/{key}"

        print(f"New file detected: {file_path}")

        # Start Glue job with file path as parameter
        response = glue.start_job_run(
            JobName='ad-tech-glue',
            Arguments={
                '--file_path': file_path
            }
        )
        print("Started Glue job:", response['JobRunId'])
    
    return {
        'statusCode': 200,
        'body': json.dumps('Glue job triggered successfully')
    }
