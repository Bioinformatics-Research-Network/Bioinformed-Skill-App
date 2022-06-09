import time
from sync import sync_assessments, download_releases_from_github, upload_releases_to_aws
from config import settings

def lambda_handler(event, context):
    if context:
        print("Lambda function ARN:", context.invoked_function_arn)
        print("CloudWatch log stream name:", context.log_stream_name)
        print("CloudWatch log group name:",  context.log_group_name)
        print("Lambda Request ID:", context.aws_request_id)
        print("Lambda function memory limits in MB:", context.memory_limit_in_mb)
        # We have added a 1 second delay so you can see the time remaining in get_remaining_time_in_millis.
        time.sleep(1) 
        print("Lambda time remaining in MS:", context.get_remaining_time_in_millis())
    
    # Run all sync functions
    print("Syncing assessments")
    sync_assessments()
    print("Syncing badges")
    print("Syncing code")
    download_releases_from_github(settings=settings)
    upload_releases_to_aws(settings=settings)


if __name__ == "__main__":
    lambda_handler(None, None)
