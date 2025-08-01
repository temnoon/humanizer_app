class CreateDiscoursePostsV2 < ActiveRecord::Migration[7.2]
  def change
    create_table :discourse_posts, id: :string do |t|
      t.string :title, null: false
      t.text :content, null: false
      t.string :status, default: 'draft'
      
      # Source relationships
      t.references :conversation, type: :string, foreign_key: true, null: true
      t.references :writebook, type: :bigint, foreign_key: true, null: true
      t.references :writebook_section, type: :bigint, foreign_key: true, null: true
      
      # Discourse integration
      t.integer :discourse_topic_id, null: true
      t.integer :discourse_post_id, null: true
      t.string :discourse_category
      t.text :discourse_tags, array: true, default: []
      t.string :discourse_url
      
      # Publishing metadata
      t.datetime :published_at
      t.datetime :last_sync_at
      t.text :error_message
      
      # Analytics
      t.integer :reply_count, default: 0
      t.integer :view_count, default: 0
      t.integer :like_count, default: 0
      
      # Allegory transformation attributes
      t.jsonb :allegory_attributes, default: {}
      
      t.timestamps
    end
    
    # Indexes for performance (note: references already create indexes for foreign keys)
    add_index :discourse_posts, :status
    add_index :discourse_posts, :discourse_topic_id, unique: true
    add_index :discourse_posts, :discourse_post_id, unique: true
    add_index :discourse_posts, :discourse_category
    add_index :discourse_posts, :published_at
    add_index :discourse_posts, :allegory_attributes, using: :gin
  end
end