# Use Python 3.9 slim image as the base image
FROM python:3.9-slim-buster

# Set environment variables
ENV FLASK_APP=wsgi.py \
    FLASK_DEBUG=1 \
    PYTHONUNBUFFERED=1 \
    CONFIG_TYPE=development \
    IN_DOCKER=1 \
    ADMIN_PASSWORD=adminpass \
    JWT_SECRET_KEY=SUPERSECRET \
    IS_DOCKER=1 

# Make directories for the application
RUN mkdir -p /restcalculator
RUN mkdir -p /tests 
# Run setup.py 
#COPY setup.py /tmp/setup.py
#RUN python /tmp/setup.py bdist_wheel

# Copy the application factory file and other source files
COPY restcalculator/ /restcalculator/
COPY tests/ /tests/


# Install any needed packages specified in requirements.txt
COPY restcalculator/requirements_docker.txt /tmp/
RUN pip install -r /tmp/requirements_docker.txt



# Set the working directory
WORKDIR /restcalculator
CMD ["sh", "-c", "python setup_scripts/wait_for_postgres.py && flask run --host=0.0.0.0 --port=8080"]



