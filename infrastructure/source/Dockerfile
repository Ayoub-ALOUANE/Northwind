FROM postgres:16

# Install Python 3 and PostgreSQL client library
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-psycopg2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy entrypoint script and ensure execution permissions
COPY entrypoint.sh /usr/local/bin/custom-entrypoint.sh
RUN chmod +x /usr/local/bin/custom-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]
CMD ["postgres"]
