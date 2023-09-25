from flask import *  
import pika
import json
import os
import pymysql
import re
from random import *
from flask_mail import *
# from yourapp import create_app


app=Flask(__name__)
# app.app_context().push()
mail = Mail(app)
app.secret_key = 'sai.chaitu1307@gmail.com'

app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465     
app.config["MAIL_USERNAME"] = 'sai.chaitu1307@gmail.com'  
app.config['MAIL_PASSWORD'] = 'jmnmmhnoyxrcymkw'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

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
                
                otp=randint(000000,999999)
                msg = Message(subject='OTP',sender ='sai.chaitu1307@gmail.com',recipients = [email] )
                msg.body = str(otp)
                mail.send(msg)
                print(otp)
                query2 = f"UPDATE Email SET otp = '{otp}' where email='{email}';"
                db_cursor.execute(query2)
                db_conn.commit()
                

rmq_channel.basic_consume(queue="otp_email",on_message_callback=verify_otp,auto_ack=True)
rmq_channel.start_consuming()
connection1.close()
db_cursor.close()
# msg = Message(subject='OTP',sender ='sai.chaitu1307@gmail.com',recipients = [email] )
# msg.body = str(otp)
# mail.send(msg)
if __name__=="__main__":
	app.run(debug= True)

