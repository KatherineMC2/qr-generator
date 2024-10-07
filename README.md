# Serverless QR Code Generator

Generate QR Codes from your favourite URLS, made completely with AWS Serverless with AWS CDK in an event driven architecture.

# Services Used:

 API Gateway, AWS Lambda, Amazon S3,Amazon DynamoDB, Amazon EventBridge, Amazon CloudFront

# Architecture:

Architecture as of now:

![Architecture](https://raw.githubusercontent.com/KatherineMC2/qr-generator/a9ffc652d88a6051b11cd66469cf2155cf530e17/architecture.png)


## Blog

To discover how was made visit my blog [blog](https://katherinemoreno.me/blog/qr-code-generator/ )




# Pre Requisites
1. Poetry
    This project uses poetry as dependency manager
    * [Installation](https://python-poetry.org/docs/#installing-with-pipx)
    * [Tutorial](https://realpython.com/dependency-management-python-poetry/)
    * [Known Errors](./docs/poetry.md)
2. Docker
    * [Installation](https://docs.docker.com/get-docker/)


# Scripts

```
    poetry run cdk deploy           Deploy the CDK Stack
    poetry run cdk synth            Synth Stack
    poetry run cdk destroy          Destroy the CDK Stack
    poetry run ruff check --diff    Checks if lint is correct
    poetry run ruff check --fix     Checks if lint is correct and  if it is not tries to fix it
    poetry run ruff format --check  Checks if formatting is correct
    poetry run ruff format          Check if formatting is correct and if it is not tries autoformat it

```



# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

to install dependencies of the layer do from the root folder  execute the command

```
pip install -t ./layer -r requirements.txt

```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
