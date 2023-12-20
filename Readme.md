# General Windows setup
Prerequirements: Python (was tested for > 3.9) and Pip
## Clone the project to your local machine
```
git clone <repository_url>
```
## Optional: Create Virtual Environment for local dependencies (Windows):
```
pip install virtualenv
```
```
python -m venv venv
```
```
venv\Scripts\activate
```
## Install Project Dependencies 
```
pip install -r requirements.txt
```
## Google Earth Engine

Install Google Cloud CLI for GEE to work without docker:
see https://cloud.google.com/sdk/docs/install

Install fiftyone Desktop to use the desktop version - this is only necessery if you want to visualize the resulting COCO dataset with the fiftyone app. 
```
pip install "fiftyone[desktop]"
```

3. Navigate into the src folder 
```
cd /src
```
4. Start code with the following comand: 
```
python modules/main.py
``` 

# ------- DOCKER --------
## Build Docker 
```
docker build -t satellite_osm_dataset .
```

## Run Docker 
```
docker run -i -t satellite_osm_dataset
```
