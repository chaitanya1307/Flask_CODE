import pika
import json
import os
import pymysql
from pytube import YouTube
import re
import boto3
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

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
S3_BUCKET_NAME = 'flaskurl'
S3_REGION = 'ap-south-1'

#s3 = boto3.resource('s3',aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key= AWS_SECRET_KEY)
url = os.environ.get('CLOUDAMQP_URL', 'amqps://qkccwucm:ewRM2mVltak6bckNsUnQwRGl1IStk-I2@puffin.rmq2.cloudamqp.com/qkccwucm')
params = pika.URLParameters(url)
connection1 = pika.BlockingConnection(params)
rmq_channel = connection1.channel()
rmq_channel.queue_declare(queue="youtube_download_queue", durable=True)

db_conn = db_connection()
db_cursor = db_conn.cursor()
def download_youtube_video(ch, method, properties, body):
                print(body.decode().replace("'","\""))
                payload = json.loads(body.decode().replace("'","\""))
                job_id = payload["job_id"]
                video_url = payload["job_url"]
                user_id = payload["user_id"]
                print(job_id,video_url,user_id)
                utube = YouTube(video_url)
                video = utube.streams.get_highest_resolution()
                file = f"{user_id}_{utube.title}.mp4"
                filename = re.sub(r'[\\/*?:"<>|()\']',"",file)
                path = os.getcwd()
                UPLOAD_FOLDER = os.path.join(path, 'uploads')
                os.makedirs(os.path.dirname(f"uploads/{user_id}/{filename}"), exist_ok=True)
                downloadFolder = str(os.path.join(f"{UPLOAD_FOLDER}/{user_id}"))
                video.download(downloadFolder, filename=filename)
                
                s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
                s3.upload_file(f"{UPLOAD_FOLDER}/{user_id}/{filename}",S3_BUCKET_NAME,f"uploads/{user_id}/youtube/{filename}")
                query = f"INSERT INTO video_info (user_id, filename) VALUES ('{user_id}', '{filename}');"
                print(query)
                db_cursor.execute(query)

                query2 = f"UPDATE youtube_url SET job_status = 'completed' where job_id='{job_id}';"
                print(query2)
                db_cursor.execute(query2)
                db_conn.commit()
                
              
                
rmq_channel.basic_consume(queue="youtube_download_queue",on_message_callback=download_youtube_video,auto_ack=True)
rmq_channel.start_consuming()
connection1.close()
db_cursor.close()
