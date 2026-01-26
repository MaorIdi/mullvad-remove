FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY mullvad_device_cleaner.py .
COPY cron_script.sh .

# Copy default allowed_devices.txt (can be overridden by volume mount)
COPY allowed_devices.txt .

# Make the script executable
RUN chmod +x cron_script.sh

# Health check to ensure the script is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD pgrep -f mullvad_device_cleaner.py || exit 1

# Run the script
CMD ["./cron_script.sh"]
