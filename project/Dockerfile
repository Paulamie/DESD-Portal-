FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \
    && apt-get clean

# Set work directory
WORKDIR /app

# Copy the requirements file first (for caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Command to run the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

