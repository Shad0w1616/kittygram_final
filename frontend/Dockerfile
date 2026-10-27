FROM node:18
WORKDIR /app

COPY package.json package.json
COPY package-lock.json package-lock.json

RUN npm ci

COPY . .
ENV PUBLIC_URL=/kittygram
RUN npm run build
