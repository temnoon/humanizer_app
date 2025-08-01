# Rails Integration - Humanizer Lighthouse Books System

## 🎯 Overview

I've successfully created a new Ruby on Rails application that implements the book-centric approach with allegory engine integration, designed as the foundation for Discourse integration and WriteBooks export.

## 🏗️ Architecture Summary

### Core Philosophy
- **Conversations → Sections → Books**: Clear path from imported conversations to structured books
- **Allegory Engine Integration**: Quantum-inspired narrative transformation based on theoretical framework
- **Unified Storage**: Single source of truth for all conversation types (ChatGPT, Discourse, manual)
- **Export Flexibility**: Multiple output formats (PDF, WriteBooks, Markdown, EPUB)

### Database Schema

```
conversations (string ID)
├── title, source_type, original_id
├── metadata (JSONB), message_count, word_count
└── messages (string ID)
    ├── role, content, message_index
    ├── parent_message_id (threading)
    └── message_media
        └── media_type, file_path, content_hash

writebooks
├── title, author, version, genre, target_audience
├── allegory_settings (JSONB)
└── writebook_sections
    ├── source_conversation_id, source_message_id
    ├── allegory_attributes (JSONB)
    └── content, section_index
```

## 🚀 Key Features Implemented

### 1. Unified Conversation Management
- **Import System**: ChatGPT conversation.json with media support
- **Duplicate Detection**: Content-based checksums prevent reimports
- **UUID Preservation**: Maintains original ChatGPT message IDs
- **Threading Support**: Parent-child message relationships

### 2. Book-Centric Workflow
- **Conversation to Book**: Direct conversion with customizable options
- **Section Management**: Each message becomes a book section
- **Source Tracking**: Maintains links between sections and original messages
- **Version Control**: Book versioning with transformation history

### 3. Allegory Engine Integration
- **Theoretical Foundation**: Based on quantum measurement framework from Narrative Theory Overview
- **SIC-POVM Semantic Probes**: Informationally complete meaning space coverage
- **Attribute Operators**: Namespace, persona, style transformations
- **Coherence Constraints**: Born rule analogues for consistent transformations

### 4. API Endpoints

#### Conversations API
```
GET    /conversations              # List with pagination/search
POST   /conversations/import       # Import conversation.json
GET    /conversations/:id          # Get conversation with messages
POST   /conversations/:id/transform # Apply allegory transformation
POST   /conversations/:id/export_to_book # Convert to book
GET    /conversations/search       # Full-text search
GET    /conversations/stats        # Usage statistics
```

#### Writebooks API
```
GET    /writebooks                 # List books with filters
POST   /writebooks                 # Create new book
POST   /writebooks/from_conversation # Create from conversation
POST   /writebooks/:id/transform   # Apply allegory transformation
GET    /writebooks/:id/export      # Export in various formats
PATCH  /writebooks/:id/publish     # Publish book
```

## 🔧 Technical Implementation

### Models

#### Conversation Model
```ruby
# Unified conversation storage with ChatGPT import
class Conversation < ApplicationRecord
  self.primary_key = :id # String UUID
  
  has_many :messages, dependent: :destroy
  has_many :writebook_sections, foreign_key: :source_conversation_id
  
  def self.import_from_chatgpt(conversation_data, media_files = [])
    # Preserves original UUIDs, handles media, prevents duplicates
  end
  
  def apply_allegory_transformation(attributes = {})
    # Quantum-inspired narrative transformation
  end
end
```

#### Message Model
```ruby
# Individual messages with threading and media support
class Message < ApplicationRecord
  belongs_to :conversation
  belongs_to :parent_message, optional: true
  has_many :message_media, dependent: :destroy
  
  def to_book_section(writebook, options = {})
    # Convert message to formatted book section
  end
end
```

#### Writebook Model
```ruby
# Enhanced with allegory engine and conversation integration
class Writebook < ApplicationRecord
  has_many :writebook_sections, dependent: :destroy
  has_many :source_conversations, through: :writebook_sections
  
  def self.create_from_conversation(conversation, options = {})
    # Direct conversation to book conversion
  end
  
  def export_to_format(format, options = {})
    # PDF, WriteBooks, Markdown, EPUB export
  end
end
```

### Services

#### AllegoryTransformationService
```ruby
# Implements quantum-inspired narrative transformation
class AllegoryTransformationService
  def initialize(namespace: 'lamish-galaxy', persona: 'temnoon', style: 'contemplative')
    @semantic_probes = initialize_semantic_probes # SIC-POVM structure
  end
  
  def transform_content(content:, role:, context: {})
    # 1. Semantic Measurement (POVM application)
    # 2. Apply Attribute Operators (namespace, persona, style) 
    # 3. Generate Narrative Output (Born rule analogue)
  end
end
```

## 🌐 Integration Points

### Python Backend Integration
- **HTTP Bridge**: AllegoryTransformationService calls Python API at localhost:8100
- **Fallback Modes**: Graceful degradation when Python API unavailable
- **Semantic Measurements**: Quantum-inspired probes for meaning analysis

### Discourse Integration Framework
- **Plugin Architecture**: Designed for Discourse plugin extraction
- **Unified Models**: Compatible with Discourse post/topic structure
- **API Compatibility**: RESTful design matches Discourse patterns

### WriteBooks Export
- **Format Preservation**: Maintains WriteBooks simplicity
- **Section-Based**: Each message = one section structure
- **Metadata Integration**: Author, genre, audience tracking

## 📊 Current Status

### ✅ Completed
- Database schema with full relationships
- Conversation import system (ChatGPT JSON)
- Book creation and management
- Allegory engine theoretical integration
- API endpoints with proper error handling
- Rails server running on port 9000

### 🔄 Next Steps
1. **Discourse Integration**: Plugin architecture and API bridges
2. **Export Systems**: PDF generation, WriteBooks format export
3. **Frontend Integration**: React components for book management
4. **Testing**: Comprehensive test suite
5. **Production**: Deployment configuration

## 🎓 Theoretical Foundation

Based on the **Narrative Theory Overview** conversation analysis:

### Quantum-Inspired Framework
- **Subjective Ontology**: All narrative exists in reader's consciousness
- **Measurement Protocol**: Reading as quantum measurement process
- **SIC-POVM Coverage**: Uniform semantic space probing
- **Coherence Constraints**: Born rule analogues for consistent transformations

### Practical Implementation
- **Semantic Probes**: 16 informationally complete meaning detectors
- **Attribute Operators**: Learnable transformations for namespace/persona/style
- **Embedding Integration**: Bridge to LLM embedding spaces
- **Multi-Scale Consistency**: Framework scales from messages to entire books

## 🚀 Quick Start

```bash
# Start Rails server
cd /Users/tem/humanizer-lighthouse/humanizer_rails
bin/rails server --port=9000

# Test endpoints
curl http://127.0.0.1:9000/conversations
curl http://127.0.0.1:9000/writebooks

# Import a conversation
curl -X POST http://127.0.0.1:9000/conversations/import \
  -F "conversation_file=@conversation.json"

# Create book from conversation  
curl -X POST http://127.0.0.1:9000/writebooks/from_conversation \
  -d "conversation_id=CONV_ID" \
  -d "title=My New Book"
```

This Rails application provides the foundation for a sophisticated book-centric content management system with theoretical rigor and practical flexibility for Discourse integration and WriteBooks compatibility.