# esta funcion recibe el productId como parametro
import boto3
import boto3.dynamodb.conditions as conditions
from datetime import datetime
import json
import qrcode
import uuid
import io
import os

# Inicialize sesion using dynamoDB
region = os.environ["REGION"]
bus_name = os.environ["BUS_NAME"]
dynamodb = boto3.resource("dynamodb", region_name=region)
table_name = os.environ["TABLE_NAME"]
qr_table = dynamodb.Table(table_name)

# Initialize a session using Amazon S3
s3 = boto3.client("s3", region_name=region)

bucket_name = os.environ["BUCKET_NAME"]

# Initialize a session in Eventbridge
event_bridge = boto3.client("events", region_name=region)


def generate_filename():
    Uuid = uuid.uuid4()
    randomUuid = Uuid.hex

    filename = randomUuid + ".png"
    return filename


def handler(event, context):
    body = event["body"]
    parsed_body = json.loads(body)
    url = parsed_body["url"]
    ## Get the current time
    current_time = int(datetime.now().timestamp())
    ## Query the table to get the item and filtering by the ttl attribute
    response = qr_table.query(
        KeyConditionExpression=conditions.Key("url_user").eq(url),
        FilterExpression=conditions.Attr("ttl").gt(current_time),
    )
    response = qr_table.get_item(Key={"url_user": url})

    if response["Count"] > 0:
        item = response["Items"][0]
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "The item requested has been found in the table",
                    "qr_code_url": item["qr_code_url"],
                }
            ),
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": os.environ["ALLOWED_ORIGIN"],
                "Access-Control-Allow-Methods": "OPTIONS,POST",
            },
        }

    else:
        filename = generate_filename()
        url_code = f"https://{bucket_name}.s3.{region}.amazonaws.com/{filename}"

        # Generate QR code
        img = qrcode.make(url)
        img_bytes = io.BytesIO()
        img.save(img_bytes)
        img_bytes = img_bytes.getvalue()

        # Generate a unique filename
        s3.put_object(
            Body=img_bytes,
            Bucket=bucket_name,
            Key=filename,
            ContentType="image/png",
            ACL="public-read",
        )
        response = event_bridge.put_events(
            Entries=[
                {
                    "Source": "create_qr",
                    "DetailType": "Qr code created",
                    "Detail": json.dumps(
                        {"url_user": f"{url}", "qr_code_url": f"{url_code}"}
                    ),
                    "EventBusName": bus_name,
                }
            ]
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "QR code generated and uploaded to S3 bucket successfully!",
                    "qr_code_url": url_code,
                }
            ),
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": os.environ["ALLOWED_ORIGIN"],
                "Access-Control-Allow-Methods": "OPTIONS,POST",
            },
        }
