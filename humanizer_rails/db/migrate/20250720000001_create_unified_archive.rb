# frozen_string_literal: true

class CreateUnifiedArchive < ActiveRecord::Migration[7.0]
  def up
    # Create unified archive content table
    create_table :archived_contents, id: :bigserial do |t|
      # Core identification
      t.string :source_type, null: false, index: true
      t.string :source_id, null: false, index: true
      t.bigint :parent_id, index: true
      
      # Content classification
      t.string :content_type, null: false, index: true
      t.text :title
      t.text :body_text
      t.jsonb :raw_content
      
      # Metadata
      t.string :author, index: true
      t.text :participants, array: true, default: []
      t.timestamptz :timestamp, index: true
      t.jsonb :source_metadata
      
      # AI Processing Results
      t.text :semantic_vector  # JSON string for now
      t.jsonb :extracted_attributes
      t.float :content_quality_score
      t.string :processing_status, default: 'pending'
      
      # Search and indexing
      t.text :search_terms, array: true, default: []
      t.string :language_detected, limit: 10
      t.bigint :word_count
      
      # Relationships and links
      t.bigint :related_content_ids, array: true, default: []
      t.text :external_links, array: true, default: []
      
      # Standard Rails timestamps
      t.timestamps default: -> { 'CURRENT_TIMESTAMP' }
    end

    # Add unique constraint on source_type + source_id
    add_index :archived_contents, [:source_type, :source_id], unique: true, name: 'idx_archived_content_unique_source'
    
    # Add foreign key for parent_id (self-referential)
    add_foreign_key :archived_contents, :archived_contents, column: :parent_id, on_delete: :cascade
    
    # Performance indexes
    add_index :archived_contents, [:source_type, :timestamp], order: { timestamp: :desc }, name: 'idx_archived_content_source_timestamp'
    add_index :archived_contents, [:author, :timestamp], order: { timestamp: :desc }, name: 'idx_archived_content_author_timestamp'
    add_index :archived_contents, :processing_status, name: 'idx_archived_content_processing_status'
    add_index :archived_contents, :content_quality_score, name: 'idx_archived_content_quality_score'
    
    # Enable PostgreSQL extensions if not already enabled
    enable_extension 'pg_trgm' unless extension_enabled?('pg_trgm')
    
    # Full-text search index using PostgreSQL's built-in capabilities
    execute <<-SQL
      CREATE INDEX idx_archived_content_fts 
      ON archived_contents 
      USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body_text, '')))
    SQL
    
    # Trigram index for fuzzy text matching
    execute <<-SQL
      CREATE INDEX idx_archived_content_trigram 
      ON archived_contents 
      USING gin(title gin_trgm_ops, body_text gin_trgm_ops)
    SQL
    
    # Try to create vector index if pgvector extension is available
    begin
      enable_extension 'vector'
      execute <<-SQL
        CREATE INDEX idx_archived_content_vector 
        ON archived_contents 
        USING ivfflat (semantic_vector::vector(768))
      SQL
    rescue ActiveRecord::StatementInvalid
      # pgvector not available, skip vector index
      Rails.logger.warn "pgvector extension not available, skipping vector index"
    end
  end

  def down
    drop_table :archived_contents
  end
end