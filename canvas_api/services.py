import requests
from django.conf import settings
from typing import Dict, List, Optional, Any


class CanvasAPIService:
    """Service class for interacting with Canvas LMS API"""
    
    def __init__(self):
        self.base_url = settings.CANVAS_API_BASE_URL
        self.token = settings.CANVAS_API_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make a request to the Canvas API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Canvas API request failed: {str(e)}")
    
    def get_courses(self, enrollment_state: str = 'active') -> List[Dict]:
        """Get list of courses for the authenticated user"""
        params = {'enrollment_state': enrollment_state}
        return self._make_request('GET', '/api/v1/courses', params=params)
    
    def get_course(self, course_id: int) -> Dict:
        """Get details of a specific course"""
        return self._make_request('GET', f'/api/v1/courses/{course_id}')
    
    def get_assignments(self, course_id: int) -> List[Dict]:
        """Get assignments for a specific course"""
        return self._make_request('GET', f'/api/v1/courses/{course_id}/assignments')
    
    def get_assignment(self, course_id: int, assignment_id: int) -> Dict:
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