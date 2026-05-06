# Build stage for React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Backend stage
FROM python:3.11-slim
WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend to backend static files
COPY --from=frontend-builder /app/dist ./static

# Install a simple static file server (whitenoise or serve with FastAPI)
RUN pip install --no-cache-dir whitenoise

# Expose port
EXPOSE 8000

# Run backend
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]