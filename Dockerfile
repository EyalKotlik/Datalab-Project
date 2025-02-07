FROM python:3.12.8-slim

WORKDIR /"Datalab-Project"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

EXPOSE 8501

# Set the working directory to the app folder
WORKDIR /"Datalab-Project/Description Improver/desc-improver-app"

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
