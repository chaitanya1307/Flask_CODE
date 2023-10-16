import json
import boto3
import pymysql
import pyttsx3
import os

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

s3_C = boto3.client('s3')
s3_R = boto3.resource('s3')

def lambda_handler(event, context):
    key=event['Records'][0]['s3']['object']['key']
    buc_name=event['Records'][0]['s3']['bucket']['name']
    user_id=key.split("/")[1]
    c = key.split("/")[3]
    print(key,buc_name,user_id,c,sep="\n")
    obj = s3_R.Object(buc_name,key)
    a=obj.get()['Body'].read().decode('utf-8')
    engine = pyttsx3.init()
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
    engine.save_to_file(str(a),f'uploads/{user_id}/{c}.mp3')
    engine.runAndWait()
    engine.stop()
    path = os.getcwd()
    UPLOAD_FOLDER = os.path.join(path, 'uploads')
    s3_C.upload_file(f'{UPLOAD_FOLDER}/{user_id}/{c}.mp3',buc_name,f"uploads/{user_id}/audios/{c}.mp3")
    connection = db_connection()
    connection_cursor = connection.cursor()
    query2 = f"UPDATE txt_speech SET stage = 'completed',s3_key = '{key}' where user_id='{user_id}';"
    print(query2)
    connection_cursor.execute(query2)
    connection.commit()
    connection_cursor.close()
    connection.close()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }




