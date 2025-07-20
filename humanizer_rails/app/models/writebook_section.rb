class WritebookSection < ApplicationRecord
  belongs_to :writebook
  has_many :llm_tasks, dependent: :nullify

  validates :section_index, presence: true, uniqueness: { scope: :writebook_id }
  validates :title, presence: true

  scope :ordered, -> { order(:section_index) }
  scope :with_content, -> { where.not(content: [nil, '']) }

  # Callbacks
  before_validation :set_section_index, if: :new_record?

  def word_count
    content&.split&.length || 0
  end

  def has_linked_archive?
    linked_archive_id.present?
  end

  def has_projections?
    projection_notes.present?
  end

  # Method to update content from LLM task
  def update_from_llm_task!(llm_task)
    if llm_task.completed?
      update!(
        content: llm_task.output,
        updated_at: Time.current
      )
    end
  end

  # Generate content using LLM
  def generate_content!(prompt, model_name = 'claude-3-sonnet', temperature = 0.7)
    llm_task = LlmTask.create!(
      task_type: 'generation',
      model_name: model_name,
      prompt: prompt,
      temperature: temperature,
      result_status: 'pending'
    )
    
    # TODO: Trigger actual LLM processing here
    # This would call your Python API or implement Ruby LLM integration
    
    llm_task
  end

  # Method to move section up in order
  def move_up!
    return if section_index <= 1
    
    transaction do
      other_section = writebook.writebook_sections.find_by(section_index: section_index - 1)
      other_section&.update!(section_index: section_index)
      update!(section_index: section_index - 1)
    end
  end

  # Method to move section down in order
  def move_down!
    max_index = writebook.writebook_sections.maximum(:section_index)
    return if section_index >= max_index
    
    transaction do
      other_section = writebook.writebook_sections.find_by(section_index: section_index + 1)
      other_section&.update!(section_index: section_index)
      update!(section_index: section_index + 1)
    end
  end

  private

  def set_section_index
    max_index = writebook.writebook_sections.maximum(:section_index) || 0
    self.section_index = max_index + 1
  end
end
