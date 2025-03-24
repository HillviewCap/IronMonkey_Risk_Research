# IronMonkey Risk Research System Architecture

## 1. System Architecture Overview

The IronMonkey Risk Research Platform follows a modular architecture based on Flask blueprints and service-oriented design. This document outlines the technical architecture, component interactions, and implementation details.

```
┌─────────────────────────────────────────────────────────────────┐
│                          Web Interface                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                        Flask Application                        │
│  ┌─────────┐   ┌──────────┐   ┌───────┐   ┌──────┐   ┌───────┐  │
│  │   Auth  │   │  Client  │   │ Risk  │   │ Admin│   │  API  │  │
│  └─────────┘   └──────────┘   └───────┘   └──────┘   └───────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                         Service Layer                           │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐   │
│  │ Elasticsearch│   │    Redis     │   │ Report Generation  │   │
│  └─────────────┘   └──────────────┘   └─────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                         Data Layer                              │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐   │
│  │ PostgreSQL  │   │ Elasticsearch │   │       Redis        │   │
│  └─────────────┘   └──────────────┘   └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Component Details

### 2.1 Flask Application Structure

The application is organized using the blueprint pattern for modularity and maintainability:

- **Auth Blueprint**: User authentication and account management
- **Client Blueprint**: Client profile and asset management
- **Risk Blueprint**: Risk assessment workflows and intelligence
- **Admin Blueprint**: System administration and configuration
- **API Blueprint**: RESTful API endpoints for frontend integration

Each blueprint contains:
- Routes (`routes.py`): URL route handlers
- Models: SQLAlchemy models (shared across blueprints)
- Templates: Jinja2 templates specific to the blueprint
- Forms: WTForms for data validation

### 2.2 Database Design

#### PostgreSQL Schema Structure

- **Client Schema**:
  ```
  clients.organizations
  clients.locations
  clients.contacts
  clients.assets
  clients.relationships
  clients.reports
  clients.settings
  ```

- **User Schema**:
  ```
  users.accounts
  users.roles
  users.permissions
  users.activity_logs
  users.sessions
  ```

- **Application Schema**:
  ```
  app.settings
  app.audit_logs
  app.scheduled_tasks
  app.notifications
  ```

- **Risk Schema**:
  ```
  risk.assessments
  risk.findings
  risk.recommendations
  risk.geo_risks
  risk.cyber_threats
  ```

### 2.3 Search and Analytics

#### Elasticsearch Indices

- **risk_assessments**: Risk assessment data with findings and recommendations
- **geo_risks**: Geopolitical risk intelligence
- **cyber_threats**: Cyber threat intelligence
- **client_assets**: Client asset inventory

#### Index Structure Example (risk_assessments)

```json
{
  "id": 123,
  "client_id": 456,
  "name": "Annual Risk Assessment 2025",
  "description": "Comprehensive assessment of geopolitical and cyber risks",
  "methodology": "Enhanced Framework v2.0",
  "status": "complete",
  "risk_score": 72.5,
  "assessment_date": "2025-03-15",
  "created_at": "2025-02-10T14:30:00Z",
  "updated_at": "2025-03-20T09:15:00Z",
  "findings": [
    {
      "id": 789,
      "title": "Vulnerable Infrastructure in Conflict Zone",
      "description": "Critical infrastructure located in areas of geopolitical tension",
      "risk_level": "High",
      "likelihood": "Medium"
    }
  ],
  "recommendations": [
    {
      "id": 321,
      "title": "Geographic Redundancy Implementation",
      "description": "Implement geographic redundancy for critical systems",
      "priority": "High",
      "status": "open"
    }
  ]
}
```

### 2.4 Caching Strategy

Redis is used for several caching purposes:

- **Session Storage**: User sessions and authentication tokens
- **Query Cache**: Frequently accessed queries with appropriate TTLs
- **Dashboard Data**: Pre-calculated dashboard metrics
- **Rate Limiting**: API rate limiting counters

## 3. Security Implementation

### 3.1 Authentication Flow

1. User submits login credentials
2. Server validates credentials against hashed password
3. On success, creates a session token stored in Redis
4. Session token is sent to client as secure, HTTP-only cookie
5. Subsequent requests include this cookie for authentication

### 3.2 Authorization Model

Role-based access control (RBAC) with the following roles:

- **Admin**: Full system access
- **Analyst**: Access to assessments and intelligence
- **Client Manager**: Access to client management features
- **Viewer**: Read-only access to specific client data

### 3.3 Data Security Measures

- **Password Storage**: bcrypt hashing with appropriate work factor
- **Database Encryption**: Encryption for sensitive fields
- **Transport Security**: HTTPS with TLS 1.3
- **Input Validation**: Form validation, parameterized queries
- **CSRF Protection**: Cross-Site Request Forgery tokens
- **Content Security Policy**: Strict CSP headers

## 4. API Design

### 4.1 RESTful Endpoints

- **Client API**: `/api/clients/`
- **Assessment API**: `/api/assessments/`
- **Intelligence API**: `/api/intelligence/`
- **Dashboard API**: `/api/dashboard-data/`

### 4.2 API Authentication

- JWT (JSON Web Token) based authentication
- Token expiration and refresh mechanism
- Rate limiting to prevent abuse

### 4.3 Response Format

```json
{
  "status": "success",
  "data": {
    // Response data here
  },
  "meta": {
    "page": 1,
    "per_page": 10,
    "total": 42
  }
}
```

## 5. Deployment Strategy

### 5.1 Development Environment

- Local Flask development server
- Docker-based PostgreSQL, Elasticsearch, and Redis
- Debug mode enabled

### 5.2 Production Environment

- Gunicorn WSGI server
- Nginx as reverse proxy
- PostgreSQL with replication
- Elasticsearch cluster
- Redis cluster for high availability
- Monitoring with Prometheus and Grafana

### 5.3 CI/CD Pipeline

- Automated testing with pytest
- Code quality checks with flake8 and black
- Database migrations with Alembic
- Containerized deployment with Docker

## 6. Monitoring and Maintenance

### 6.1 Logging Strategy

- Structured logging with JSON format
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Log aggregation with ELK stack

### 6.2 Performance Monitoring

- Request timing and throughput
- Database query performance
- Cache hit ratios
- Error rates and status codes

### 6.3 Backup Strategy

- Daily PostgreSQL backups
- Elasticsearch snapshots
- Offsite storage for disaster recovery
