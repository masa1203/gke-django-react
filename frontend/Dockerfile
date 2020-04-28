# frontend/Dockerfile
FROM node:12.14.1

RUN mkdir /code
WORKDIR /code

# Install dependencies
COPY package.json /code/
COPY yarn.lock /code/
RUN yarn install

# Add rest of the client code
COPY . /code/

EXPOSE 3000
