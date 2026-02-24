# MySQL Dockerfile - Custom MySQL 8.0 image
FROM mysql:8.0

# Set environment variables
ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-rootpassword}
ENV MYSQL_DATABASE=${MYSQL_DATABASE:-op_cms}
ENV MYSQL_USER=${MYSQL_USER:-op_cms_user}
ENV MYSQL_PASSWORD=${MYSQL_PASSWORD:-op_cms_password}

# Copy custom MySQL configuration
COPY my.cnf /etc/mysql/conf.d/op_cms.cnf

# Create log directory
RUN mkdir -p /var/log/mysql && \
    chown -R mysql:mysql /var/log/mysql

# Expose MySQL port
EXPOSE 3306

# Volume for data persistence
VOLUME /var/lib/mysql

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD} || exit 1

# Default command
CMD ["mysqld"]
