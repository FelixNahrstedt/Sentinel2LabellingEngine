from flask import Flask,render_template,request
from modules.OverpassQuery import query_OSM


app = Flask(__name__)
 
@app.route('/', methods = ['GET'])
def form():
    return render_template('form.html')
 
# `read-form` endpoint  
@app.route('/read-form', methods=['POST']) 
def read_form(): 
  
    # Get the form data as Python ImmutableDict datatype  
    data = request.form 
    buffer_size = data["Nodesize"]*data["scalingFactor"]
    query_OSM(data["Query"],buffer_size,data["Name"])
    ## Return the extracted information  
    return render_template('data.html')
 
 
app.run(host='localhost', port=4000)