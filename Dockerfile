FROM python:3.9

# Set working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Install mage-ai
RUN pip install mage-ai

# Expose port for Mage.ai UI
EXPOSE 6789

# Default command to run Mage.ai
CMD ["mage", "start", "ff-transform-pipeline"]
