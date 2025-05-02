# 1. Base Image: Use an official Python slim image
FROM python:3.11-slim

# 2. Environment Variables: Ensure logs appear immediately and Flask knows it's production
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
# Optional: If your main file wasn't app.py, you'd set FLASK_APP here

# 3. Working Directory: Set the context within the container
WORKDIR /app

# 4. Copy Requirements: Cache this layer for faster builds if dependencies don't change
COPY requirements.txt .

# 5. Install Dependencies: Use --no-cache-dir to minimize image size
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Application Code: Copy everything else needed for the app
# This includes app.py, forms.py, blueprints/, static/, templates/
COPY . .

# 7. Expose Port: The port Gunicorn will listen on inside the container
# Render prefers 10000, so we'll use that.
EXPOSE 10000

# 8. Run Command: Start the app using Gunicorn
# Bind to 0.0.0.0 to accept connections from Render's proxy.
# Adjust worker count based on Render plan if needed (start with 2-4).
# app:app -> looks for the 'app' instance in the 'app.py' file.
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "3", "app:app"]