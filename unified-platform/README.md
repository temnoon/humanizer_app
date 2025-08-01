# Unified Humanizer Platform

A consolidated, production-ready platform for content transformation, search, and curation with comprehensive security and monitoring.

## 🏗️ Architecture

### Unified API Gateway
- **Single entry point** on port 8100
- **FastAPI** with async/await throughout
- **Pydantic models** with comprehensive validation
- **Security middleware** with rate limiting and authentication
- **Real-time WebSocket** support for live updates

### Data Layer
- **PostgreSQL** with vector extensions for structured data
- **Redis** for caching and session management  
- **ChromaDB** for vector similarity search
- **Unified schema** eliminating data duplication

### Security Features
- **JWT authentication** with refresh tokens
- **Rate limiting** per user/IP with Redis backend
- **Request validation** with Pydantic models
- **SQL injection protection** and input sanitization
- **CORS** and security headers configured

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM (for embeddings and vector search)

### One-Command Startup
```bash
# Clone and navigate
cd unified-platform

# Copy environment template
cp .env.example .env

# Edit API keys in .env file
nano .env

# Start everything
docker-compose up -d

# Check status
docker-compose ps
```

### Development Mode
```bash
# Start with live reloading
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# View logs
docker-compose logs -f api
```

## 📡 API Endpoints

### Base URL: `http://localhost:8100`

### System
- `GET /` - API information
- `GET /health` - Health check with dependency status
- `GET /docs` - Interactive API documentation (dev mode)

### Authentication (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /login` - User login (returns JWT)
- `POST /logout` - User logout
- `GET /me` - Current user info

### Content Management (`/api/v1/content`)
- `POST /ingest` - Upload and process content
- `GET /content/{id}` - Retrieve content by ID
- `GET /content` - List content with filtering
- `DELETE /content/{id}` - Delete content

### Search (`/api/v1/search`)
- `POST /semantic` - Vector similarity search
- `POST /fulltext` - Full-text search

### Transformation (`/api/v1/transform`)
- `POST /transform` - Transform content using LPE/Quantum/Maieutic

### LLM Services (`/api/v1/llm`)
- `POST /complete` - Direct LLM completion
- `POST /embed` - Generate embeddings

### WebSocket (`/ws`)
- `/ws/transformations/{session_id}` - Real-time transformation updates

## 🔧 Configuration

All configuration is centralized in `shared/config.py` with no magic numbers:

```python
# Example: Adjust rate limiting
RATE_LIMIT_PER_MINUTE=100

# Example: Change LLM provider
LLM_DEFAULT_PROVIDER=deepseek

# Example: Adjust caching
CACHE_TTL_SECONDS=3600
```

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost:5432/humanizer
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# LLM Providers (at least one required)
DEEPSEEK_API_KEY=your_key
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Optional
DEBUG=false
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=100
```

## 🧪 Testing the API

### Test Content Ingestion
```bash
# Upload text content
curl -X POST "http://localhost:8100/api/v1/content/ingest" \
  -F "content_type=text" \
  -F "source=test" \
  -F "title=Test Document" \
  -F "text_data=This is a test document for the unified platform."

# Upload file
curl -X POST "http://localhost:8100/api/v1/content/ingest" \
  -F "content_type=text" \
  -F "source=file_upload" \
  -F "file=@document.txt"
```

### Test Search
```bash
# Semantic search
curl -X POST "http://localhost:8100/api/v1/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test document",
    "limit": 10,
    "similarity_threshold": 0.7
  }'
```

### Test Transformation
```bash
# Transform content
curl -X POST "http://localhost:8100/api/v1/transform/transform" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Transform this text",
    "engine": "lpe",
    "attributes": {
      "persona": "academic",
      "style": "formal"
    }
  }'
```

## 📊 Monitoring

### Health Checks
```bash
# Basic health
curl http://localhost:8100/health

# Detailed status
curl http://localhost:8100/health | jq
```

### Logs
```bash
# Application logs
docker-compose logs -f api

# Database logs  
docker-compose logs -f db

# All services
docker-compose logs -f
```

### Metrics (Optional)
```bash
# Start monitoring stack
docker-compose --profile monitoring up -d

# Access Grafana
open http://localhost:3000
# Login: admin / admin (change password!)

# Access Prometheus
open http://localhost:9090
```

## 🔍 Key Features

### Zero Magic Numbers
- All timeouts, limits, dimensions, models configurable
- Centralized configuration system
- Environment-specific overrides

### Comprehensive Validation
- Pydantic models with detailed constraints
- Input sanitization and size limits
- Type safety throughout

### Production Security
- Rate limiting with burst protection
- Request size limits
- SQL injection prevention
- XSS protection headers
- CORS configuration

### Performance Optimized
- Multi-tier caching (local + Redis)
- Database connection pooling
- Async/await throughout
- Vector search indexing

### Observability
- Structured JSON logging
- Performance monitoring
- Error tracking with context
- Health check endpoints

## 📈 Migration from Existing Services

### Phase 1: Parallel Operation
1. Deploy unified platform alongside existing services
2. Test API endpoints for parity
3. Validate data migration scripts

### Phase 2: Data Migration
1. Export data from existing services
2. Import to unified PostgreSQL schema
3. Verify data integrity

### Phase 3: Traffic Migration
1. Update client applications to use unified API
2. Monitor performance and error rates
3. Gradually retire old services

### Phase 4: Cleanup
1. Remove old service containers
2. Clean up unused data volumes
3. Update documentation

## 🛟 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check what's using port 8100
lsof -i :8100

# Kill conflicting processes
docker-compose down
```

**Database connection issues:**
```bash
# Check database status
docker-compose exec db pg_isready

# View database logs
docker-compose logs db
```

**Memory issues:**
```bash
# Check Docker resource usage
docker stats

# Increase Docker memory limit (8GB+ recommended)
```

**API key errors:**
```bash
# Verify environment variables
docker-compose exec api env | grep API_KEY

# Test LLM connectivity
curl -X POST "http://localhost:8100/api/v1/llm/complete" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

## 📚 Development

### Adding New Features
1. Define Pydantic models in `shared/models.py`
2. Add configuration in `shared/config.py`
3. Implement router in `api/routers/`
4. Add tests in `tests/`
5. Update documentation

### Database Migrations
```bash
# Create migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migration
docker-compose exec api alembic upgrade head
```

## 🤝 Contributing

1. Follow the established patterns for security and validation
2. Add comprehensive tests for new features
3. Update configuration system for any new parameters
4. Document API changes in OpenAPI specs

---

**Ready for production deployment with proper security, monitoring, and scalability! 🚀**