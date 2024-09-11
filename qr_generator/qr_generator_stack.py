from aws_cdk import (
    CfnOutput,
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
)
from aws_cdk.aws_cloudfront import BehaviorOptions, Distribution, OriginAccessIdentity
from aws_cdk import Duration


from aws_cdk.aws_cloudfront_origins import S3Origin

from aws_cdk.aws_lambda_python_alpha import (
    PythonFunction,
)

from constructs import Construct

import os


class QrGeneratorStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -------------- Frontend ------------------#

        # Create a bucket to host the website
        qr_website_bucket = s3.Bucket(
            self, "qr_website_bucket", access_control=s3.BucketAccessControl.PRIVATE
        )

        # Verificar la existencia del directorio website
        website_dir = os.path.join(os.path.dirname(__file__), "website")
        if not os.path.isdir(website_dir):
            raise FileNotFoundError(f"El directorio {website_dir} no existe")

        qr_origin_access_identity = OriginAccessIdentity(self, "OriginAccessIdentity")
        qr_website_bucket.grant_read(qr_origin_access_identity)

        qr_distribution = Distribution(
            self,
            "Distribution",
            default_root_object="website.html",
            default_behavior=BehaviorOptions(
                origin=S3Origin(
                    qr_website_bucket, origin_access_identity=qr_origin_access_identity
                )
            ),
        )

        s3deploy.BucketDeployment(
            self,
            "DeployWebsite",
            sources=[s3deploy.Source.asset(website_dir)],
            destination_bucket=qr_website_bucket,
            distribution=qr_distribution,
            distribution_paths=["/*"],  # This is for invalidation of the cache
        )

        # This makes to print in the console log the domain of the distribution
        CfnOutput(self, "DomainName", value=qr_distribution.domain_name)

        # ------------------------ Backend -------------------------------------#

        # Crear el bucket S3
        bucket = s3.Bucket(
            self,
            "Bucket",
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            object_ownership=s3.ObjectOwnership.OBJECT_WRITER,
            lifecycle_rules=[s3.LifecycleRule(expiration=Duration.days(1))],
        )

        cf_domain_name = "https://" + qr_distribution.domain_name

        # Create dynamoDB table

        qr_code_table = dynamodb.Table(
            self,
            "QRTable",
            partition_key=dynamodb.Attribute(
                name="url_user",
                type=dynamodb.AttributeType.STRING,
            ),
            time_to_live_attribute="ttl",
            table_name="qr_code_table",
        )

        bus = events.EventBus(
            self,
            "bus",
            event_bus_name="BusForLambdaEvents",
        )

        bus.archive(
            "Archive",
            archive_name="LambdaEventsArchive",
            description="LambdaEvents Archive",
            event_pattern=events.EventPattern(account=[Stack.of(self).account]),
            retention=Duration.days(365),
        )

        # Definir la función Lambda usando la capa creada
        create_qr_lambda = PythonFunction(
            self,
            "CreateQrCodeLambda",
            function_name="createQrCodeLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            index="create_qr.py",  # Path to the directory with the Lambda function code
            handler="handler",  # Handler of the Lambda function
            entry="./lambda",
            environment={
                "REGION": self.region,
                "BUCKET_NAME": bucket.bucket_name,
                "TABLE_NAME": qr_code_table.table_name,
                "ALLOWED_ORIGIN": cf_domain_name,
                "BUS_NAME": bus.event_bus_name,
            },
            description="Lambda for creating the QR code",
        )

        bucket.grant_read_write(create_qr_lambda)
        bucket.grant_put_acl(create_qr_lambda)
        bus.grant_put_events_to(create_qr_lambda)

        # Definir la API Gateway
        api = apigateway.RestApi(self, "ApiGatewayQR", rest_api_name="RestAPI QR")

        qr_code_integration = apigateway.LambdaIntegration(create_qr_lambda)

        qr = api.root.add_resource("qr")

        qr.add_cors_preflight(
            allow_methods=["POST", "OPTIONS"],
            allow_origins=[cf_domain_name],
        )
        qr.add_method("POST", qr_code_integration)

        # Grant permitions to the lambda to read and write the table

        qr_code_table.grant_read_data(create_qr_lambda)

        update_table_lambda = PythonFunction(
            self,
            "UpdateTableLambda",
            function_name="updateTableLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            index="update_table.py",  # Path to the directory with the Lambda function code
            handler="handler",  # Handler of the Lambda function
            entry="./lambda",
            environment={"REGION": self.region, "TABLE_NAME": qr_code_table.table_name},
            description="Lambda for updating the qr table with a new record",
        )
        qr_code_table.grant_write_data(update_table_lambda)

        event_rule = events.Rule(
            self,
            "Rule",
            event_pattern=events.EventPattern(
                source=["create_qr"],
            ),
            event_bus=bus,
        )
        # Add lambda function as a target for the EventBridge rule
        event_rule.add_target(targets.LambdaFunction(update_table_lambda))
