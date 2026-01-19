FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir requests

# Copy application files
COPY mullvad_device_cleaner.py .
COPY allowed_devices.txt .
COPY cron_script.sh .

# Make the cron script executable
RUN chmod +x cron_script.sh

# Run the cron script
CMD ["./cron_script.sh"]
