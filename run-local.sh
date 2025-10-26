#!/bin/bash

# Metropolis Parking Management - Local Testing Script
echo "=================================================================================="
echo "METROPOLIS PARKING MANAGEMENT SYSTEM - LOCAL TESTING"
echo "=================================================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check if user wants Selenium
read -p "Do you want to enable auto token refresh? (requires Chrome/Edge/Firefox) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 Installing Selenium for auto token refresh..."
    pip install selenium==4.16.0
    export AUTO_TOKEN_REFRESH=true
else
    export AUTO_TOKEN_REFRESH=false
fi

# Set environment variables for testing
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
export ADMIN_PASSWORD="admin"
export PORT=5000

echo ""
echo "=================================================================================="
echo "✅ Setup complete!"
echo "=================================================================================="
echo ""
echo "📝 Your login credentials:"
echo "   Password: admin"
echo ""
echo "🚀 Starting server at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================================================="

# Run the application
python3 app.py
