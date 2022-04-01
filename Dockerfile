# This import the python image from Docker Hub
FROM python 
# We tell the Docker Daemon to create a work directory in Docker
WORKDIR /app
# We copy all the files from the current directory inside our virtual directory
COPY . /app
#We install the dependencies of the project
RUN pip install -r requirements.txt
#When we run the image, this command will be launch
CMD ["python", "main.py"]
