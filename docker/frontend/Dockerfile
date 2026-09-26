# ============================================================
# SmartFit Frontend Dockerfile (Development Mode)
# ============================================================

FROM node:20-alpine

WORKDIR /app

# Copy dependency definitions from the root build context
COPY frontend/package*.json ./

RUN npm install

# Copy frontend source files
COPY frontend/ ./

EXPOSE 5173

# Bind Vite dev server to 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]