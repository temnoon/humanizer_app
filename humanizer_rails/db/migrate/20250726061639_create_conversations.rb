class CreateConversations < ActiveRecord::Migration[7.2]
  def change
    # Conversations table - unified storage for all conversation types
    create_table :conversations, id: :string do |t|
      t.string :title, null: false
      t.string :source_type, null: false # 'chatgpt', 'discourse', 'manual', etc.
      t.string :original_id # Original ID from source system
      t.text :summary
      t.jsonb :metadata, default: {}
      t.integer :message_count, default: 0
      t.integer :word_count, default: 0
      t.datetime :original_created_at
      t.datetime :original_updated_at
      t.timestamps
      
      t.index :source_type
      t.index :original_id
      t.index :original_created_at
      t.index [:title, :source_type]
      t.index :metadata, using: :gin
    end

    # Messages table - individual messages within conversations
    create_table :messages, id: :string do |t|
      t.string :conversation_id, null: false
      t.string :role, null: false # 'user', 'assistant', 'system', etc.
      t.text :content, null: false
      t.string :parent_message_id # For threaded conversations
      t.integer :message_index # Order within conversation
      t.integer :word_count, default: 0
      t.jsonb :metadata, default: {}
      t.datetime :original_timestamp
      t.timestamps
      
      t.index :conversation_id
      t.index :role
      t.index :parent_message_id
      t.index [:conversation_id, :message_index]
      t.index :original_timestamp
      t.index :metadata, using: :gin
    end

    # Media files associated with messages
    create_table :message_media do |t|
      t.string :message_id, null: false
      t.string :media_type, null: false # 'image', 'audio', 'video', 'document'
      t.string :filename
      t.string :file_path
      t.string :content_hash # SHA256 for deduplication
      t.integer :file_size
      t.jsonb :metadata, default: {}
      t.timestamps
      
      t.index :message_id
      t.index :media_type
      t.index :content_hash
    end

    # Foreign key constraints
    add_foreign_key :messages, :conversations, column: :conversation_id, primary_key: :id, on_delete: :cascade
    add_foreign_key :message_media, :messages, column: :message_id, primary_key: :id, on_delete: :cascade
  end
end
