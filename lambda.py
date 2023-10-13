import json
import boto3
import pymysql
import pyttsx3
from dotenv import load_dotenv 
import os


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
S3_BUCKET_NAME = 'flaskfile'
S3_REGION = 'ap-south-1'

# s3_C = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
s3_R = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)

event = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ap-south-1', 'eventTime': '2023-10-12T11:07:07.336Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AIDAUS2MADNTYKTVPVJIN'}, 'requestParameters': {'sourceIPAddress': '183.82.97.86'}, 'responseElements': {'x-amz-request-id': 'QZ6DX28KPEQH0HZH', 'x-amz-id-2': '1/xqgP0jFBgpHW2U6yGRKHHU8kYcnKZxmKfSh7Zmp1mzbxcf9qXeaRY/WtvRGRMtsi4D2ldiLADft3PCuQkS/JvoR50wIpY7EYD+t/3PbA8='}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'lambda_trigger', 'bucket': {'name': 'flaskurl', 'ownerIdentity': {'principalId': 'A8WIRMB3DCK3Y'}, 'arn': 'arn:aws:s3:::flaskurl'}, 'object': {'key': 'uploads/6/audios/sample.txt', 'size': 21, 'eTag': '6e6391b586f7fe47e9e60d888a26837e', 'versionId': '8bL0.3G.zk3FOOU9Suh.T6.zRxA7IkwZ', 'sequencer': '006527D35B494E41B6'}}}]}

context=" "

def lambda_handler(event, context):
    print(event)
    key=event['Records'][0]['s3']['object']['key']
    buc_name=event['Records'][0]['s3']['bucket']['name']
    print(key,buc_name,sep="\n")
    user_id=key.split("/")[1]
    c = key.split("/")[3]
    print(user_id,c,sep="\n")
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
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
lambda_handler(event,context)





