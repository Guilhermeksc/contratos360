# Etapa 1 – Build Angular
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Etapa 2 – Servir via Nginx (para dev local, opcional)
FROM nginx:1.27-alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]