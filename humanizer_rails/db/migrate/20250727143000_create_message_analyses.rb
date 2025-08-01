class CreateMessageAnalyses < ActiveRecord::Migration[7.2]
  def change
    create_table :message_analyses, id: :string do |t|
      t.string :conversation_id, null: false
      t.string :summary_type, null: false, default: 'comprehensive'
      t.string :focus_area
      t.text :selected_message_ids # JSON array of message IDs
      t.text :summary_data # JSON of analysis results
      t.text :analysis_metadata # JSON of additional metadata
      t.string :created_by
      t.integer :message_count, default: 0
      t.integer :word_count, default: 0
      
      t.timestamps
    end
    
    add_foreign_key :message_analyses, :conversations, column: :conversation_id
    add_index :message_analyses, :conversation_id
    add_index :message_analyses, :summary_type
    add_index :message_analyses, :created_at
  end
end