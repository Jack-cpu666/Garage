#!/bin/bash
# Render.com start script for Metropolis Parking Management System

echo "=================================================================================="
echo "METROPOLIS PARKING MANAGEMENT SYSTEM - STARTING ON RENDER.COM"
echo "=================================================================================="

# Check if required environment variables are set
if [ -z "$ADMIN_PASSWORD" ]; then
    echo "WARNING: ADMIN_PASSWORD not set. Using default 'admin555'"
    export ADMIN_PASSWORD="admin555"
fi

if [ -z "$SECRET_KEY" ]; then
    echo "WARNING: SECRET_KEY not set. Generating random key..."
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
fi

# Display configuration (without exposing secrets)
echo "Configuration:"
echo "  PORT: ${PORT:-10000}"
echo "  BASE_URL: ${BASE_URL:-https://specialist.api.metropolis.io}"
echo "  SITE_ID: ${SITE_ID:-4005}"
echo "  AUTO_TOKEN_REFRESH: ${AUTO_TOKEN_REFRESH:-false}"
echo ""

# Start the application with gunicorn
echo "Starting application with gunicorn..."
exec gunicorn app:app \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
