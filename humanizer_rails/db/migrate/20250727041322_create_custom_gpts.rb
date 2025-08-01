class CreateCustomGpts < ActiveRecord::Migration[7.2]
  def change
    create_table :custom_gpts do |t|
      t.string :gizmo_id, null: false
      t.string :name, null: false
      t.text :description
      t.string :creator
      t.string :category
      t.text :capabilities
      t.datetime :created_at_gpt

      t.timestamps
    end
    
    add_index :custom_gpts, :gizmo_id, unique: true
    add_index :custom_gpts, :name
    add_index :custom_gpts, :category
  end
end
