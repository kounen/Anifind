# Create a layer from the 3.8-slim-buster Docker image
FROM python:3.8-slim-buster

# Working directory
WORKDIR /app

# Copy the dependencies
COPY requirements.txt

# Install the dependencies (image build step)
RUN pip3 install -r requirements.txt

# Copy the files
COPY . .

# Inform Docker that the container listens on this specified network port at runtime
EXPOSE 3000

# Executable command (command the container executes by default when we launch the built image)
# --host=0.0.0.0 tells to the operating system to listen on all public IPs including frontend IP
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]