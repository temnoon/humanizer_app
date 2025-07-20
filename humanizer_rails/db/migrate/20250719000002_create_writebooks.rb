class CreateWritebooks < ActiveRecord::Migration[7.0]
  def change
    create_table :writebooks do |t|
      t.string :title, null: false
      t.string :author
      t.string :version, null: false, default: '1.0'
      t.text :description
      t.datetime :published_at
      
      t.timestamps
    end

    add_index :writebooks, :title
    add_index :writebooks, :author
    add_index :writebooks, :version
    add_index :writebooks, [:title, :version], unique: true
    add_index :writebooks, :published_at
  end
end
