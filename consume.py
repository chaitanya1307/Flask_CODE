import pika
import json
import os
import pymysql
from pytube import YouTube

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
queue_name = 'youtube_download_queue'
rmq_channel = connection1.channel()
rmq_channel.queue_declare(queue="youtube_download_queue", durable=True)

db_conn = db_connection()
db_cursor = db_conn.cursor()
def download_youtube_video(ch, method, properties, body):
                payload = json.loads(str(payload))
                job_id = payload["job_id"]
                video_url = payload["job_url"]
                user_id = payload["user_id"]
                utube = YouTube(video_url)
                video = utube.streams.get_highest_resolution()
                filename = f"{user_id}_{utube.title}.mp4"
                path = os.getcwd()
                UPLOAD_FOLDER = os.path.join(path, 'uploads')
                os.makedirs(os.path.dirname(f"uploads/{user_id}/{filename}"), exist_ok=True)
                app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                downloadFolder = str(os.path.join(f"{app.config['UPLOAD_FOLDER']}/{user_id}"))
                video.download(downloadFolder, filename=filename)
                query = f"INSERT INTO video_info (user_id, filename) VALUES ('{user_id}', '{filename}');"
                print(query)
                db_cursor.execute(query)
                db_conn.commit()
                db_cursor.close()
                db_conn.close()
                return redirect(url_for('videos'))
rmq_channel.basic_consume(queue="youtube_download_queue",on_message_callback=download_youtube_video)
rmq_channel.start_consuming()
#rmq_channel.close()
rmq_conn.close()
