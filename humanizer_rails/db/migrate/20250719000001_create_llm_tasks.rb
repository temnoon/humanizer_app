class CreateLlmTasks < ActiveRecord::Migration[7.0]
  def change
    create_table :llm_tasks do |t|
      t.string :task_type, null: false
      t.string :model_name, null: false
      t.float :temperature, default: 0.7
      t.text :prompt
      t.text :input
      t.text :output
      t.string :result_status, null: false, default: 'pending'
      t.jsonb :metadata, default: {}
      
      t.timestamps
    end

    add_index :llm_tasks, :task_type
    add_index :llm_tasks, :model_name
    add_index :llm_tasks, :result_status
    add_index :llm_tasks, :created_at
    add_index :llm_tasks, :metadata, using: :gin
  end
end
