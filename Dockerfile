# API

FROM node:20-alpine AS builder

WORKDIR /app

COPY packages/js/package.json packages/js/package-lock.json /app/packages/js/
RUN cd /app/packages/js && npm ci

COPY data /app/data
COPY packages/js/src /app/packages/js/src
COPY packages/js/tsconfig.json /app/packages/js/
RUN cd /app/packages/js && npm run build

COPY api/package.json api/package-lock.json /app/api/
RUN cd /app/api && npm ci

COPY api/src /app/api/src
COPY api/openapi.yaml /app/api/
COPY api/tsconfig.json /app/api/
RUN cd /app/api && npm run build

FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/api/dist /app/api/dist
COPY --from=builder /app/api/node_modules /app/api/node_modules
COPY --from=builder /app/api/openapi.yaml /app/api/
COPY --from=builder /app/packages/js/dist /app/packages/js/dist
COPY --from=builder /app/packages/js/data /app/packages/js/data
COPY data /app/data

ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

USER node

CMD ["node", "api/dist/app.js"]
