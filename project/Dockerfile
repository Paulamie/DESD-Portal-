FROM python:3.12-slim

# Install system dependencies for MySQL and Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    netcat-openbsd \
    mariadb-client \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . /app/

# Make wait-for-it script executable
RUN chmod +x /app/wait-for-it.sh

# Expose port
EXPOSE 8000

# Wait for DB and start Django
CMD ["sh", "-c", "/app/wait-for-it.sh db:3306 -- python manage.py runserver 0.0.0.0:8000"]
