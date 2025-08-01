class EnhanceWritebooksAndSections < ActiveRecord::Migration[7.2]
  def change
    # Add conversation source references to writebook sections
    add_column :writebook_sections, :source_conversation_id, :string
    add_column :writebook_sections, :source_message_id, :string
    add_column :writebook_sections, :allegory_attributes, :jsonb, default: {}
    
    add_index :writebook_sections, :source_conversation_id
    add_index :writebook_sections, :source_message_id
    add_index :writebook_sections, :allegory_attributes, using: :gin

    # Add allegory engine fields to writebooks
    add_column :writebooks, :genre, :string
    add_column :writebooks, :target_audience, :string
    add_column :writebooks, :allegory_settings, :jsonb, default: {}
    
    add_index :writebooks, :genre
    add_index :writebooks, :target_audience
    add_index :writebooks, :allegory_settings, using: :gin

    # Add foreign key constraints to conversations
    add_foreign_key :writebook_sections, :conversations, column: :source_conversation_id, primary_key: :id, on_delete: :nullify
    add_foreign_key :writebook_sections, :messages, column: :source_message_id, primary_key: :id, on_delete: :nullify
  end
end
