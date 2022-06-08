# Developer notes

![Build Status](https://github.com/Bioinformatics-Research-Network/BRN-bot/workflows/tests/badge.svg) [![codecov](https://codecov.io/gh/Bioinformatics-Research-Network/BRN-bot/branch/main/graph/badge.svg?token=64FAWBD72C)](https://codecov.io/gh/Bioinformatics-Research-Network/BRN-bot)

Primary maintainer: Henry Miller

This README contains notes to aid contributors and maintainers for this repo. It's a living document, so feel free to suggest changes any time. 

This is a GitHub app which can be installed at the organization level via: https://github.com/apps/brn-bot

## Dev notes

### Quick start

Here are the steps required for setting up and launching the BRN bot

1. Clone repo

```shell
git clone git@github.com:Bioinformatics-Research-Network/BRN-bot.git
```

2. Switch to your branch (do not commit / push to main)

```shell
git checkout -b <name_of_branch>
```

3. Install nodejs & smee

```shell
curl -sL https://deb.nodesource.com/setup_16.x -o /tmp/nodesource_setup.sh
sudo bash /tmp/nodesource_setup.sh
sudo apt install nodejs
sudo npm install -g smee-client
```

4. Start smee channel

```shell
smee -u https://smee.io/rSiwWHyU4AMt1zn --port 8001
```

5. Use pip, venv, and the `requirements.txt` file (make sure you have python3.10 or higher installed)

```shell
# Install python3.10-venv if you have not already...
# sudo apt install python3.10-venv

python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

6. Set environment (ask Henry for these)

```shell
export APP_ENV=development
export BOT_KEY_PATH="brn_bot_dev.pem"
```

7. Run unit tests

```shell
pytest
```

8. Launch the app

```shell
uvicorn main:app --reload --port 8001
```

9. Try it out by navigating to the [test repo PR](https://github.com/Bioinformatics-Research-Network/test-bot/pull/1) and writing "@brnbot hello" in the PR comments. You should see a response from BRN bot which says "Hello <your_gh_username>! 😊". For a list of all available commands, type "@brnbot help".


### Other notes and considerations

1. You can add new deps to the poetry env by running `poetry add <package_name>`
2. The app must be installed by GitHub organizations to be used. As each skill assessment has its own organization (e.g., Python Programming II), the bot has to be installed separately for each. After this is done, the *Install ID* must be registered in `bot/const.py` within the `installation_ids` object. You can obtain the installation ID for an organization by commenting on a PR/Issue in that org and getting the [webhook output from smee.io](https://smee.io/rSiwWHyU4AMt1zn) -- the install ID is in the event payload under `{"installation": {"id": <id_number>}}`


## Workflow for contributing:

All the work for this project has been modularized into relatively independent [issues](https://github.com/Bioinformatics-Research-Network/Skill-cert-bot/issues). If you see one which you would like to complete and it has no assignees, feel free to just add yourself as an assignee and get started. 

1. You are assigned an issue (or you self-assign)
2. Set up your dev environment using *** (this part needs to be figured out still)
3. Switch to your own branch (please do not work on the `main` branch unless you are the primary maintainer)
4. If developing new modules or functions, start by writing pytest unit tests in the `tests/` folder. It is good practice to write all unit tests prior to writing the modules which they test. That way, the expected behavior is clearly defined prior to writing the module code. 
5. Commit changes to your branch and push to github. It is recommended to do this at the end of a coding session to avoid potentially losing your progress.
6. Once your feature / module is ready, submit a pull request to pull your branch into `main`. The maintainer will review your code prior to merging it. 



### Deployment

Before the app could be set up for rapid deployment, it first had to be initialized on AWS Elastic Beanstalk. These steps outline what Henry did to accomplish that:

<details>
<summary>Preliminary steps on AWS EB</summary>

Prior to deploying the application for the first time, Henry performed all the following steps to ensure correct configuration:

1. Created an OAuth GitHub app within the Bioinformatics Research Network GitHub org to handle authentication to the Web UI. Homepage URL: https://skill.bioinformed.app/ -- callback URL: https://skill.bioinformed.app/login/github/authorized
2. Registered a domain name (bioinformed.app) using Google Domains
3. Routed the domain to AWS Route 53 using [this guide](https://www.entechlog.com/blog/aws/connect-google-domain-to-aws-route-53/). Specifically, he created a Route 53 hosted zone for 'bioinformed.app'. This generated the `NS` records which he added as custom nameservers in the Google Domain record for bioinformed.app.
4. Used AWS Certificate Manager to register SSL certificates for 'bioinformed.app', 'learn.bioinformed.app', 'www.bioinformed.app', and 'skill.bioinformed.app'. These certificates were then added to the hosted zone as CNAME records.
5. Export poetry deps to requirements.txt

```bash
poetry export --without-hashes -o requirements.txt
```

5. Created a ZIP file of the application, ignoring unnecessary files:

```bash
zip skill-app-ghbot.zip -r * .[^.]* -x "*cache*" -x "*venv*" -x "*instance*" -x "*vscode*" -x "*.git*" -x "*.ebextensions*" -x "*.elasticbeanstalk/logs*" -x "Dockerfile.dev"
```

6. Installed the awsebcli package: [link](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install-advanced.html)
7. then created a new environment ("skill-app-production") within that application. Uploaded code in the ZIP file and added version tag v0.0.1. Also added custom configuration to enable an Application load balancer (modify capacity to allow load balancing, then add application load balancer) similar to [this guide](https://docs.amazonaws.cn/en_us/elasticbeanstalk/latest/dg/environments-cfg-nlb.html). 

7. Initialize an elastic beanstalk application with the appropriate settings (`--profile brn` is only necessary if you have multiple AWS CLI profiles):

```bash
$ eb init -i --profile brn

Select a default region
1) us-east-1 : US East (N. Virginia)
2) us-west-1 : US West (N. California)
3) us-west-2 : US West (Oregon)
4) eu-west-1 : EU (Ireland)
5) eu-central-1 : EU (Frankfurt)
6) ap-south-1 : Asia Pacific (Mumbai)
7) ap-southeast-1 : Asia Pacific (Singapore)
8) ap-southeast-2 : Asia Pacific (Sydney)
9) ap-northeast-1 : Asia Pacific (Tokyo)
10) ap-northeast-2 : Asia Pacific (Seoul)
11) sa-east-1 : South America (Sao Paulo)
12) cn-north-1 : China (Beijing)
13) cn-northwest-1 : China (Ningxia)
14) us-east-2 : US East (Ohio)
15) ca-central-1 : Canada (Central)
16) eu-west-2 : EU (London)
17) eu-west-3 : EU (Paris)
18) eu-north-1 : EU (Stockholm)
19) eu-south-1 : EU (Milano)
20) ap-east-1 : Asia Pacific (Hong Kong)
21) me-south-1 : Middle East (Bahrain)
22) af-south-1 : Africa (Cape Town)
(default is 3): 1


Select an application to use
1) Skill-App-CRUD
2) Skill-App-WebUI
3) [ Create new Application ]
(default is 1): 1


It appears you are using Docker. Is this correct?
(Y/n): Y
Select a platform branch.
1) Docker running on 64bit Amazon Linux 2
2) ECS running on 64bit Amazon Linux 2
3) Multi-container Docker running on 64bit Amazon Linux (Deprecated)
4) Docker running on 64bit Amazon Linux (Deprecated)
(default is 1): 1

Do you wish to continue with CodeCommit? (Y/n): n
Do you want to set up SSH for your instances?
(Y/n): Y

Select a keypair.
1) aws-eb
2) dev-sa-app
3) moodle
4) [ Create new KeyPair ]
(default is 3): 1
```

8. Add the option for using a local artifact to deploy ([link](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-configuration.html#eb-cli3-artifact)):

```bash
printf "deploy:\n  artifact: skill-app-ghbot.zip" >> .elasticbeanstalk/config.yml 
```

9. Created a new environment ("skill-app-ghbot-prod") which includes load balancing:

```bash
$ eb create --profile brn
Enter Environment Name
(default is Skill-App-WebUI-dev): production
Enter DNS CNAME prefix
(default is production22): 

Select a load balancer type
1) classic
2) application
3) network
(default is 2): 


Would you like to enable Spot Fleet requests for this environment? (y/N): N
Uploading Skill-App-WebUI/app-7756-220607_145245692926.zip to S3. This may take a while.
Upload Complete.
Environment details for: production
...additional lines ommitted due to sensitive data...
2022-06-07 19:56:39    INFO    Successfully launched environment: production
```

10. Created an A record (alias) in the hosted zone (Route 53) for bioinformed.app. Record is for skill.bioinformed.app and routed traffic to our elastic beanstalk environment using the "Route traffic to Alias" option. Environment was in "us-east-1" with name "production22.us-east-1.elasticbeanstalk.com".
11. Returned to the Elastic Beanstalk environment for this app. Added a listener to the load balancer for port 443, HTTPS protocol, with the SSL certificate created earlier and the ELBSecurityPolicy-2016-08 policy. Disabled HTTP access.

At this point, the app was working. If you are unable to follow these steps, ask Henry and he will help you.

</details>


After the app was deployed successfully for the first time, it was set up to allow deployment via GitHub Actions. This was done via the following steps:

<details>
<summary>Setting up GitHub actions deploy</summary>

Deployment via GitHub actions required the following steps:

1. An elasticbeanstalk config was added to the secrets in the github repo
2. A copy of the production environemntal variables was added to the repo secrets
3. The `.github/workflows/deploy.yml` script was written to enable deployment with a button press in github.

To enable github actions to assume the proper AWS IAM Role for deployment, we needed to set up an OIDC connection following [this guide](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services). Here is what Henry did:

4. Follow [these steps](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html) and use 
5. Create an IAM role for deployment and then attached this trust policy (replace `<your_aws_userid>` with the correct value):

```JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::346542362226:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    "token.actions.githubusercontent.com:sub": "repo:Bioinformatics-Research-Network/Skill-App-GHBot:ref:refs/heads/main"
                }
            }
        }
    ]
}
```

6. Add the ARN of the role you created to the secrets for the repo.


And that should be it! After this, the github action should work. If you run into any issues trying to repeat this protocol, let Henry know and he will help.

</details>


With the previous steps complete, one can now deploy the app by navigating to the github actions panel and triggering the **Build and Deploy** action manually. This should push the latest version into production.

