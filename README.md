# Skill App Sync

**Maintainer**: @millerh1

This is an AWS Lambda function which will sync the data sources for the BRN Skill App. 

Data sources:

1. Airtable
  - Assessment table
2. GitHub
  - Assessment code in releases will be uploaded to AWS S3 buckets
3. Badgr
  - Badges and assertions

## Dev notes

### Getting started

This service is meant to be deployed as a function on [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html) in a Python 3.9 environment. Therefore, the layout follows the conventions used by aws lambda. The main software environment is in the `sync/` directory. Therefore, to get started, do the following:

1. Clone this repo
2. Request the `.env` file from @millerh1 and add it to the root of this git repo.
3. `cd` into the `sync` directory
4. Create a `venv` from `requirements.txt`:

```shell
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Run the sync function using the command line:

```shell
python3 handler.py
```

This will run the full sync function and update all databases. 

This is a non-destructive action and will not harm anything.

### Deployment

This is the approach @millerh1 uses to deploy this function to AWS Lambda (ask him if you need access to do likewise):

1. Download the aws cli toolkit and configure correctly (@millerh1 uses a profile `brn`)
2. Create an execution role for AWS lambda:

```shell
aws iam create-role --role-name lambda-ex --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}' --profile brn
```

3. Attach deploy permissions to the new role:

```shell
aws iam attach-role-policy --role-name lambda-ex --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

4. Create a zip file archive of the `sync/` folder (must have `.venv/` created in it)

```shell
cd sync/ && zip ../skill-app-sync.zip -r * .[^.]* -x "*cache*" -x "*instance*" -x "*vscode*" -x "*.git*" -x "*.ebextensions*" -x "*.elasticbeanstalk/logs*" && cd ..
```

5. Upload to AWS

```shell
aws s3 cp --profile brn --region us-east-1 skill-app-sync.zip s3://skill-assessment-app/lambda_functions/skill-app-sync.zip
```


5. Create the lambda function

```shell
aws lambda create-function --function-name sync3 \
--code '{"S3Bucket": "skill-assessment-app", "S3Key": "lambda_functions/skill-app-sync.zip"}' \
--handler handler.lambda_handler --runtime python3.9 \
--role arn:aws:iam::<aws id>:role/lambda-ex --profile brn --region us-east-1
```


