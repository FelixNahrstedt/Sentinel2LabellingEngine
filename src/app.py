from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from modules.OverpassQuery import query_OSM


app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'


@app.route('/', methods = ['GET','POST'])
def form():
    if request.method == 'POST':
        data = request.form 
        # to-do: fix the how to get data from form and put it in session HERE!
        buffer_size= int(request.form.get("NodeSize"))*int(request.form.get("scalingFactor"))
        session["buffer_size"] = buffer_size
        session["satellite"] = request.form.get("Satellite")
        session["nodeLen"] = query_OSM(request.form.get("Query"),buffer_size,request.form.get("Name"))
        session["name"] = request.form.get("Name")
        print("Hello world")
        return redirect(url_for('read_form'))
    return render_template('form.html')
 
# `read-form` endpoint  
@app.route('/read_form', methods=['GET', 'POST']) 
def read_form(): 
    name = session.get("name")
    nodeLen = session.get("nodeLen")
    buffer_size = session.get("buffer_size")
    satellite = session.get("satellite")
    return render_template("data.html",name=name,nodeLen=nodeLen,img_size=buffer_size, satellite=satellite)

    # Get the form data as Python ImmutableDict datatype  

    ## Return the extracted information  
 
# `read-form` endpoint  
@app.route('/get_data', methods=['GET', 'POST']) 
def get_data(): 
    name = session.get("name")
    nodeLen = session.get("nodeLen")
    buffer_size = session.get("buffer_size")
    satellite = session.get("satellite")
    
    return render_template("downloading.html",name=name,nodeLen=nodeLen,img_size=buffer_size, satellite=satellite)
 
 
app.run(host='localhost', port=5000)