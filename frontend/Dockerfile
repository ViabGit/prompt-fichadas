# Dockerfile simplificado para producción
FROM node:18-alpine as build

WORKDIR /app

# Instalar Angular CLI globalmente
RUN npm install -g @angular/cli@17

# Copiar package.json
COPY package.json ./

# Instalar dependencias
RUN npm install

# Copiar código fuente
COPY . .

# Build de producción
RUN ng build --configuration production

# Usar nginx para servir
FROM nginx:alpine

# Copiar archivos build
COPY --from=build /app/dist/fichadas-frontend /usr/share/nginx/html

# Copiar configuración nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Exponer puerto
EXPOSE 80

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]