FROM python:3.10-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y build-essential libssl-dev libffi-dev python3-dev default-libmysqlclient-dev \
    && apt-get clean



# Set work directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install the required python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . /app/

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
