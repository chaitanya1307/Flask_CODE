import pymysql
from random import *
import os
import json
from fpdf import *
import boto3
from dotenv import load_dotenv
current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
S3_BUCKET_NAME = 'flaskurl'
S3_REGION = 'ap-south-1'
s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)

def db_connection():
    timeout = 10
    connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db="defaultdb",
    host="mysql-1ed7bbbc-wlmycn-2bde.aivencloud.com",
    password="AVNS_bgJrNel49GgbukSs-4U",
    read_timeout=timeout,
    port=26098,
    user="avnadmin",
    write_timeout=timeout,
    )
    return connection

connection = db_connection()
connection_cursor = connection.cursor()
event = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ap-south-1', 'eventTime': '2023-10-11T11:34:12.175Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'A8WIRMB3DCK3Y'}, 'requestParameters': {'sourceIPAddress': '183.82.97.86'}, 'responseElements': {'x-amz-request-id': 'VF7H83HBSMY6G2SR', 'x-amz-id-2': 'SeV/gxB3fczkMmJO9ElPz7aTWfcsMSAbdMfbiWdeGgIfJ4EUUNStcLxVgCsrwnQgd9iLd+fH0c2b6k26TyNlCU+BzbrHvz1F'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'lambda_trigger', 'bucket': {'name': 'flaskurl', 'ownerIdentity': {'principalId': 'A8WIRMB3DCK3Y'}, 'arn': 'arn:aws:s3:::flaskurl'}, 'object': {'key': 'uploads/6/pdf/sample.txt', 'size': 21, 'eTag': '6e6391b586f7fe47e9e60d888a26837e', 'versionId': 'ZWrFTcnhjmE95eDsBdhixqXebOQ05SZI', 'sequencer': '0065268834265A2C3C'}}}]}
context = " "
def lambda_handler(event, context):
    s3_key=event['Records'][0]['s3']['object']['key']
    bucket_name=event['Records'][0]['s3']['bucket']['name']
    user_id=s3_key.split("/")[1]
    print(user_id)
    filename=s3_key.split("/")[3]
    print(filename)
    path = os.getcwd()
    UPLOAD_FOLDER = os.path.join(path, 'uploads')
    base = os.path.basename(s3_key)
    c = os.path.splitext(base)[0]
    pdf_path = os.path.join(UPLOAD_FOLDER, f"{user_id}/{c}.pdf")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    s3_client.download_file(bucket_name, s3_key, pdf_path)
    if os.path.exists(pdf_path):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        with open(pdf_path, "r") as text_file:
            for line in text_file:
                pdf.cell(200, 10, txt=line, ln=1, align="C")
        pdf.output(pdf_path)
        s3_key=event['Records'][0]['s3']['object']['key']
        base = os.path.basename(s3_key)
        c = os.path.splitext(base)[0]
        user_id=s3_key.split("/")[1]
        query = f"INSERT INTO login_flask_upload2 (user_id, filename) VALUES ('{user_id}','{c}.pdf');"
        connection_cursor.execute(query)
        connection.commit()
        query2 = f"UPDATE txt_pdf SET job_status = 'completed' where user_id='{user_id}';"
        print(query2)
        connection_cursor.execute(query2)
        connection.commit()
        s3_client.upload_file(pdf_path, bucket_name, f"uploads/{user_id}/pdf/{c}.pdf", ExtraArgs = {
            "ContentDisposition": "inline",
            "ContentType": "application/pdf"
        })
        connection_cursor.close()
        connection.close()
        return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
lambda_handler(event,context)
