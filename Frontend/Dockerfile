FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build


FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx.https.conf /etc/nginx/https.conf

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]
