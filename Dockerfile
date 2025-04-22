# Use the official Python image as a base
FROM python:3.9-slim

# Install system dependencies required for PyAudio and streamlit-webrtc
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender1 \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port Streamlit will use
EXPOSE 8501

# Set the environment variable for Streamlit
ENV STREAMLIT_SERVER_PORT=8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
