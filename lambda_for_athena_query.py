import boto3

ATHENA_DATABASE = 'adtech_db'
ATHENA_OUTPUT = 's3://adtech-reporting-data/athena_processed/'

def lambda_handler(event, context):
    client = boto3.client('athena')
    
    response = client.start_query_execution(
        QueryString="MSCK REPAIR TABLE processed_campaign_data;",
        QueryExecutionContext={'Database': ATHENA_DATABASE},
        ResultConfiguration={'OutputLocation': ATHENA_OUTPUT}
    )
    
    return {
        'statusCode': 200,
        'body': f"Started Athena query: {response['QueryExecutionId']}"
    }

