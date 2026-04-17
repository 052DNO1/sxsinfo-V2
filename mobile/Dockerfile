FROM node:22 AS build-stage
WORKDIR /app

ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV ELECTRON_SKIP_BINARY_DOWNLOAD=1

ARG VITE_PASSWORD_ENCRYPT_KEY
ENV VITE_PASSWORD_ENCRYPT_KEY=$VITE_PASSWORD_ENCRYPT_KEY

COPY package.json yarn.lock ./
RUN yarn config set registry https://registry.npmmirror.com/ && yarn install

COPY . .
RUN chmod +x node_modules/.bin/vite
RUN yarn build

FROM alpine:latest
COPY --from=build-stage /app/dist /app/dist
VOLUME ["/app/dist"]
CMD ["tail", "-f", "/dev/null"]
