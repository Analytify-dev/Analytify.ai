# Stage 1: Build the Angular application
FROM node:20.15 AS build

WORKDIR /app

RUN rm -rf node_modules package-lock.json

RUN npm cache clean     --force

COPY package.json  ./

ENV NODE_OPTIONS="--max_old_space_size=4096"

RUN npm install  --legacy-peer-deps

RUN npm install -g @angular/cli

COPY . .

CMD [ "npm","start","--host 0.0.0.0 --port 4000" ]

RUN npm run build 

# # Stage 2: Serve the application with Nginx
FROM nginx:alpine

COPY --from=build /app/dist/Analytify-Angular/browser /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]


# FROM caddy:alpine

# # Copy build output
# COPY dist/Analytify-Angular /usr/share/caddy

# # Copy Caddyfile
# COPY Caddyfile /etc/caddy/Caddyfile

