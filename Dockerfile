FROM oven/bun:1.2.5 AS build
WORKDIR /app
COPY package.json vite.config.ts ./
COPY src ./src
RUN bun install
RUN bun run build

FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist ./
EXPOSE 80
