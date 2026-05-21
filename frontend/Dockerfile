FROM node:20-alpine

WORKDIR /app

# Install pnpm
# RUN npm install -g pnpm

# Copy package files
COPY pnpm-lock.yaml package.json ./

# Install dependencies
#RUN pnpm install

# Copy application code
COPY . .

# Build the application
#RUN pnpm build
RUN npm install
# RUN npm run dev

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "run", "dev"]

