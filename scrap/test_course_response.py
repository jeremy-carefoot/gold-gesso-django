#!/usr/bin/env python
"""
Simple script to test Canvas API connection.
Run this after setting up your .env file to verify your token works.
"""

import os
import sys
import json
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canvas_backend.settings')
django.setup()

from canvas_api.services import CanvasAPIService
from django.conf import settings


def test_canvas_connection():
    """Test the Canvas API connection and display results"""
    
    service = CanvasAPIService()
    
    # Create output directory if it doesn't exist
    output_dir = Path('./canvasResponses')
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Try to get user profile (simplest authenticated endpoint)
        profile = service.get_user_profile()

        # Get assignments for course 26907
        assignments = service._make_request('GET', f'/api/v1/courses/{26907}/assignments')
        
        # Save assignments to JSON file
        assignments_file = output_dir / 'assignmentsResponse.json'
        with open(assignments_file, 'w') as f:
            json.dump(assignments, f, indent=2)
        print(f"Assignments saved to {assignments_file}")
        
        # Get all courses
        courses = service._make_request('GET', '/api/v1/courses')
        
        # Save courses to JSON file
        courses_file = output_dir / 'coursesResponse.json'
        with open(courses_file, 'w') as f:
            json.dump(courses, f, indent=2)
        print(f"Courses saved to {courses_file}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = test_canvas_connection()
    sys.exit(0 if success else 1)