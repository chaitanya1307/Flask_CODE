import pika
import pymysql
import json
import os
import boto3
from dotenv import load_dotenv 
import pyttsx3
from dotenv import load_dotenv 


current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)


#Connecting to database
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


AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
S3_BUCKET_NAME = 'flaskfile'
S3_REGION = 'ap-south-1'

#RabbitMQ Connections
url = os.environ.get('CLOUDAMQP_URL', 'amqps://qkccwucm:ewRM2mVltak6bckNsUnQwRGl1IStk-I2@puffin.rmq2.cloudamqp.com/qkccwucm')
params = pika.URLParameters(url)
connection1 = pika.BlockingConnection(params)
rq_channel = connection1.channel()
rq_channel.queue_declare(queue="speech_queue", durable=True)
connection = db_connection()
connection_cursor = connection.cursor()

s3_C = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
s3_R = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
#Cosnsume functionality
def download_txt(ch, method, properties, body):
    print(body.decode().replace("'", "\""))
    payload = json.loads(body.decode().replace("'", "\""))
    job_id = payload["job_id"]
    filename = payload["s3_key"]
    user_id = payload["user_id"]
    s3_bucket_name = payload["bucket_name"]

    obj = s3_R.Object(s3_bucket_name,filename )
    print("?????????????????????????",obj)
    a=obj.get()['Body'].read().decode('utf-8')
    print("||||||||||||||||||||||||||||||",a)
    base = os.path.basename(filename)
    c = os.path.splitext(base)[0]
    print(c)
    
    path = os.getcwd()
    UPLOAD_FOLDER = os.path.join(path, 'uploads')
    if not os.path.exists(os.path.join(filename)):
        os.makedirs(os.path.join(filename))
    engine = pyttsx3.init()
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
    engine.save_to_file(str(a),f'uploads/{user_id}/{c}.mp3')
    engine.runAndWait()
    engine.stop()
    print(UPLOAD_FOLDER)
    s3_C.upload_file(f'{UPLOAD_FOLDER}/{user_id}/{c}.mp3',s3_bucket_name,f"uploads/{user_id}/audios/{c}.mp3")
    os.remove(f"{UPLOAD_FOLDER}/{user_id}/{c}.mp3")
    path = f"uploads/{user_id}/audios/{c}.txt"
    try:
       os.rmdir(path)
       print("directory is deleted")
    except OSError as x:
        print("Error occured: %s : %s" % (path, x.strerror))

    query = f"INSERT INTO audios (user_id, filename) VALUES ('{user_id}', '{c}.mp3');"
    print(f"Audio_POST--->{query}")
    connection_cursor.execute(query)
    connection.commit()

    # Updating the stage
    path1 = f"uploads/{user_id}/audios/{c}.mp3"
    query2 = f"UPDATE txt_speech SET stage = 'completed',s3_key = '{path1}' where job_id='{job_id}';"
    print(query2)
    connection_cursor.execute(query2)
    connection.commit()
   

rq_channel.basic_consume(queue="speech_queue",on_message_callback=download_txt,auto_ack=True)
rq_channel.start_consuming()
connection1.close()
connection_cursor.close()
    # return "download completed"