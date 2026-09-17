FROM node:22-slim AS build

WORKDIR /repo
COPY package.json package-lock.json ./
COPY packages/types/package.json packages/types/
COPY apps/web/package.json apps/web/
RUN npm install

COPY packages/types ./packages/types
COPY apps/web ./apps/web
COPY tsconfig.base.json ./
RUN npm run build:types && npm run build -w @quantastica/web

FROM nginx:1.27-alpine
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /repo/apps/web/dist /usr/share/nginx/html
EXPOSE 80
