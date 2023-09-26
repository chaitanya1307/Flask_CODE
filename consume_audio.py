import pika
import pymysql
import json
import os
import pyttsx3

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


#RabbitMQ Connections
url = os.environ.get('CLOUDAMQP_URL', 'amqps://qkccwucm:ewRM2mVltak6bckNsUnQwRGl1IStk-I2@puffin.rmq2.cloudamqp.com/qkccwucm')
params = pika.URLParameters(url)
connection1 = pika.BlockingConnection(params)
rmq_channel = connection1.channel()
rmq_channel.queue_declare(queue="speech_queue", durable=True)
connection = db_connection()
connection_cursor = connection.cursor()


#Cosnsume functionality
def download_txt(ch, method, properties, body):
    print(body.decode().replace("'", "\""))
    payload = json.loads(body.decode().replace("'", "\""))
    print(payload)
    job_id = payload["job_id"]
    filename = payload["job_file"]
    user_id = payload["user_id"]
    print(job_id, filename, user_id)
    path = os.getcwd()
    UPLOAD_FOLDER = os.path.join(path, 'uploads')
    print(f"--------->{UPLOAD_FOLDER}")
    base = os.path.basename(filename)
    c = os.path.splitext(base)[0]
    
    if not os.path.exists(os.path.join(UPLOAD_FOLDER, str(user_id))):
        os.makedirs(os.path.join(UPLOAD_FOLDER, str(user_id)))
    file_path = os.path.join(UPLOAD_FOLDER, str(user_id), os.path.basename(filename))
    with open(file_path, 'wb') as file:
        file.write(body)
        
    engine = pyttsx3.init()
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
    engine.save_to_file(open(f"{UPLOAD_FOLDER}/{user_id}/{filename}", 'r').read(), os.path.join(f"{UPLOAD_FOLDER}/{user_id}/{c}.mp3"))
    engine.say(open(f"{UPLOAD_FOLDER}/{user_id}/{filename}", 'r').read())  
    engine.runAndWait()
    engine.stop()
    # Insert files into the audio table

    query = f"INSERT INTO audios_speech (user_id, filename) VALUES ('{user_id}', '{c}.mp3');"
    print(f"Audio_POST--->{query}")
    connection_cursor.execute(query)
    connection.commit()

    # Updating the stage
    query2 = f"UPDATE file_text SET stage = 'completed' where job_id='{job_id}';"
    print(query2)
    connection_cursor.execute(query2)
    connection.commit()

rmq_channel.basic_consume(queue="speech_queue",on_message_callback=download_txt,auto_ack=True)
rmq_channel.start_consuming()
connection1.close()
connection_cursor.close()
    # return "download completed"