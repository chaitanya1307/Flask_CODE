from flask import Flask, render_template, request
from flask_mail import Mail, Message
import pymysql
import os
import math
import random
import smtplib
from dotenv import load_dotenv 

current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)



app=Flask(__name__)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
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



@app.route('/', methods =['GET', 'POST'])

def login():
     if request.method == 'GET':
        return render_template('login.html')
     
     elif request.method == 'POST':
        email=request.form["email1"]
        password=request.form["password"]
        conn = db_connection()
        cur = conn.cursor()
        Query = f"SELECT email,passwrd FROM Email WHERE email='{email}' AND passwrd='{password}';"
        print(Query)
        cur.execute(Query)
        details=cur.fetchall()
        if len(details)==0:
            return "user not found"
        elif len(details) > 0:
            return "Login Successful"            

           

@app.route('/register', methods =['GET', 'POST'])

def register():
    digits="0123456789"
    OTP=""


    if request.method == 'GET':  
        return render_template('register.html')
    
    elif request.method == 'POST':
        lastname=request.form["lastname"]
        firstname=request.form["firstname"]
        email=request.form["email"]
        mobile=request.form["mobile"]
        city=request.form["city"]
        password=request.form["password"]

        if 'email' in request.form:

                query= f"SELECT * from Email where email = '{email}'"

                connection = db_connection()

                connection_cursor = connection.cursor()

                connection_cursor.execute(query)

                users=connection_cursor.fetchall()

                print(len(users))

                if len(users)>0:

                    message = "The email address already exists"

                    connection_cursor.close()

                    connection.close()

                    return render_template('register.html', message=message)

                else:
                    query = f"INSERT INTO Email (lastname, firstname, email, mobile, city,passwrd) VALUE ('{lastname}', '{firstname}', '{email}', '{mobile}', '{city}','{password}');"

                    connection_cursor.execute(query)

                    connection.commit()

                    connection_cursor.close()

                    connection.close()
                    for i in range(4):
                        OTP+=digits[math.floor(random.random()*10)]
                    otp = OTP + " is your OTP"
                    msg= otp
                    s = smtplib.SMTP('smtp.gmail.com', 587)
                    s.starttls()
                    username = os.environ.get('MAIL_USERNAME')
                    password = os.environ.get('MAIL_PASSWORD')
                    s.login(username, password)
                        #emailid = input(email)
                    s.sendmail('sai.chaitu1307@gmail.com',email,msg)
                    a = input("Enter Your OTP >>: ")
                    if a == OTP:
                            print("Verified")
                            # send email
                            
                            email = request.form["email"]
                            lastname = request.form['lastname']
                            data = {
                                    "lastname": lastname,
                                }
                            
                            msg = Message('Welcome to our website!', sender = 'sai.chaitu1307@gmail.com', recipients = [email])
                            msg.body = f"Hello!{lastname}Thank you  for registering on our website. We hope you enjoy our services!"
                            mail.send(msg)
                            
                            message = "Registration Successful."

                            return render_template('register.html', message=message,data=data)
       
                    else:
                            return render_template("invalidotp.html")

                    

        else:

            message = "Please enter an email address"

        return render_template('register.html', message=message)

       
if __name__=='__main__':
    app.run()