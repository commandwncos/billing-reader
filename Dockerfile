FROM python:3.9-slim  
  
# Set the working directory  
WORKDIR /application  
  
# Copy all files to the application directory  
COPY . .  
  
# Ensure requirements.txt is in the correct location  
# This line is not necessary if requirements.txt is copied above  
# COPY requirements.txt application/requirements.txt  
  
# Upgrade pip and install requirements  
RUN pip install --upgrade pip  
RUN pip install -r requirements.txt  
  
# Update apt and install additional packages  
RUN apt update --yes  
RUN apt upgrade --yes  
RUN apt install poppler-utils --yes  
RUN apt install libzbar0 --yes  
  
# Set environment variables  
ARG MODEL_NAME
ARG API_VERSION 
ARG AZURE_ENDPOINT
ARG API_KEY
  
# Expose the application port  
EXPOSE 3000  
  
# Command to run the application  
CMD ["python", "main.py"]  