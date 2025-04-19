FROM python:3.11.5-slim

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies for psycopg2 with specific versions and clean up in one layer
RUN apt-get update && apt-get install \
    dnsutils=1:9.11.5.P4+dfsg-5.1+deb10u11 \
    libpq-dev=11.16-0+deb10u1 \
    python3-dev=3.12.4 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==25.0.1 \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run migrations
RUN python manage.py collectstatic --noinput || echo "Static files collection optional"
RUN python manage.py migrate

EXPOSE 8000

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "pygoat.wsgi"]