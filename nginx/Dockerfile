# Stage 1: Build Portfolio frontend
FROM node:20-alpine AS portfolio-build
WORKDIR /portfolio
COPY portfolio/package.json portfolio/package-lock.json ./
RUN npm ci --prefer-offline
COPY portfolio/ .
RUN npm run build

# Stage 2: Build React blackbird frontend
FROM node:20-alpine AS blackbird-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --prefer-offline
COPY frontend/ .
RUN npm run build

# Stage 3: Nginx serving built frontend + acting as reverse proxy
FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/conf.d/ /etc/nginx/conf.d/
COPY --from=portfolio-build /portfolio/dist /usr/share/nginx/html/portfolio
COPY --from=blackbird-build /frontend/dist /usr/share/nginx/html/blackbird
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]

