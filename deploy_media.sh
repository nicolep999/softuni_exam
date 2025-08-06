#!/bin/bash

# Deploy media files to Railway volume
echo "Deploying media files to Railway..."

# Create media directory in volume if it doesn't exist
mkdir -p /app/media

# Copy all media files to the volume
cp -r media/* /app/media/

echo "Media files deployed successfully!"
echo "Files copied:"
ls -la /app/media/ 