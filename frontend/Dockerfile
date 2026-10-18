FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
# npm 10.8.2 'edgesOut' bug'ı → npm@11'e yükselt (node:20 uyumlu)
RUN npm install -g npm@11
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:alpine
# Güvenlik: build apt/apk upgrade (Trivy fixable)
RUN apk -U upgrade --no-cache
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

