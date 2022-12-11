# Create a layer from the latest python Docker image
FROM python:3.10

# Make the 'app' folder the current working directory
WORKDIR /app

# Copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . .

# Update pip before use it
RUN pip install --upgrade pip

# Install project dependencies
RUN pip3 install -r requirements.txt

# Inform Docker that the container listens on this specified network port at runtime
EXPOSE 5000

# Executable command (command the container executes by default when we launch the built image)
CMD [ "python3", "app.py"]