
import pika
import json
import os
import pymysql
import re
from random import *
import smtplib
from dotenv import load_dotenv
current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)


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


url = os.environ.get('CLOUDAMQP_URL', 'amqps://qkccwucm:ewRM2mVltak6bckNsUnQwRGl1IStk-I2@puffin.rmq2.cloudamqp.com/qkccwucm')
params = pika.URLParameters(url)
connection1 = pika.BlockingConnection(params)
rmq_channel = connection1.channel()
rmq_channel.queue_declare(queue="otp_email", durable=True)

db_conn = db_connection()
db_cursor = db_conn.cursor()
def verify_otp(ch, method, properties, body):
                print(body.decode().replace("'","\""))
                payload = json.loads(body.decode().replace("'","\""))
                email = payload["email"]
                time_stamp = payload["timestamp"]
                # s.login("sai.chaitu1307@gmail.com ", "your gmail's security")

                otp=randint(000000,999999)
                print("---------------------",otp)
                msg = f" {otp}  is your otp"
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                password = os.environ.get('MAIL_PASSWORD')
                
                server.login("sai.chaitu1307@gmail.com", password)
                server.sendmail("sai.chaitu1307@gmail.com",email,msg)

                query2 = f"UPDATE Email SET otp = '{otp}' where email='{email}';"
                db_cursor.execute(query2)
                db_conn.commit()
                

rmq_channel.basic_consume(queue="otp_email",on_message_callback=verify_otp,auto_ack=True)
rmq_channel.start_consuming()
connection1.close()
db_cursor.close()


