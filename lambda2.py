import mysql.connector
from random import *
import os
from fpdf import *
import boto3

s3_client = boto3.client('s3')

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
        query2 = f"UPDATE login_flask_queue2 SET job_status = 'completed' where user_id='{user_id}';"
        print(query2)
        connection_cursor.execute(query2)
        connection.commit()
        s3_client.upload_file(pdf_path, bucket_name, f"uploads/{user_id}/pdf/{c}.pdf", ExtraArgs = {
            "ContentDisposition": "inline",
            "ContentType": "application/pdf"
        })
        connection_cursor.close()
        connection.close()
        os.remove(pdf_path)