import boto3
import os
from datetime import datetime, timedelta

dynamodb = boto3.resource("dynamodb")
table_name = os.environ["TABLE_NAME"]
qr_table = dynamodb.Table(table_name)


today = datetime.now()
tomorrow = today + timedelta(hours=23)

today_ts = int(today.timestamp())
tomorrow_ts = int(tomorrow.timestamp())


def handler(event, context):
    url_user = event["detail"]["url_user"]
    qr_code_url = event["detail"]["qr_code_url"]
    qr_table.put_item(
        Item={
            "url_user": url_user,
            "qr_code_url": qr_code_url,
            "ttl": tomorrow_ts,
        }
    )
