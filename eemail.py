from flask import *  
from flask_mail import *  
from random import *
import pymysql

app=Flask(__name__)
mail = Mail(app)

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

@app.route('/validate', methods=['POST'])
def validate_otp(email, otp):
		email = request.form['email']
		otp = request.form['otp']
		connection = db_connection()
		connection_cursor = connection.cursor()
		query = f"SELECT * from Email where email = '{email}' and otp = '{otp}'"
		connection_cursor.execute(query)
		users=connection_cursor.fetchall()
		print(len(users))
		if len(users)>0:
			return True
		else:
			return False
		
		
	#Open Connetion
	#Open Cursor
	# SELECT * FROM users WHERE email="email" and otp="otp"
	# return True/False
	# return True

@app.route('/', methods=['GET','POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html',message="")
	elif request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		query = f"SELECT * from Email where username = '{username}' and passwrd = '{password}';"
		connection = db_connection()
		connection_cursor = connection.cursor()
		connection_cursor.execute(query)
		result = connection_cursor.fetchall()
		print(result)
		if len(result)>0:
			message="login success"
			
			return redirect(url_for('profile'))
			#message="login success"
			
		elif len(result)==0:
			message="user not found"
		return render_template('login.html',message=message)
	
# @app.route('/profile')
# def profile():
# 	connection = db_connection()
# 	connection_cursor = connection.cursor()
# 	connection_cursor.execute("select * from Email")
# 	rows=connection_cursor.fetchall()
# 	print(rows)

# 	return render_template("profile.html",rows=rows)

user = {"username": "abc"}
@app.route('/profile', methods=['GET', 'POST'])
def profile():
	if (request.method == 'POST'):
		username = request.form['username']
		print(username)
		# connection = db_connection()
		# connection_cursor = connection.cursor()
		if username == user['username']:
			session['user'] = username
			connection = db_connection()
			connection_cursor = connection.cursor()
			connection_cursor.execute("select * from Email")
			rows=connection_cursor.fetchall()
			print(rows)
			return render_template("profile.html",rows=rows)
	

@app.route('/register', methods=['GET', 'POST'])
def register():
		message=" "
		if request.method == 'GET':
			return render_template('register.html', message="please fill out the form")
		elif request.method == 'POST':

			print(request.form)
			if 'verify' in request.form:
				email = request.form['email']
				otp_req = request.form['otp']
				if validate_otp(email, otp_req):
					return render_template("login.html", message="Successfully Verified... Please Login.")
				else:
					return render_template("verify.html")
				
			if 'register' in request.form:
				phonenum=request.form['phonenum']
				password = request.form['password']
				email = request.form['email']
				username = request.form['username']
				# validation=request.form['validation']
				query= f"SELECT * from Email where email = '{email}';"
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
					otp=randint(000000,999999)
					validation = 0
					query= f"INSERT INTO Email (username,email,passwrd,phonenum,otp) VALUES ('{username}','{email}', '{password}','{phonenum}','{otp}');"
					connection_cursor.execute(query)
					connection.commit()
					connection_cursor.close()
					connection.close()
					message='Registration successful'
					msg = Message(subject='OTP',sender ='sai.chaitu1307@gmail.com',recipients = [email] )
					msg.body = str(otp)
					mail.send(msg)
					return render_template('verify.html', message=message, email=email)
			else:
				message = "Please enter an email address"
			return render_template('register.html')

# @app.route('/validate', methods=['POST'])
# def validate():
# 	user_otp=request.form['otp']
# 	if otp==int(user_otp):
# 		return render_template('register.html')

if __name__=="__main__":
	app.run(debug= True)