class WritebookSection < ApplicationRecord
  belongs_to :writebook
  belongs_to :source_conversation, class_name: 'Conversation', optional: true
  belongs_to :source_message, class_name: 'Message', optional: true
  has_many :llm_tasks, dependent: :nullify

  validates :section_index, presence: true, uniqueness: { scope: :writebook_id }
  validates :title, presence: true

  scope :ordered, -> { order(:section_index) }
  scope :with_content, -> { where.not(content: [nil, '']) }
  scope :from_conversations, -> { where.not(source_conversation_id: nil) }
  scope :from_messages, -> { where.not(source_message_id: nil) }
  scope :manual, -> { where(source_conversation_id: nil, source_message_id: nil) }

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

  # Check if section is derived from a conversation
  def from_conversation?
    source_conversation_id.present?
  end

  # Check if section is derived from a specific message
  def from_message?
    source_message_id.present?
  end

  # Get the source content (conversation or message)
  def source_content
    return source_message.content if source_message
    return source_conversation.title if source_conversation
    nil
  end

  # Apply allegory transformation to this section
  def apply_allegory_transformation(attributes = {})
    if source_message
      # Use message's transformation method
      transformed_message = source_message.apply_allegory_transformation(attributes)
      transformed_content = transformed_message.content
    else
      # Direct content transformation
      allegory_service = AllegoryTransformationService.new(
        namespace: attributes[:namespace] || 'lamish-galaxy',
        persona: attributes[:persona] || 'temnoon',
        style: attributes[:style] || 'contemplative'
      )
      
      transformed_content = allegory_service.transform_content(
        content: content,
        role: 'section',
        context: section_context
      )
    end

    # Create new section with transformed content
    dup.tap do |new_section|
      new_section.content = transformed_content
      new_section.allegory_attributes = allegory_attributes.merge(
        transformation: attributes,
        transformed_at: Time.current,
        original_section_id: id
      )
    end
  end

  # Get context for allegory transformation
  def section_context
    {
      writebook_title: writebook.title,
      section_title: title,
      section_index: section_index,
      genre: writebook.genre,
      target_audience: writebook.target_audience,
      has_source: from_conversation? || from_message?,
      source_type: source_conversation&.source_type
    }
  end

  # Sync content with source if available
  def sync_with_source!
    return unless from_message? && source_message

    update!(
      content: source_message.format_for_book,
      updated_at: Time.current
    )
  end

  # Check if content has diverged from source
  def diverged_from_source?
    return false unless from_message? && source_message
    
    expected_content = source_message.format_for_book
    content != expected_content
  end

  private

  def set_section_index
    max_index = writebook.writebook_sections.maximum(:section_index) || 0
    self.section_index = max_index + 1
  end
end
