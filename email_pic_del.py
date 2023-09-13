from flask import *  
from flask_mail import *  
from random import *
import pymysql
import os
from werkzeug.utils import secure_filename

app=Flask(__name__)
mail = Mail(app)
app.secret_key = 'sai.chaitu1307@gmail.com'
#app.config['UPLOAD_FOLDER'] = 'C:\Users\Minfy.DESKTOP-7I2JS0O\Documents\GitHub\Flask_CODE\UPLOAD_FOLDER'

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
		
		
	
@app.route('/', methods=['GET','POST'])
def login():
	if request.method == 'GET':
		if 'user_id' in session:
			return redirect(url_for('profile'))
		else:
			return render_template('login.html',message="")
	elif request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		query = f"SELECT * from Email where username = '{username}' and passwrd = '{password}';"
		connection = db_connection()
		connection_cursor = connection.cursor()
		connection_cursor.execute(query)
		user = connection_cursor.fetchone()
		print("===================================================")
		print(user)
		if user is not None:
			if user['username']==username and user['passwrd']==password:
				session['user_id'] = user['personid']
				print("--------------------")
				print(session['user_id'])
				return redirect(url_for('profile'))
			
			
		else:
			message="user not found"
			return render_template('login.html',message=message)
		
	#return render_template('login.html')
		
		
		
@app.route('/profile')
def profile():
	if 'user_id' in session:
		connection = db_connection()
		connection_cursor = connection.cursor()
		user_id = session['user_id']
		query=f"SELECT * FROM Email WHERE personid = {user_id}"
		connection_cursor.execute(query)
		users=connection_cursor.fetchone()
		print(users)
	
		return render_template("profile.html",users=users)
	else:
		message="You must be logged in"
		return render_template('login.html',message=message)
		#if user:
			#return f"welcome, {user['username']} yours mail : {user['email']} and your phonenumber : {user['phonenum']}"
		
	        #return render_template("profile.html")
	

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
		
@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/gallery', methods=['POST','GET'])
def gallery():
	if request.method == 'GET':
		if 'user_id'in session:
			user_id=session.get('user_id')
			connection = db_connection()
			connection_cursor = connection.cursor()
			query = f" SELECT  user_id,filename from pic_info  WHERE user_id='{user_id}';"
			print(query)
			connection_cursor.execute(query)
			images = connection_cursor.fetchall()
			print(f"Total images information ---->{images}")
			connection_cursor.close()
			connection.close()
		return render_template('gallery.html',images=images)
	if request.method == 'POST':
		if 'user_id' in session and 'files' in request.files:
			files=request.files.getlist('files')
			print("--------------------------------------------")
			print(type(files))
			user_id=session['user_id']
			print(user_id)
			path = os.getcwd()
			print(f"path----->{path}")
			UPLOAD_FOLDER = os.path.join(path, 'uploads')
			for file in files:
				if file and allowed_file(file.filename):
							filename = secure_filename(file.filename)
							print(f"actual filename------>{filename}")
							os.makedirs(os.path.dirname(f"uploads/{user_id}/{filename}"), exist_ok=True)
							app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
							file.save(os.path.join(f"{app.config['UPLOAD_FOLDER']}/{user_id}", file.filename))
							print("-----------------------------------")
							connection = db_connection()
							connection_cursor = connection.cursor()
							query = f"INSERT INTO pic_info (user_id,filename) VALUE ('{user_id}', '{filename}');"
							print(query)
							connection_cursor.execute(query)
							connection.commit()
							connection_cursor.close()
							connection.close()
			return render_template('gallery.html')
		
@app.route('/uploads/<user_id>/<filename>',methods=["GET"])

def uploads(user_id, filename):
    session_user_id=session.get('user_id')
    print(type(session_user_id))
    if session_user_id is not None:
         print(type(user_id ))
         if str(session_user_id)== str(user_id):
           return send_file(f"uploads/{user_id}/{filename}")
         else:
           return "Forbidden", 403
    return "Forbidden", 403


@app.route('/delete/<int:user_id>/<filename>', methods=['POST'])
def delete_image(user_id,filename):
	session_user_id = session.get('user_id')
	if session_user_id is not None and str(session_user_id) == str(user_id):
		print(f"it is in deleting with userid {session_user_id}")
		path_to_delete = os.path.join('uploads', str(user_id), filename)
		print(f"path_to_delete---->{path_to_delete}")
		if os.path.exists(path_to_delete):
			os.remove(path_to_delete)
			print(f"After delete--->{path_to_delete}")
			connection = db_connection()
			connection_cursor = connection.cursor()
			query = f"DELETE FROM pic_info WHERE user_id='{user_id}' AND filename='{filename}';"
			connection_cursor.execute(query)
			connection.commit()
			connection_cursor.close()
			connection.close()
			return redirect(url_for('gallery'))
		else:
			print("---------------------------------")
			return "Forbidden", 403
	
		
			

if __name__=="__main__":
	app.run(debug= True)
