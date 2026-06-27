FROM node:20-alpine

WORKDIR /app

COPY packages/js/package.json packages/js/package-lock.json /app/lib/
RUN cd /app/lib && npm ci --production

COPY packages/js/dist /app/lib/dist
COPY packages/js/data /app/lib/data

COPY api/package.json api/package-lock.json /app/api/
RUN cd /app/api && npm ci --production

COPY api/src /app/api/src
COPY api/openapi.yaml /app/api/openapi.yaml
COPY api/tsconfig.json /app/api/tsconfig.json
RUN cd /app/api && npm run build

COPY data /app/data

ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

CMD ["node", "api/dist/app.js"]
