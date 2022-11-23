# Create a layer from the node:lts-alpine Docker image
FROM node:lts-alpine

# Install simple http server for serving static content
RUN npm install -g serve

# Make the 'app' folder the current working directory
WORKDIR /app

# Copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json ./

# Install project dependencies
RUN npm install

# Copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . .

# Build app for production with minification
RUN npm run build

# Inform Docker that the container listens on this specified network port at runtime
EXPOSE 8080

# Executable command (command the container executes by default when we launch the built image)
CMD [ "serve", "-s", "dist" ]