# Use a smaller base image
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl gcc &&  curl https://sh.rustup.rs -sSf | sh -s -- -y && apt-get install --reinstall libc6-dev -y

# Cache dependencies
COPY ./backend/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install aiohttp requests setuptools && \
    pip install -r /tmp/requirements.txt

# Copy application code
WORKDIR /backend
COPY ./backend .

# Expose port and run the application
EXPOSE 8000
CMD ["uvicorn", "app:app", "--reload"]
