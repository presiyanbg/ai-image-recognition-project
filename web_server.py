#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Курсов проект по Изкуствен интелект с преподавател к-н лейт. асистент Веселин Евгениев Атанасов.

Екип: Христомир Цонев 12281-31 и Пресиян Цоневски 12281-26.
"""

# Categories to compare
X = "cars"
Y = "people"

# Two example images for the website, they are in the static directory next 
# where this file is and must match the filenames here
sampleY='static/people.jpg'
sampleX='static/traffic.jpg'
siteWallpaper='static/wallpaper.jpg'

# Where I will keep user uploads
UPLOAD_FOLDER = 'static/uploads'
# Allowed files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# Machine Learning Model Filename
ML_MODEL_FILENAME = 'saved_model.h5'

#Load operation system library
import os

#website libraries
from flask import render_template
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

#Load math library
import numpy as np

#Load machine learning libraries
from tensorflow.keras.preprocessing import image
from keras.models import load_model

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
from tensorflow.compat.v1.keras.backend import set_session

# Create the website object
app = Flask(__name__)

def load_model_from_file():
    #Set up the machine learning session
    mySession = tf.Session()
    set_session(mySession)
    myModel = load_model(ML_MODEL_FILENAME)
    myGraph = tf.get_default_graph()
    return (mySession,myModel,myGraph)

#Try to allow only images
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Define the view for the top level page
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    #Initial webpage load
    if request.method == 'GET' :
        return render_template('index.html',myX=X,myY=Y,mySampleX=sampleX,mySampleY=sampleY,mySiteWallpaper=siteWallpaper)
    else: # if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser may also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # If it doesn't look like an image file
        if not allowed_file(file.filename):
            flash('I only accept files of type'+str(ALLOWED_EXTENSIONS))
            return redirect(request.url)
        #When the user uploads a file with good parameters
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))

    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    test_image = image.load_img(UPLOAD_FOLDER+"/"+filename,target_size=(150,150))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis=0)

    mySession = app.config['SESSION']
    myModel = app.config['MODEL']
    myGraph = app.config['GRAPH']
    with myGraph.as_default():
        set_session(mySession)
        result = myModel.predict(test_image)
        image_src = "/"+UPLOAD_FOLDER +"/"+filename
        if result[0] < 0.5 :
            answer = "<div class='col-3 text-center'><img src='"+image_src+"' class='img-thumbnail' /><h4>guess:"+X+" "+str(result[0])+"</h4></div>"     
        else:
            answer = "<div class='col-3 text-center'><img class='img-thumbnail' src='"+image_src+"' class='img-thumbnail' /><h4>guess:"+Y+" "+str(result[0])+"</h4></div>"     
        results.append(answer)
        return render_template('index.html',myX=X,myY=Y,mySampleX=sampleX,mySampleY=sampleY,mySiteWallpaper=siteWallpaper,len=len(results),results=results)



def main():
    (mySession,myModel,myGraph) = load_model_from_file()
    
    app.config['SECRET_KEY'] = 'super secret key'
    
    app.config['SESSION'] = mySession
    app.config['MODEL'] = myModel
    app.config['GRAPH'] = myGraph

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #16MB upload limit
    app.run()

# Create a running list of results
results = []

#Launch everything
main()