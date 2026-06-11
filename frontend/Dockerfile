FROM node:20-alpine@sha256:a32ba75d0ff3fd3cedc8e8521279a2e59b51e01ead3ed10bd5e92589f25823ef AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:20-alpine@sha256:a32ba75d0ff3fd3cedc8e8521279a2e59b51e01ead3ed10bd5e92589f25823ef AS runner

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/next.config.* ./
COPY --from=builder /app/next-env.d.ts ./

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 3000

CMD ["npm", "run", "start"]
