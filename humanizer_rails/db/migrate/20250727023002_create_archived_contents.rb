class CreateArchivedContents < ActiveRecord::Migration[7.2]
  def change
    create_table :archived_contents do |t|
      t.string :source_type
      t.string :source_id
      t.bigint :parent_id
      t.string :content_type
      t.string :title
      t.string :author
      t.text :body_text
      t.timestamp :timestamp
      t.json :source_metadata
      t.integer :word_count
      t.text :search_terms

      t.timestamps
    end
    
    add_index :archived_contents, :source_type
    add_index :archived_contents, :content_type
    add_index :archived_contents, :parent_id
    add_index :archived_contents, [:source_type, :source_id], unique: true
  end
end
