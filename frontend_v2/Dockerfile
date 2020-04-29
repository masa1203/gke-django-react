# frontend/Dockerfile
FROM node:12.14.1

RUN mkdir /code
WORKDIR /code

# Install dependencies
COPY package.json /code/
COPY package-lock.json /code/
RUN npm install

# Add rest of the client code
COPY . /code/

EXPOSE 3000
