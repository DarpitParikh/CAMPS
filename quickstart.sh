#!/bin/bash
# Quick Start Guide for Academic Management System

echo "==================================================="
echo "LDRP Academic Management System - Quick Start"
echo "==================================================="
echo ""

# Check Python version
echo "Checking Python installation..."
python --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Mac/Linux
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt 2>/dev/null || pip install django pandas openpyxl reportlab

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser if database is fresh
echo ""
echo "==================================================="
echo "SETUP COMPLETE!"
echo "==================================================="
echo ""
echo "To create admin account (superuser):"
echo "python manage.py createsuperuser"
echo ""
echo "To start development server:"
echo "python manage.py runserver"
echo ""
echo "Then visit: http://127.0.0.1:8000/"
echo "Admin:    http://127.0.0.1:8000/admin/"
echo ""
