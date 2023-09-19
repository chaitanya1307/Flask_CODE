from flask import Flask, render_template, request,jsonify, make_response

import requests
import ipaddress

app = Flask(__name__)

app.config['DEBUG'] = True


# @app.route('/')
# def index():
#     return 'Flask is Awesome!'


# @app.route('/geolocation', methods=['GET'])
# def get_geolocation():
#         return render_template('index2.html')

@app.route('/iplocation', methods=["GET","POST"])
def post_geolocation(): 
	if request.method == 'GET':
		return render_template('index2.html')
	elif request.method == 'POST':
		ipaddress.ip_address(request.form['ip_address'])
		req = requests.get('https://ipgeolocation.abstractapi.com/v1/?ip_address=' + request.form['ip_address'] + '&api_key=2470d093773e499ea714dc1c5c1c598e')
		return make_response(jsonify(req.json()))


# @app.route('/fetch-gelocation', methods=['POST'])
# def post_geolocation():
#         ipaddress.ip_address(request.form['ip_address'])
#         req = requests.get('https://ipgeolocation.abstractapi.com/v1/?ip_address=' + request.form['ip_address'] + '&api_key=2470d093773e499ea714dc1c5c1c598e')
#         return make_response(jsonify(req.json()))
    # except ValueError:
    #     return make_response(jsonify({'error': 'Invalid IP Address'}))
    # except Exception as e:
    #     return make_response(jsonify({'error': str(e)}))



if __name__ == "__main__":
    app.run(debug=True)