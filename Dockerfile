# start by pulling the python image
FROM python:3.9-slim

# copy the requirements file into the image
COPY ./requirements.txt /src/requirements.txt

# switch working directory
WORKDIR /src

# For Fiona to run properly
RUN apt-get update
RUN apt-get install -y gdal-bin libgdal-dev g++
# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY ./src /src
COPY ./data /data

# configure the container to run in an executed manner
#ENTRYPOINT [ "python" ]

#EXPOSE 5000

CMD [ "python", "modules/main.py" ]  
