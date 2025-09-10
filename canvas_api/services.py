import requests
from django.conf import settings
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp


class CanvasAPIService:
    """Service class for interacting with Canvas LMS API"""
    
    def __init__(self, user=None):
        self.base_url = settings.CANVAS_API_BASE_URL
        
        # Use user's Canvas token if user is provided, otherwise fall back to settings
        if user and hasattr(user, 'canvas_auth_token') and user.canvas_auth_token:
            self.token = user.canvas_auth_token
        else:
            # Fallback to settings token (for backwards compatibility or admin use)
            self.token = settings.CANVAS_API_TOKEN
            
        if not self.token:
            raise ValueError("No Canvas API token available. User must set their Canvas token.")
            
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        self.session = None

    async def __aenter__(self):
        """Create aiohttp session on the context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session on context manager exit"""
        if self.session:
            await self.session.close()
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make a request to the Canvas API"""
        url = f"{self.base_url}{endpoint}"

        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                # headers=self.headers,
                json=data,
                params=params
            ) as response:
                response.raise_for_status()
                content = await response.text()
                if content:
                    import json
                    return json.loads(content)
                return {}
        except aiohttp.ClientError as e:
            raise Exception(f"Canvas API request failed: {str(e)}")
    
    async def get_courses(self, enrollment_state: str = 'active') -> List[Dict]:
        """Get list of courses for the authenticated user
        
        Canvas API parameters used:
        - enrollment_state: Filter by enrollment state
        - include[]: Additional data to include
        - per_page: Number of results (max 100)
        """
        params = {
            'enrollment_state': enrollment_state,
            'include[]': [
                'term',           # Include term information
                'course_progress',  # Include progress info
                'sections',       # Include course sections
                'total_scores',   # Include grade info
                'current_grading_period_scores',  # Current grades
                'course_image',   # Course banner image
                'concluded'       # Include concluded courses
            ],
            'per_page': 100  # Get more results at once
        }
        return await self._make_request('GET', '/api/v1/courses', params=params)
    
    def get_course(self, course_id: int) -> Dict: # Not being used
        """Get details of a specific course"""
        return self._make_request('GET', f'/api/v1/courses/{course_id}')
    
    async def get_course_assignments(self, course_id: int, params:dict=dict()) -> List[Dict]:
        """Get assignments for a specific course"""
        params["order_by"] = "due_at"
        return await self._make_request('GET', f'/api/v1/courses/{course_id}/assignments', params=params)
    

# These views are actually bad because they still need the course id. I need to make them not do that and instead work on all courses
# None of the below are being used
    def get_unsubmitted_assignments(self, course_id: int) -> List[Dict]:
        """Get unsubmitted assignments for a specific course"""
        params = {
            "bucket":"unsubmitted",
        }
        return self.get_assignment(course_id=course_id, params=params)
    
    def get_overdue_assignments(self, course_id: int) -> List[Dict]:
        """Get pverdue assignments for a specific course"""
        params = {
            "bucket":"overdue",
        }
        return self.get_assignment(course_id=course_id, params=params)
     



    def get_assignment(self, course_id: int, assignment_id: int) -> Dict: # Make this so that we don't need to pass the course id here
        """Get details of a specific assignment"""
        return self._make_request('GET', f'/api/v1/courses/{course_id}/assignments/{assignment_id}')
    

    
    def get_calendar_events(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Get calendar events"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self._make_request('GET', '/api/v1/calendar_events', params=params)
    
    def get_user_profile(self) -> Dict:
        """Get the current user's profile"""
        return self._make_request('GET', '/api/v1/users/self/profile')