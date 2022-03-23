#  This is a web-based weibull tool. It uses Flask micro webframeworks + Computer module
#  static folder: app.css, app.js
#  templates folder: layout.html (basic layout) and app.html
#  Bootstrap CSS and jQuery (ajax) are used.
#  Xiaoyang Liu
#  March 22, 2022
#  xiaoyang.liu@gmail.com
#
# run this app in command 
#  $export FLASK_APP=weibull_app.py
#  $flask run
#
# 1/29/2019: new feature:
# input file types could be xlsx, txt and csv
# input file has the first row of x and y name
# based on input max value, to live adjust x tick range and estimated x 
# based on input x and y name, to live change label text
# convert non-string columns into string to avoid the plot bug
# remove zero and na values to avoid the plot bug
# add fitting parameters into table
# add button to download the fitting and prediction results
# clean codes by remove print and console.log

# 2/2/2019 new features:
# add a new filter to rotate the x-tick
# make xtick of mile/km to be value/1000
# make xlabel of mile  and km to be (x1000)
# remove non-numeric data and fill them with NaN

# 5/8/2020 changes
# work with GITHUB and VSCode

from compute import listdata, plotdata
from flask import Flask, render_template, request,json,jsonify
# from werkzeug import secure_filename
import os
import pandas as pd


# Application object
app = Flask(__name__)

# set up environment, local development Ubuntu, pythonanywhere, The difference is the app path folder
env = "local"
if env == "local":
    UPLOAD_DIR = 'uploads/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
    app.secret_key = 'MySecretKey'
    if not os.path.isdir(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)
elif env == "pythonanywhere":
    UPLOAD_DIR = 'mysite/uploads/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
    app.secret_key = 'MySecretKey'
    if not os.path.isdir(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)   
   
# Allowed file types for file upload
ALLOWED_EXTENSIONS = set(['xlsx', 'txt', 'csv'])
def allowed_file(filename):
    """Does filename have the right extension?"""
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#global vaiable; user loaded file name;
fullfilename = ''
df = pd.DataFrame()

# initial page, ajax request is based on this page without reloading full page
@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template("app.html")

# upload *.xlsx file onto server upload foder, reade file content and return them back to front page
@app.route('/upload',methods = ['POST'])
def upload_fun(): 
    global fullfilename
    global df
#    if no file exist
    if 'file' not in request.files:
        print('No file, please select one data file')
        return render_template("app.html")
    file = request.files['file']
        # if user does not select file, browser also submit a empty part without filename
    if file.filename == '':
        print('Please select one data file, the file type could be txt, csv, xlsx')
        return render_template("app.html")
#    if file type is allowed and not empty
    if file and allowed_file(file.filename):
        filename=file.filename
        fullfilename=app.config['UPLOAD_FOLDER']+filename
#        save file 
        file.save(fullfilename) 
#        read file content
        data = listdata(fullfilename)  
#       encode data into json format and send it back to front page
        data = json.loads(data)
        pritn(data)
        return jsonify({"data": data})

# plot and predict
@app.route('/plot',methods=['POST'])
def plot_fun():
    global fullfilename
    param = request.get_json()
#    get predict and plot parameters, and call plotdata function from Computer module
    data = plotdata(fullfilename,param)
#    encode data into json format and send it back to front page
    data = json.loads(data)
    return  jsonify({"data": data})

       
if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug = True, port = 80 )