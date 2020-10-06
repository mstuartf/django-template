## Features

* Configurable using environment variables using dotenv
* Env variables set locally by running local.sh
* Logging to console locally and to CloudWatch using Watchtower in EB (needs to be activated - instructions below)
* Custom pagination
* Tailwind (with purging for fast page load)
* Sqlite locally, postgresql remote
* Dependencies listed in requirements.txt
* Elastic beanstalk container commands to migrate, createsuperuser (django.config)
* EB configuration to ensure auth headers are sent to Django (wsgi_custom.config)
* Force redirect http to https (needs to be activated - instructions below)
* Worker environment for deferred tasks (verification email only)
* Cron file for worker tasks

## Setup

### 1. Setup pyenv

* Create a virtualenv for the project: `$ pyenv virtualenv 3.6.3 $PROJECT_NAME`
* Activate the virtualenv: `$ pyenv local $PROJECT_NAME`
* Install dependencies: `$ pip install -r requirements.txt`
* Note: when using the eb cli you will need to deactivate the virtualenv (`$ pyenv local system` / `$ pyenv deactivate`)

### 1. Configure AWS CLI

* Install the (AWS CLI)[https://aws.amazon.com/cli/] if you do not already have it.
* Open the AWS console and go to `My Security Credentials` in the main menu. `Under Access keys (access key ID and secret access 
key)`, click `Create New Access Key` and copy the ID and key generated.
* Open your credentials file (~/.aws/credentials on a mac).
* Add the profile name and ID and key from the AWS console to the bottom of the file:

```
[$PROFILE_NAME]
aws_access_key_id=AKIAIOSFODNN7EXAMPLE
aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

* We will configure all EB CLI commands from this directory to use this profile in the next step. 

### 2. Init EB project

* Init the EB CLI for the directory: `eb init` and follow instructions. This will create an untracked .elasticbeanstalk dir.
* Setup SSH for project?
* Open .elasticbeanstalk/config.yml and set `profile` to the name of the profile created in the previous step. This means 
that you will not have to append `--profile $PROFILE_NAME` to all EB CLI commands.

### 2. Create new EB env

* Create an env using the CLI (make sure to specify postgres): `eb create $ENV_NAME -db -db.engine postgres`
* Enter a password for the DB (printable ASCII characters, except for white space and the symbols '/', '"', or '@')
* The env will be created but the first deployment will fail because all of the env variables are missing. You will get an 
error: `"The SECRET_KEY setting must not be empty."`.
* Go to EB configuration and add the BASIC CONFIG environment variables listed in local.sh.
* Use [this tool](https://miniwebtool.com/django-secret-key-generator/) to generate a SECRET_KEY.
* You also need to set the SUPERUSER DETAILS variables (container command will fail unless these are set).
* Add EB environment url to allowed hosts (i.e. XXX.eu-west-2.elasticbeanstalk.com)
* Add EB environment url to cors whitelist (i.e. http://XXX.eu-west-2.elasticbeanstalk.com)
* Apply configurations.
* Some values will need to be updated later (e.g. queue names) but adding these ones means the status will update to 'OK'.

### 3. Setup logging

* Go to IAM > Users > Add user
* Enter a username and select Programmatic Access
* Select Attach existing policies directly
* Choose CloudWatchLogsFullAccess
* Create User
* Set the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables from the user's details
* Set the AWS_LOG_GROUP to the app name and AWS_LOG_STREAM to the env name
* Hit Apply
* Go into settings and uncomment the additional configurations in LOGGING

### 4. Setup SSL (skip until you have custom domain)

Create a `redirect.config` filein .ebextensions with the following content:

```
files:
  "/etc/httpd/conf.d/ssl_rewrite.conf":
    mode: "000644"
    owner: root
    group: root
    content: |
      RewriteEngine On
      <If "-n '%{HTTP:X-Forwarded-Proto}' && %{HTTP:X-Forwarded-Proto} != 'https'">
      RewriteRule (.*) https://%{HTTP_HOST}%{REQUEST_URI} [R,L]
      </If>
```

Then configure the load balancer to server over HTTPS:

* Create a eu-west-2 AWS certificate for the API subdomain  (e.g. api.domain.com)
* Validate domain ownership by adding CNAME records (wait 5min and check certificate is 'issued' in manager).
* Add a new listener to the EB load balancer on port 443 (HTTPS) forwarding to port 80 (HTTP). Select the certificate 
you just created. Make sure you apply the changes!
* * If you get a 408, check the ports and protocol values are correct here.
* Add a CNAME for the API subdomain pointing to EB url (e.g. HOST RECORD: api, POINTS TO: XXX.eu-west-2.elasticbeanstalk.com)

### 2. Setup worker environment

#### 2a. Background

There are two kinds of EB environments:
* Web tiers: accept HTTP requests over the internet
* Worker tiers: read messages from SQS queues

Worker tiers are essentially private apps that web tiers can use to offload long-running operations that can be done
outside the context of a request. 

When you create a worker env, AWS automatically provisions an SQS queue and DLQ. Tasks can then be passed to the worker
by posting messages to the SQS queue. Each instance of the worker env runs a daemon process that reads messages from the
queue and posts them to the endpoint configured for the worker env. If the worker's endpoint returns a 200, the message
is deleted from the queue.

##### Using the same codebase

The worker tier is a different environment, but it does not have to be different code. If the background tasks to be handled
by the worker will need to use a lot of the main application's logic, it might make sense for the worker to use the same codebase.
E.g. you may not want to duplicate all models from the web tier.

If you use the same codebase for the web and worker tiers, you will need to prevent the worker endpoint called by the
daemon process from being called over the internet. For this, we can check the request headers match those automatically 
set by the daemon process (is this robust enough?).

There are different ways to deploy the same code to both envs (the web and the worker tiers):
* deploy twice
* or create application version, then update both envs to use this version
For now, we just deploy twice for simplicity.

##### Using the same database

Similarly, the worker app may need to connect to the same database as the web app. AWS allows multiple environments to connect
to the same database, so this is possible. For an EB environment, you just need to set the RDS environment variables manually
to tell the env which database to connect to and the credentials to use. 

In this repo, the worker env connects to the same database as the web tier so that background tasks can make changes here. E.g.
marking emails as sent and saving IDs, creating recurring classes, etc.

##### Offloading tasks to the worker

Once you have the worker app set up, all you need to do to offload background tasks is add a message to the relevant
queue in the normal way. For recursive functionality, the worker env itself may wish to add messages to the queue. Again,
this is just done in the normal way.

#### 2b. Create worker tier with same codebase

* Create the worker tier env: `eb create $ENV_NAME-worker --tier worker`
* The SQS and DL queues are created automatically.
* Each instance of the worker env will automatically have a daemon process that pulls messages from the queue.
* Copy environment variables from web tier.

#### 2c. Connect worker tier to same database as web tier

* Set these environment variables from [RDS](https://eu-west-2.console.aws.amazon.com/rds/home?region=eu-west-2#databases:): 
 * RDS_HOSTNAME: On the Connectivity & security tab on the Amazon RDS console: Endpoint.
 * RDS_PORT: On the Connectivity & security tab on the Amazon RDS console: Port.
 * RDS_DB_NAME: On the Configuration tab on the Amazon RDS console: DB Name.
 * RDS_USERNAME: On the Configuration tab on the Amazon RDS console: Master username.
 * RDS_PASSWORD: This was set when the web tier was created.
* Add worker env security group to inbound rules for RDS instance:
 * Go to [RDS](https://eu-west-2.console.aws.amazon.com/rds/home?region=eu-west-2#databases:).
 * Select the DB instance used by the web tier.
 * Under Connectivity & security, click the VPC security group link.
 * Click inbound rules > edit inbound rules.
 * It will show a create new rule interface.
 * Leave the default values, but under the 'source', select the security group of the worker tier (you can find this in 
 the eb console > Configuration > Instances).)
 * Save the inbound rule.
 
#### 2d. Configurations

* Go to EB > Environments > Configuration > Worker > Messages and set the `Http path` to `/worker/` to post all messages 
to this endpoint (the trailing slash is important or all requests will get a 301).
* Set the AWS_WORKER_QUEUE environment variable for the web and worker tiers to the name of the queue so that both can 
post to this queue.
* Make sure the AWS account has permission to add to the queue or you will not be able to deploy:
 * Click on the queue > Access policy > Edit
 * Paste in a copy of the following policy with the correct ARN (not just the name!):

```
{
  "Version": "2012-10-17",
  "Id": "arn:aws:sqs:eu-west-2:104524225421:awseb-e-jkm2nk6pat-stack-AWSEBWorkerQueue-3YIQPFIER6ZM/SQSDefaultPolicy",
  "Statement": [
    {
      "Sid": "Sid1593294416611",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "SQS:*",
      "Resource": "arn:aws:sqs:eu-west-2:104524225421:awseb-e-jkm2nk6pat-stack-AWSEBWorkerQueue-3YIQPFIER6ZM"
    }
  ]
}
```
 
#### 2e. Plug in

* Uncomment apps.worker.client code
* Redeploy web and worker tiers
 
### Cron jobs

Once you have the worker setup, you can setup automated jobs by creating a cron.yaml file in the root dir and specifying 
the worker endpoint to be hit and the schedule. E.g.:

version: 1
cron:
 - name: "reminders-job"
   url: "/worker/process-occurrences/"
   schedule: "*/15 * * * *"

Then add the relevant endpoint in the worker `views.py` and `urls.py` files.

## Running

### To run locally:

* Make sure you have python 3 on your machine
* Checkout the repo
* Install dependencies: `$ pip install -r requirements.txt`
* Initialise db: `$ . local migrate`
* Run local server using shell script: `. local.sh runserver`
* If you want to access the Django admin, run `. local.sh createsuperuser` to create yourself a login.

### To deploy

* Make sure you have configured the (AWS CLI)[https://aws.amazon.com/cli/].
* Run `$ eb deploy $ENV_NAME`

### Migrations

Run automatically remotely (container command specified in `django.config`).
Locally, run `$ . local migrate` whenever new migration files created.
