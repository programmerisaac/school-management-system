# Smart Multi-School Management System

A comprehensive, AI-powered multi-school management system built with Django, HTMX, Alpine.js, and Tailwind CSS. This system allows users to manage multiple schools from a single platform with subscription-based access.

## Features

### Core Features

- **Multi-Tenancy**: One user can own and manage multiple schools
- **School Switching**: Easy switching between schools from the dashboard
- **Subscription Management**: Paystack integration for school subscriptions
- **Role-Based Access Control**: Super Admin, School Owner, School Admin, Principal, Teacher, Staff, Parent, Student
- **Redis Caching**: Optimized database queries with Redis cache
- **Celery Task Queue**: Background tasks for emails, notifications, and reports

### Student Management

- Complete student information system with:
  - Personal information, photos, and contact details
  - Guardian/parent management
  - Admission and enrollment tracking
  - Student ID with QR code generation
  - Medical records and special needs tracking
  - Attendance management
  - Grade and performance tracking

### Staff Management

- Staff information and HR management:
  - Staff profiles with qualifications and documents
  - Employment type and designation tracking
  - Attendance and leave management
  - Subject assignments for teachers
  - Performance tracking

### Academic Management

- **Classes & Subjects**: Manage classes, sections, and subjects
- **Exams & Grading**:
  - Multiple exam types (midterm, final, quiz, test, assignment)
  - Automated grade calculation
  - Report card generation
- **Assignments**: Create and manage homework/assignments with submissions
- **Academic Calendar**: Terms and academic years

### Fee Management

- Fee structure configuration per class
- Student fee tracking
- Payment recording with multiple methods
- Paystack integration for online payments
- Receipt generation
- Fee reminder system
- Discount and scholarship management

### Communications

- Multi-channel notifications (Email, SMS)
- Announcements system
- Parent-teacher messaging
- Automated notifications for:
  - Fee reminders
  - Attendance alerts
  - Exam schedules
  - General announcements

### Parent Portal

- View children's information
- Check attendance and grades
- Pay fees online
- Receive notifications
- Communicate with teachers

## Technology Stack

- **Backend**: Django 5.0.1
- **Frontend**: HTMX, Alpine.js, Tailwind CSS (CDN)
- **Database**: PostgreSQL (recommended) / SQLite (development)
- **Cache**: Redis
- **Task Queue**: Celery with Redis broker
- **Payment**: Paystack
- **File Storage**: Local / AWS S3 (optional)

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL (recommended) or SQLite
- Redis Server
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd school-management-system
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` file with your configuration:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=postgresql://user:password@localhost:5432/school_management
   REDIS_URL=redis://localhost:6379/0
   PAYSTACK_SECRET_KEY=your-paystack-secret-key
   PAYSTACK_PUBLIC_KEY=your-paystack-public-key
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Create static directories**
   ```bash
   mkdir -p static staticfiles media logs
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Start Redis** (in a separate terminal)
   ```bash
   redis-server
   ```

10. **Start Celery Worker** (in a separate terminal)
    ```bash
    celery -A config worker -l info
    ```

11. **Start Celery Beat** (in a separate terminal)
    ```bash
    celery -A config beat -l info
    ```

## Project Structure

```
school-management-system/
├── apps/
│   ├── accounts/          # User authentication and profiles
│   ├── academics/         # Classes, subjects, exams, grading
│   ├── communications/    # Messaging and notifications
│   ├── core/             # Core utilities, middleware, context processors
│   ├── fees/             # Fee management and payments
│   ├── parents/          # Parent portal
│   ├── schools/          # School and subscription management
│   ├── staff/            # Staff and HR management
│   └── students/         # Student information system
├── config/               # Project configuration
│   ├── settings.py      # Django settings
│   ├── urls.py          # Main URL configuration
│   ├── celery.py        # Celery configuration
│   └── wsgi.py          # WSGI configuration
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── components/     # Reusable components (navbar, sidebar)
│   ├── core/          # Core templates
│   ├── accounts/      # Account templates
│   ├── schools/       # School templates
│   ├── students/      # Student templates
│   ├── staff/         # Staff templates
│   ├── academics/     # Academic templates
│   ├── fees/          # Fee templates
│   └── errors/        # Error pages
├── static/            # Static files (CSS, JS, images)
├── media/             # User uploaded files
├── logs/              # Application logs
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Key Models

### User Model (accounts/models.py)
- Custom user model with email authentication
- Role-based user types (Super Admin, School Owner, etc.)
- Profile information and activity logging

### School Model (schools/models.py)
- Multi-tenant school management
- Subscription tracking
- School branding (logo, colors)
- Academic year and term management

### Student Model (students/models.py)
- Complete student information
- QR code for student ID
- Attendance and grade tracking
- Guardian relationships

### Fee Models (fees/models.py)
- Fee structure per class
- Student fee tracking
- Payment records with Paystack integration
- Receipt generation

## Configuration

### Redis Caching

The system uses Redis for:
- Session storage
- Query result caching
- Celery task queue

Key cache functions in `apps/core/cache_utils.py`:
- `cached_queryset()` - Cache queryset results
- `CacheManager.get_school_stats()` - Cached school statistics
- Model-level cache invalidation on save

### Celery Tasks

Scheduled tasks (configured in `config/celery.py`):
- Fee reminders (daily at 9 AM)
- Attendance report generation (weekly)
- Subscription expiry checks (daily at midnight)

### Paystack Integration

Configure in `.env`:
```env
PAYSTACK_SECRET_KEY=sk_test_xxxxx
PAYSTACK_PUBLIC_KEY=pk_test_xxxxx
```

Payment flow:
1. Student fee created in system
2. Parent/Admin initiates payment
3. Redirect to Paystack
4. Webhook handles payment verification
5. Receipt generated automatically

## Multi-Tenancy

The system supports multi-tenancy where:
- One user can own multiple schools
- Each school has isolated data
- Users can switch between schools
- School-specific branding (colors, logo)

Implementation:
- `ActiveSchoolMiddleware` sets the active school in request
- `SchoolSwitchMiddleware` handles school switching
- `@school_required` decorator ensures school is selected
- Context processors add school data to templates

## Security Features

- CSRF protection enabled
- Role-based access control
- Object-level permissions (django-guardian)
- SQL injection protection
- XSS protection
- Secure password hashing
- Activity logging for audit trails

## Branding

Default colors:
- Primary: `#154bba` (Blue)
- Secondary: `#f9d000` (Yellow)

Schools can customize their colors in the school settings.

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings to functions and classes
- Keep functions small and focused

### Database Optimization
- Use `select_related()` and `prefetch_related()` for queries
- Add database indexes on frequently queried fields
- Use Redis cache for expensive queries
- Implement pagination for large querysets

## Deployment

### Production Settings

1. Set `DEBUG=False` in `.env`
2. Configure allowed hosts
3. Set up SSL/TLS
4. Use PostgreSQL database
5. Configure email backend (SMTP)
6. Set up file storage (AWS S3 recommended)
7. Configure Sentry for error tracking

### Using Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

This project is proprietary software. All rights reserved.

## Support

For support, please contact: support@schoolmanagement.com

## Roadmap

### Phase 1 (Current)
- ✅ Multi-school management
- ✅ Student information system
- ✅ Staff management
- ✅ Fee management with Paystack
- ✅ Exam and grading system
- ✅ Basic communications

### Phase 2 (Planned)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics and reporting
- [ ] AI-powered insights
- [ ] Biometric attendance
- [ ] LMS integration
- [ ] Parent mobile app
- [ ] SMS notifications (Twilio)
- [ ] Transport management
- [ ] Library management
- [ ] Inventory management
- [ ] Hostel management

### Phase 3 (Future)
- [ ] Video conferencing integration
- [ ] AI-assisted grading
- [ ] Predictive analytics for student performance
- [ ] Chatbot for FAQs
- [ ] Advanced security features
- [ ] Multi-language support
- [ ] API marketplace

## Credits

Developed with ❤️ using Django, HTMX, Alpine.js, and Tailwind CSS.
