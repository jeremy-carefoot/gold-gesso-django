# Canvas Planner - Development Roadmap

## Project Overview
A Django REST API backend that integrates with Canvas LMS to provide enhanced planning and organization features for university students. Should be useful.

## Current Status ✅
- Basic Django project structure with Django REST Framework
- Canvas API integration service layer
- Authentication setup
- API endpoints for courses, assignments, calendar events, and user profile
- Environment-based configuration

## Immediate Priorities (Week 1)

### 1. Local Data Storage
Add Django models to store user preferences and custom data:
```python
class CourseNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    canvas_course_id = models.IntegerField()
    notes = models.TextField()
    color = models.CharField(max_length=7)  # Hex color for UI
    is_hidden = models.BooleanField(default=False)

class CustomReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    canvas_assignment_id = models.IntegerField()
    reminder_date = models.DateTimeField()
    message = models.TextField()
```

### 2. Assignment Management
- [ ] Aggregate assignments from all courses
- [ ] Add endpoint: `GET /api/assignments/upcoming?days=7`
- [ ] Track completion status locally
- [ ] Add priority/importance flags
- [ ] Custom reminder system

### 3. Caching Layer
Implement caching to reduce Canvas API calls:
```python
from django.core.cache import cache

def get_courses(self):
    cache_key = f"courses_{user_id}_{enrollment_state}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    # Fetch from Canvas...
    cache.set(cache_key, courses, 300)  # 5 min cache
```

## Core Features

### Calendar & Planning
- [ ] Combined calendar view aggregating all course assignments
- [ ] Personal events/deadlines outside of Canvas
- [ ] Export to iCal/Google Calendar
- [ ] Weekly/monthly workload visualization
- [ ] Smart scheduling suggestions

### Grade Management
- [ ] Store historical grades (Canvas doesn't keep history)
- [ ] GPA calculator
- [ ] "What if" grade calculator
- [ ] Grade trends and analytics
- [ ] Course average comparisons

### Smart Notifications
- [ ] New assignment alerts
- [ ] Grade update notifications
- [ ] Due date reminders (configurable: 24hr, 3 days, 1 week)
- [ ] Course announcement notifications
- [ ] Weekly summary emails

## Technical Improvements

### Background Processing
```python
# Using Celery for async tasks
@shared_task
def sync_canvas_data(user_id):
    """Periodically sync Canvas data"""
    # Runs every hour to fetch updates
    
@shared_task
def send_assignment_reminders():
    """Daily task to send due date reminders"""
```

### Real-time Updates
- [ ] WebSocket support using Django Channels
- [ ] Live notifications for grade updates
- [ ] Real-time collaboration features

### Error Handling & Resilience
```python
class CanvasAPIException(Exception):
    pass

class RateLimitException(CanvasAPIException):
    retry_after: int

class CourseNotFoundException(CanvasAPIException):
    pass
```

### API Improvements
- [ ] Pagination for large datasets
- [ ] Filtering and sorting options
- [ ] GraphQL endpoint for complex queries
- [ ] Batch operations support
- [ ] Rate limit handling with exponential backoff

## Data Analysis Features

### Academic Analytics
- [ ] Assignment density heatmap
- [ ] Time management insights
- [ ] Study pattern recommendations
- [ ] Deadline clustering warnings

### Performance Tracking
- [ ] Grade trend visualization
- [ ] Assignment completion rates
- [ ] Time-to-completion metrics
- [ ] Peer comparison (anonymized)

## Architecture Decisions

### Frontend Integration
- **Authentication**: JWT tokens vs Session-based
- **API Design**: REST vs GraphQL for complex queries
- **Real-time**: WebSockets vs Server-Sent Events
- **File Storage**: Local vs S3 for attachments

### Data Strategy
- **Sync Frequency**: Hourly vs on-demand
- **Storage**: What to cache locally vs fetch live
- **Privacy**: Data retention policies
- **Backup**: Canvas downtime contingency

### Scaling Considerations
- Redis for caching and session storage
- PostgreSQL for production database
- Celery with Redis/RabbitMQ for task queue
- Docker containerization
- CI/CD pipeline setup

## MVP Features (Priority Order)

1. **Assignment Aggregator**
   - Unified view of all assignments
   - Sort by due date, course, priority
   - Mark as complete locally

2. **Course Customization**
   - Color coding
   - Custom notes
   - Hide/show courses
   - Course nicknames

3. **Smart Caching**
   - 5-minute course cache
   - 10-minute assignment cache
   - User-triggered refresh

4. **Basic Notifications**
   - Email reminders for due dates
   - Daily digest option
   - Configurable timing

## Future Enhancements

### AI/ML Features
- Assignment time estimation
- Optimal study schedule generation
- Grade prediction models
- Personalized study recommendations

### Collaboration
- Study group formation
- Shared calendars
- Note sharing (with permissions)
- Group project coordination

### Mobile Support
- Mobile-optimized API endpoints
- Push notifications
- Offline support with sync

### Integrations
- Google Calendar sync
- Notion integration
- Todoist/task manager sync
- Discord/Slack notifications

## Security Considerations

- Secure token storage
- API rate limiting
- Input validation and sanitization
- CORS configuration
- Regular security audits
- GDPR/privacy compliance

## Performance Targets

- API response time < 200ms (cached)
- API response time < 2s (Canvas fetch)
- 99.9% uptime
- Support 1000+ concurrent users
- Cache hit rate > 80%

## Development Phases

### Phase 1: Foundation (Current)
- ✅ Basic Canvas integration
- ✅ Authentication system
- ⏳ Local data models
- ⏳ Caching implementation

### Phase 2: Core Features (Weeks 2-4)
- Assignment aggregation
- Course customization
- Basic notifications
- Calendar integration

### Phase 3: Enhancement (Weeks 5-8)
- Analytics dashboard
- Grade tracking
- Advanced notifications
- Performance optimizations

### Phase 4: Scale (Weeks 9-12)
- Production deployment
- Monitoring and logging
- User feedback integration
- Mobile API support

## Success Metrics

- User engagement: Daily active users
- Performance: API response times
- Reliability: Uptime percentage
- Utility: Assignments tracked vs Canvas total
- Satisfaction: User feedback scores

## Notes

- Canvas API has rate limits - implement exponential backoff
- Some universities have custom Canvas configurations
- Consider FERPA compliance for US universities
- Cache invalidation strategy is crucial
- Mobile-first API design for future app