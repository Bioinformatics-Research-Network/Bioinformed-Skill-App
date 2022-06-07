# Skill App WebUI

**Maintainer**: @millerh1

This is a web application, written in Python-Flask. It provides users with a GUI for interacting with the BRN skill app. The **primary features** are:

1. Login/authentication with GitHub.
2. A customizable user profile which displays badges earned by the user.
3. An "Assessments" page which shows the assessments available to the user.
4. An interface for launching, monitoring, and deleting assessments.
5. A "Settings" page which can be used to update a user's profile.

## Dev notes

### Getting started

### Deployment

<details>
<summary>Preliminary steps</summary>

Prior to deploying the application for the first time, Henry performed all the following steps to ensure correct configuration:

1. Created an OAuth GitHub app within the Bioinformatics Research Network GitHub org to handle authentication to the Web UI. Homepage URL: https://skill.bioinformed.app/ -- callback URL: https://skill.bioinformed.app/login/github/authorized
2. Registered a domain name (bioinformed.app) using Google Domains
3. Routed the domain to AWS Route 53 using [this guide](https://www.entechlog.com/blog/aws/connect-google-domain-to-aws-route-53/). Specifically, he created a Route 53 hosted zone for 'bioinformed.app'. This generated the `NS` records which he added as custom nameservers in the Google Domain record for bioinformed.app.
4. Used AWS Certificate Manager to register SSL certificates for 'bioinformed.app', 'learn.bioinformed.app', 'www.bioinformed.app', and 'skill.bioinformed.app'. These certificates were then added to the hosted zone as CNAME records.
<!-- 4. Downloaded and installed the awsebcli package -->
5. Created a ZIP file of the application, ignoring unnecessary files:

```bash
zip skill-app-webui.zip -r * .[^.]* -x "*cache*" -x "*venv*" -x "*instance*" -x "*vscode*" -x "*.git*"
```

6. Create a new Elastic Beanstalk application ("Skill-App-WebUI"), then created a new environment ("skill-app-production") within that application. Uploaded code in the ZIP file and added version tag v0.0.1. Also added custom configuration to enable an Application load balancer (modify capacity to allow load balancing, then add application load balancer) similar to [this guide](https://docs.amazonaws.cn/en_us/elasticbeanstalk/latest/dg/environments-cfg-nlb.html). 
7. Created an A record (alias) in the hosted zone (Route 53) for bioinformed.app. Record is for skill.bioinformed.app and routed traffic to our elastic beanstalk environment using the "Route traffic to Alias" option. Environment was in "us-east-1" with name "skill-app-production.eba-hnvvzhf2.us-east-1.elasticbeanstalk.com".
8. Returned to the Elastic Beanstalk environment for this app. Added a listener to the load balancer for port 443, HTTPS protocol, with the SSL certificate created earlier and the ELBSecurityPolicy-2016-08 policy. Disabled HTTP access.

</details>




