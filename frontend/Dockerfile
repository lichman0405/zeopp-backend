# Stage 1: Build the Vue.js application
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
# Assuming the vue project is in a subdirectory called 'vue-project' inside 'frontend'
COPY vue-project/package.json ./vue-project/package.json
COPY vue-project/package-lock.json ./vue-project/package-lock.json
# If using yarn:
# COPY vue-project/yarn.lock ./vue-project/yarn.lock

# Change working directory to the vue-project to run npm commands
WORKDIR /app/vue-project

# Install dependencies
RUN npm install
# If using yarn:
# RUN yarn install

# Copy the rest of the application source code
# First go back to /app then copy vue-project
WORKDIR /app
COPY vue-project/ ./vue-project/

# Change working directory to vue-project again to run build
WORKDIR /app/vue-project
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:alpine

# Copy the build output from the builder stage to Nginx html directory
# The output of `npm run build` for Vite/Vue is typically in a 'dist' folder
COPY --from=builder /app/vue-project/dist /usr/share/nginx/html

# Copy the Nginx configuration file
# This assumes nginx.conf is in the root of the 'frontend' directory when building frontend/Dockerfile
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
