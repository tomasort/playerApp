# Use the official Nginx image from the Docker Hub
FROM nginx:latest

# Copy the custom Nginx configuration file into the container
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create a directory for static files and copy them from the app
RUN mkdir -p /usr/share/nginx/html/static
COPY /StreamerApp/app/static/ /usr/share/nginx/html/static/

# Expose port 80
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
