# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.2].define(version: 2025_07_27_143000) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "archived_contents", force: :cascade do |t|
    t.string "source_type"
    t.string "source_id"
    t.bigint "parent_id"
    t.string "content_type"
    t.string "title"
    t.string "author"
    t.text "body_text"
    t.datetime "timestamp", precision: nil
    t.json "source_metadata"
    t.integer "word_count"
    t.text "search_terms"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["content_type"], name: "index_archived_contents_on_content_type"
    t.index ["parent_id"], name: "index_archived_contents_on_parent_id"
    t.index ["source_type", "source_id"], name: "index_archived_contents_on_source_type_and_source_id", unique: true
    t.index ["source_type"], name: "index_archived_contents_on_source_type"
  end

  create_table "conversations", id: :string, force: :cascade do |t|
    t.string "title", null: false
    t.string "source_type", null: false
    t.string "original_id"
    t.text "summary"
    t.jsonb "metadata", default: {}
    t.integer "message_count", default: 0
    t.integer "word_count", default: 0
    t.datetime "original_created_at"
    t.datetime "original_updated_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["metadata"], name: "index_conversations_on_metadata", using: :gin
    t.index ["original_created_at"], name: "index_conversations_on_original_created_at"
    t.index ["original_id"], name: "index_conversations_on_original_id"
    t.index ["source_type"], name: "index_conversations_on_source_type"
    t.index ["title", "source_type"], name: "index_conversations_on_title_and_source_type"
  end

  create_table "custom_gpts", force: :cascade do |t|
    t.string "gizmo_id", null: false
    t.string "name", null: false
    t.text "description"
    t.string "creator"
    t.string "category"
    t.text "capabilities"
    t.datetime "created_at_gpt"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["category"], name: "index_custom_gpts_on_category"
    t.index ["gizmo_id"], name: "index_custom_gpts_on_gizmo_id", unique: true
    t.index ["name"], name: "index_custom_gpts_on_name"
  end

  create_table "discourse_posts", id: :string, force: :cascade do |t|
    t.string "title", null: false
    t.text "content", null: false
    t.string "status", default: "draft"
    t.string "conversation_id"
    t.bigint "writebook_id"
    t.bigint "writebook_section_id"
    t.integer "discourse_topic_id"
    t.integer "discourse_post_id"
    t.string "discourse_category"
    t.text "discourse_tags", default: [], array: true
    t.string "discourse_url"
    t.datetime "published_at"
    t.datetime "last_sync_at"
    t.text "error_message"
    t.integer "reply_count", default: 0
    t.integer "view_count", default: 0
    t.integer "like_count", default: 0
    t.jsonb "allegory_attributes", default: {}
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["allegory_attributes"], name: "index_discourse_posts_on_allegory_attributes", using: :gin
    t.index ["conversation_id"], name: "index_discourse_posts_on_conversation_id"
    t.index ["discourse_category"], name: "index_discourse_posts_on_discourse_category"
    t.index ["discourse_post_id"], name: "index_discourse_posts_on_discourse_post_id", unique: true
    t.index ["discourse_topic_id"], name: "index_discourse_posts_on_discourse_topic_id", unique: true
    t.index ["published_at"], name: "index_discourse_posts_on_published_at"
    t.index ["status"], name: "index_discourse_posts_on_status"
    t.index ["writebook_id"], name: "index_discourse_posts_on_writebook_id"
    t.index ["writebook_section_id"], name: "index_discourse_posts_on_writebook_section_id"
  end

  create_table "llm_tasks", force: :cascade do |t|
    t.string "task_type", null: false
    t.string "model_name", null: false
    t.float "temperature", default: 0.7
    t.text "prompt"
    t.text "input"
    t.text "output"
    t.string "result_status", default: "pending", null: false
    t.jsonb "metadata", default: {}
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["created_at"], name: "index_llm_tasks_on_created_at"
    t.index ["metadata"], name: "index_llm_tasks_on_metadata", using: :gin
    t.index ["model_name"], name: "index_llm_tasks_on_model_name"
    t.index ["result_status"], name: "index_llm_tasks_on_result_status"
    t.index ["task_type"], name: "index_llm_tasks_on_task_type"
  end

  create_table "message_analyses", id: :string, force: :cascade do |t|
    t.string "conversation_id", null: false
    t.string "summary_type", default: "comprehensive", null: false
    t.string "focus_area"
    t.text "selected_message_ids"
    t.text "summary_data"
    t.text "analysis_metadata"
    t.string "created_by"
    t.integer "message_count", default: 0
    t.integer "word_count", default: 0
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["conversation_id"], name: "index_message_analyses_on_conversation_id"
    t.index ["created_at"], name: "index_message_analyses_on_created_at"
    t.index ["summary_type"], name: "index_message_analyses_on_summary_type"
  end

  create_table "message_media", force: :cascade do |t|
    t.string "message_id", null: false
    t.string "media_type", null: false
    t.string "filename"
    t.string "file_path"
    t.string "content_hash"
    t.integer "file_size"
    t.jsonb "metadata", default: {}
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["content_hash"], name: "index_message_media_on_content_hash"
    t.index ["media_type"], name: "index_message_media_on_media_type"
    t.index ["message_id"], name: "index_message_media_on_message_id"
  end

  create_table "messages", id: :string, force: :cascade do |t|
    t.string "conversation_id", null: false
    t.string "role", null: false
    t.text "content", null: false
    t.string "parent_message_id"
    t.integer "message_index"
    t.integer "word_count", default: 0
    t.jsonb "metadata", default: {}
    t.datetime "original_timestamp"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["conversation_id", "message_index"], name: "index_messages_on_conversation_id_and_message_index"
    t.index ["conversation_id"], name: "index_messages_on_conversation_id"
    t.index ["metadata"], name: "index_messages_on_metadata", using: :gin
    t.index ["original_timestamp"], name: "index_messages_on_original_timestamp"
    t.index ["parent_message_id"], name: "index_messages_on_parent_message_id"
    t.index ["role"], name: "index_messages_on_role"
  end

  create_table "writebook_sections", force: :cascade do |t|
    t.bigint "writebook_id", null: false
    t.integer "section_index", null: false
    t.string "title", null: false
    t.text "content"
    t.integer "linked_archive_id"
    t.text "projection_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "source_conversation_id"
    t.string "source_message_id"
    t.jsonb "allegory_attributes", default: {}
    t.index ["allegory_attributes"], name: "index_writebook_sections_on_allegory_attributes", using: :gin
    t.index ["linked_archive_id"], name: "index_writebook_sections_on_linked_archive_id"
    t.index ["source_conversation_id"], name: "index_writebook_sections_on_source_conversation_id"
    t.index ["source_message_id"], name: "index_writebook_sections_on_source_message_id"
    t.index ["writebook_id", "section_index"], name: "index_writebook_sections_on_writebook_id_and_section_index", unique: true
    t.index ["writebook_id"], name: "index_writebook_sections_on_writebook_id"
  end

  create_table "writebooks", force: :cascade do |t|
    t.string "title", null: false
    t.string "author"
    t.string "version", default: "1.0", null: false
    t.text "description"
    t.datetime "published_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "genre"
    t.string "target_audience"
    t.jsonb "allegory_settings", default: {}
    t.index ["allegory_settings"], name: "index_writebooks_on_allegory_settings", using: :gin
    t.index ["author"], name: "index_writebooks_on_author"
    t.index ["genre"], name: "index_writebooks_on_genre"
    t.index ["published_at"], name: "index_writebooks_on_published_at"
    t.index ["target_audience"], name: "index_writebooks_on_target_audience"
    t.index ["title", "version"], name: "index_writebooks_on_title_and_version", unique: true
    t.index ["title"], name: "index_writebooks_on_title"
    t.index ["version"], name: "index_writebooks_on_version"
  end

  add_foreign_key "discourse_posts", "conversations"
  add_foreign_key "discourse_posts", "writebook_sections"
  add_foreign_key "discourse_posts", "writebooks"
  add_foreign_key "message_analyses", "conversations"
  add_foreign_key "message_media", "messages", on_delete: :cascade
  add_foreign_key "messages", "conversations", on_delete: :cascade
  add_foreign_key "writebook_sections", "conversations", column: "source_conversation_id", on_delete: :nullify
  add_foreign_key "writebook_sections", "messages", column: "source_message_id", on_delete: :nullify
  add_foreign_key "writebook_sections", "writebooks"
end
