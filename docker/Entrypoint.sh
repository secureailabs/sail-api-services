#!/bin/bash
set -e
imageName=apiservices

# Start the nginx server
# nginx -g 'daemon off;' 2>&1 | tee /app/nginx.log &

# Use the InitializationVector to populate the IP address of the audit services
auditIP=$(cat /InitializationVector.json | jq -r '.audit_service_ip')

# Start the local mongodb database
mongod --port 27017 --dbpath /srv/mongodb/db0 --bind_ip localhost --fork --logpath /var/log/mongod.log

# modify the audit service ip of promtail config file
sed -i "s,auditserver,$auditIP,g" /promtail_local_config.yaml

# Start the promtail client
/promtail_linux_amd64 -config.file=/promtail_local_config.yaml  > /promtail.log 2>&1&

# Start the Public API Server
uvicorn app.main:server --host 0.0.0.0 --port 8000

# To keep the container running
tail -f /dev/null
