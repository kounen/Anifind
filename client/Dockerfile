# Create a layer from the node:lts-alpine Docker image
FROM node:lts-alpine

# Make the 'app' folder the current working directory
WORKDIR /app

# Copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . .

# Install project dependencies
RUN yarn install

# Inform Docker that the container listens on this specified network port at runtime
EXPOSE 8080

# Executable command (command the container executes by default when we launch the built image)
CMD [ "yarn", "run", "serve" ]