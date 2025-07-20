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

ActiveRecord::Schema[7.2].define(version: 2025_07_19_000003) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

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

  create_table "writebook_sections", force: :cascade do |t|
    t.bigint "writebook_id", null: false
    t.integer "section_index", null: false
    t.string "title", null: false
    t.text "content"
    t.integer "linked_archive_id"
    t.text "projection_notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["linked_archive_id"], name: "index_writebook_sections_on_linked_archive_id"
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
    t.index ["author"], name: "index_writebooks_on_author"
    t.index ["published_at"], name: "index_writebooks_on_published_at"
    t.index ["title", "version"], name: "index_writebooks_on_title_and_version", unique: true
    t.index ["title"], name: "index_writebooks_on_title"
    t.index ["version"], name: "index_writebooks_on_version"
  end

  add_foreign_key "writebook_sections", "writebooks"
end
