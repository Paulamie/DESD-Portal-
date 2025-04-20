FROM python:3.12-slim

# Install system dependencies including netcat (for wait-for-it)
RUN apt-get update \
    && apt-get install -y build-essential libssl-dev libffi-dev python3-dev default-libmysqlclient-dev netcat-openbsd \
    && apt-get clean

# Set work directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install the required python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else (including wait-for-it.sh)
COPY . /app/

# Make wait-for-it.sh executable
RUN chmod +x /app/wait-for-it.sh

# Expose the port
EXPOSE 8000
