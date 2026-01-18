# Use the official Python image with Playwright pre-installed (saves setup time)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables (Defaults, can be overridden)
ENV HEADLESS=true

# Command to run the automation bot (default behavior)
# Users can also override this to run specific scripts like 'python run_zepto_availability.py'
CMD ["python", "automate_zepto.py"]
