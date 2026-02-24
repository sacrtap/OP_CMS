# Redis Dockerfile - Custom Redis 7.x image
FROM redis:7-alpine

# Set environment variables
ENV REDIS_PASSWORD=${REDIS_PASSWORD:-redispassword}

# Copy custom Redis configuration
COPY redis.conf /usr/local/etc/redis/redis.conf

# Create data directory
RUN mkdir -p /data

# Expose Redis port
EXPOSE 6379

# Volume for data persistence
VOLUME /data

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD redis-cli -a ${REDIS_PASSWORD} ping | grep -q PONG || exit 1

# Start Redis with custom config
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
