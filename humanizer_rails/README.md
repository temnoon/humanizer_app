# Humanizer Rails Backend

A Ruby on Rails API backend for the Humanizer Lighthouse project, designed to work alongside the existing Python API and React frontend.

## Overview

This Rails application provides:

- **LLM Task Management**: Unified logging and tracking of all LLM operations
- **Writebook System**: Structured content creation with versioning
- **Python API Bridge**: Seamless integration with existing Python backend
- **Future Discourse Integration**: Extensible for Discourse plugin development

## Architecture

### Core Models

#### LlmTask
Canonical schema for all LLM operations:
- `task_type`: humanization, summarization, analysis, etc.
- `model_name`: claude-3-sonnet, gpt-4, etc.
- `prompt`, `input`, `output`: Full LLM conversation data
- `metadata`: JSONB field for tokens, cost, duration, etc.
- `result_status`: pending, processing, completed, failed

#### Writebook
Long-form content management:
- `title`, `author`, `version`: Basic metadata
- `published_at`: Publication status
- Has many `WritebookSection`s

#### WritebookSection
Individual sections within writebooks:
- `section_index`: Ordering within writebook
- `title`, `content`: Section data
- `linked_archive_id`: Link to discourse/archive content
- `projection_notes`: Future planning notes

### Services

#### ArchiveClient
HTTParty-based service for communicating with Python backend:
- `get_chat_summary(id)`
- `humanize_text(text, style)`
- `analyze_discourse_posts(posts)`
- `process_with_llm(task_type, prompt, ...)`

## API Endpoints

### LLM Tasks
- `GET /llm_tasks` - List all tasks with filtering
- `POST /llm_tasks` - Create new task (optionally via Python API)
- `GET /llm_tasks/:id` - Show specific task
- `GET /llm_tasks/stats` - Get task statistics

### Writebooks
- `GET /writebooks` - List writebooks
- `POST /writebooks` - Create new writebook
- `PATCH /writebooks/:id/publish` - Publish writebook
- `POST /writebooks/:id/create_version` - Create new version

### Writebook Sections
- `GET /writebooks/:id/sections` - List sections
- `POST /writebooks/:id/sections` - Create section
- `PATCH /writebooks/:id/sections/:id/move_up` - Reorder sections
- `POST /writebooks/:id/sections/:id/generate_content` - Generate via LLM

### Archive Bridge (Python API)
- `GET /api/v1/archive/summary/:id`
- `POST /api/v1/archive/humanize`
- `POST /api/v1/archive/analyze_discourse`
- `GET /api/v1/archive/status`

## Setup

### Prerequisites
```bash
# Install Ruby 2.6+ and Rails
brew install ruby rails
gem install bundler

# Install PostgreSQL
brew install postgresql
```

### Installation
```bash
cd /Users/tem/humanizer-lighthouse/humanizer_rails

# Install gems
bundle install

# Setup database
bin/rails db:create
bin/rails db:migrate

# Start server
bin/rails server
```

### Environment
The Rails app expects your Python API to be running on `http://localhost:5000`. Adjust `ArchiveClient` base_uri if different.

## Integration Strategy

### Phase 1: Parallel Operation
- Rails API runs alongside Python API
- React frontend can call either backend
- Gradual migration of functionality

### Phase 2: Python API Bridge
- Rails becomes primary API
- Python functions called via `ArchiveClient`
- Unified logging in Rails database

### Phase 3: Native Rails
- LLM processing moved to Ruby gems
- Python API deprecated
- Full Rails/Hotwire frontend

### Phase 4: Discourse Plugin
- Extract engines for Discourse compatibility
- Plugin architecture for Discourse integration

## Development

### Testing
```bash
# Run tests (when RSpec is set up)
bundle exec rspec

# Check routes
bin/rails routes

# Console access
bin/rails console
```

### Database Operations
```bash
# Create migration
bin/rails generate migration AddFieldToModel field:type

# Migrate
bin/rails db:migrate

# Rollback
bin/rails db:rollback

# Reset (caution!)
bin/rails db:reset
```

## File Structure
```
humanizer_rails/
├── app/
│   ├── controllers/
│   │   ├── llm_tasks_controller.rb
│   │   ├── writebooks_controller.rb
│   │   └── api/v1/archive_controller.rb
│   ├── models/
│   │   ├── llm_task.rb
│   │   ├── writebook.rb
│   │   └── writebook_section.rb
│   └── services/
│       └── archive_client.rb
├── config/
│   ├── routes.rb
│   ├── database.yml
│   └── application.rb
└── db/
    └── migrate/
        ├── 20250719000001_create_llm_tasks.rb
        ├── 20250719000002_create_writebooks.rb
        └── 20250719000003_create_writebook_sections.rb
```

## Next Steps

1. **Install Rails properly** and run `bundle install`
2. **Set up PostgreSQL** and run migrations
3. **Test Python API integration** via ArchiveClient
4. **Gradually migrate React frontend** to use Rails endpoints
5. **Plan Discourse plugin architecture**

## Future Extensions

- Background job processing (Sidekiq)
- WebSocket support for real-time updates
- File upload handling for document processing
- Advanced search with Elasticsearch
- Caching layer with Redis
- API rate limiting
- Authentication & authorization
