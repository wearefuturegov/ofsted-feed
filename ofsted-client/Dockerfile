# Use an official Python runtime as a parent image
FROM python:3.12-slim
ARG PORT
ENV PORT=$PORT

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run app.py when the container launches
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --log-level debug app:app
# CMD tail -f /dev/null
# CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
# CMD ["python", "app.py"]

