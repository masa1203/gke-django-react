# frontend/web-back/Dockerfile
FROM node:12.14.1

WORKDIR /code

# Install dependencies
COPY package.json ./
COPY package-lock.json ./
RUN npm install

# Add rest of the client code
COPY . ./
RUN npm run build

EXPOSE 3000
