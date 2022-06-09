# Skill App Sync

**Maintainer**: @millerh1

This is an AWS Lambda function which will sync the data sources for the BRN Skill App. It will trigger once every 6 hours and synchronize data across multiple sources with the BRN database:

1. Airtable
  - Update `assessment` table with the latest assessments
2. GitHub
  - Uses `assessment` table to figure out the latest release -- downloads the release code from github and uploads it to AWS S3 buckets for use by the bot.
3. Badgr
  - New and updated badges / assertions are discovered using the badgr API -- then the `badges` and `assertions` tables are updated accordingly.

## Dev notes

**Before you begin**: You will need to request the `.env` file from @millerh1 -- otherwise you will be unable to run this code successfully.

### Getting started

This service is meant to be deployed as a function on [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html) using a Docker container with Python 3.9. 

The layout of this repo follows the conventions used by aws lambda. The main software environment is in the `sync/` directory. Therefore, to get started, do the following:

1. Clone this repo
2. Request the `.env` file from @millerh1 and add it to the root of this git repo.
3. Change to the `sync/` directory:

```shell
cd sync/
```

4. Create a `venv` from `requirements.txt`:

```shell
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. Run the sync function locally using the command line:

```shell
python3 handler.py
```

This will run the full sync function and update all databases. 

This is a non-destructive action, so no databases will be harmed.

#### Testing code in a production-like environment

Running `python handler.py` is a convenient way to test code locally. However, running the function this way does not always show how the code will behave once deployed. 

To test the code in a realistic environment, use [Docker](https://www.docker.com/).

1. Download Docker and install
2. Once you feel comfortable with using docker from the command line, build the image:

```shell
docker build -t skill-app-sync .
```

3. Then, run the image (exposing localhost port 9000). This will expose the lambda server which will start listening for trigger events.

```shell
docker run -p 9000:8080 skill-sync
```

4. Open a **second terminal** and send it a trigger event (POST request). *Note*: you can also just run step 3 in headless mode (`-d`) and then reuse the same terminal window.

```shell
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

This should cause the entire sync workflow to trigger successfully. Address any errors before deploying a new version to production.


### Deployment

This is the approach @millerh1 used to deploy this function to AWS Lambda for the first time (if you want to do the same, you will need aditional AWS access -- ask @millerh1). 

<details>
<summary>Initial deployment</summary>


These steps are adapted from [this article](https://medium.com/geekculture/3-ways-to-overcome-aws-lambda-deployment-size-limit-part-2-8d0e8d0264b0).


#### Pushing the build image to AWS ECR

1. Download the aws cli toolkit and configure for your profile (@millerh1 uses a profile called `brn` for all steps shown here)

2. Set the working dir to `sync/` if you haven't already done so.

```shell
cd sync/
```

3. Build the latest docker image.

```shell
docker build -t skill-sync .
```

4. Create an AWS ECR repository (step was already completed by @millerh1) so you don't need to do this again.

```shell
aws ecr create-repository --profile brn --repository-name skill-app-sync --region us-east-1
```

The above command returns the URI for our images: `346542362226.dkr.ecr.us-east-1.amazonaws.com/skill-app-sync`

5. Tag the local image with the URI

```shell
docker tag skill-app-sync:latest 346542362226.dkr.ecr.us-east-1.amazonaws.com/skill-app-sync:latest
```

6. Authenticate docker to enable pushing local images to the AWS container repository (ECR)

```shell
aws ecr get-login-password --region us-east-1 --profile brn | docker login --username AWS --password-stdin 346542362226.dkr.ecr.us-east-1.amazonaws.com/skill-app-sync
```

7. Push the image to the registry

```shell
docker push 346542362226.dkr.ecr.us-east-1.amazonaws.com/skill-app-sync:latest
```


#### Setting up AWS Lambda function and scheduled trigger


1. Create an execution role for AWS lambda.

```shell
aws iam create-role --role-name lambda-ex --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}' --profile brn
```

This creates an ARN: `arn:aws:iam::346542362226:role/lambda-ex`

2. Attach deploy permissions to the new role:

```shell
aws iam attach-role-policy --role-name lambda-ex --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

3. Create the lambda function

```shell
aws lambda create-function --region us-east-1 --profile brn --function-name skill-app-sync --code ImageUri=346542362226.dkr.ecr.us-east-1.amazonaws.com/skill-app-sync:latest --role arn:aws:iam::346542362226:role/lambda-ex --package-type Image --timeout 600 --memory-size 512
```

4. Follow [this guide](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-run-lambda-schedule.html) to create a rule that triggers our lambda function once every 6 hours. Rule created by @millerh1 is called `run-skill-app-sync`.


</details>


To update the existing lambda function, simply do the following:


1. Download the aws cli toolkit and configure for your profile
2. Set the working dir to `sync/` if you haven't already done so.

```shell
cd sync/
```

3. Build the latest docker image using

```shell
docker build -t skill-app-sync:latest .
```

4. Authenticate docker to enable pushing local images to the AWS container repository (ECR)

```shell
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 346542362226.dkr.ecr.us-east-1.amazonaws.com/skill-app-sync
```

5. Tag the local image with the URI for the AWS container repository

```shell
docker tag skill-app-sync:latest 346542362226.dkr.ecr.us-east-1.amazonaws.com/skill-app-sync:latest
```

6. Push the image to the registry

```shell
docker push 346542362226.dkr.ecr.us-east-1.amazonaws.com/skill-app-sync:latest
```

7. Now update the lambda function to trigger using the new version of the image.

```shell
aws lambda update-function-code --region us-east-1 --function-name skill-app-sync --image-uri 346542362226.dkr.ecr.us-east-1.amazonaws.com/skill-app-sync:latest
```

Now, your function should automatically run using the latest version of the code!

