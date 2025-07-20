class LlmTask < ApplicationRecord
  validates :task_type, presence: true
  validates :model_name, presence: true
  validates :result_status, presence: true

  # Enum for common task types
  enum task_type: {
    humanization: 'humanization',
    summarization: 'summarization', 
    analysis: 'analysis',
    generation: 'generation',
    classification: 'classification',
    custom: 'custom'
  }

  # Enum for result status
  enum result_status: {
    pending: 'pending',
    processing: 'processing',
    completed: 'completed',
    failed: 'failed',
    cancelled: 'cancelled'
  }

  # Scopes for common queries
  scope :recent, -> { order(created_at: :desc) }
  scope :by_model, ->(model) { where(model_name: model) }
  scope :successful, -> { where(result_status: 'completed') }
  scope :failed, -> { where(result_status: 'failed') }

  # Helper methods for metadata access
  def duration
    metadata&.dig('duration')
  end

  def token_count
    metadata&.dig('token_count')
  end

  def cost
    metadata&.dig('cost')
  end

  def set_metadata(key, value)
    self.metadata ||= {}
    self.metadata[key] = value
  end

  def get_metadata(key)
    metadata&.dig(key)
  end

  # Class method to create from Python API call
  def self.create_from_api_call(task_type:, model_name:, prompt:, input: nil, temperature: 0.7)
    create!(
      task_type: task_type,
      model_name: model_name,
      prompt: prompt,
      input: input,
      temperature: temperature,
      result_status: 'pending'
    )
  end

  # Method to mark as completed with output
  def complete_with_output!(output, metadata = {})
    update!(
      output: output,
      result_status: 'completed',
      metadata: self.metadata&.merge(metadata) || metadata
    )
  end

  # Method to mark as failed with error
  def fail_with_error!(error_message)
    update!(
      result_status: 'failed',
      metadata: (self.metadata || {}).merge(error: error_message)
    )
  end
end
