FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY mullvad_device_cleaner.py .

# The -u flag is critical for seeing logs in Kubernetes immediately
CMD ["python3", "-u", "mullvad_device_cleaner.py", "--apply", "--interval", "1"]