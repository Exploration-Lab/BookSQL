# jsqlparser-as-a-service
JSQLParser as a Service

## Setup Instructions
1. Install Docker using the following link: https://docs.docker.com/get-docker/

## Running Instructions
1. Build the image using the following command: `docker build -t jsqlparser-as-a-service .`
2. Running the image inside a docker container: `docker run -d -p 8079:8079 jsqlparser-as-a-service`