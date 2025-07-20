class CreateWritebookSections < ActiveRecord::Migration[7.0]
  def change
    create_table :writebook_sections do |t|
      t.references :writebook, null: false, foreign_key: true
      t.integer :section_index, null: false
      t.string :title, null: false
      t.text :content
      t.integer :linked_archive_id
      t.text :projection_notes
      
      t.timestamps
    end

    add_index :writebook_sections, [:writebook_id, :section_index], unique: true
    add_index :writebook_sections, :linked_archive_id
  end
end
