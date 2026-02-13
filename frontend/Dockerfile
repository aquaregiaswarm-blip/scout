# Scout Frontend Dockerfile
FROM node:20-alpine AS base

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Development target
FROM base AS development
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Build target
FROM base AS builder
ENV NEXT_TELEMETRY_DISABLED=1
# Set API URL at build time for Next.js
ENV NEXT_PUBLIC_API_URL=https://scout-backend-841327020312.us-east1.run.app/api/v1
RUN npm run build

# Production target
FROM node:20-alpine AS production
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy public folder if it exists (use shell to handle missing folder)
COPY --from=builder /app/public* ./public/
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000

CMD ["node", "server.js"]
