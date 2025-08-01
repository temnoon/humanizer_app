# Analysis results for selected messages from a conversation
class MessageAnalysis < ApplicationRecord
  self.primary_key = :id
  
  belongs_to :conversation
  
  validates :summary_type, presence: true, inclusion: { 
    in: %w[comprehensive key_points topics flow technical] 
  }
  validates :selected_message_ids, presence: true
  validates :summary_data, presence: true
  
  scope :recent, -> { order(created_at: :desc) }
  scope :by_type, ->(type) { where(summary_type: type) }
  scope :for_conversation, ->(conversation_id) { where(conversation_id: conversation_id) }
  
  before_validation :generate_id, if: :new_record?
  before_save :serialize_data
  after_initialize :deserialize_data
  
  # Virtual attributes for easier access to JSON data
  attr_accessor :selected_message_id_array, :summary_hash, :metadata_hash
  
  def selected_messages
    return [] unless conversation && selected_message_id_array
    conversation.messages.where(id: selected_message_id_array).ordered
  end
  
  def summary
    summary_hash || {}
  end
  
  def metadata
    metadata_hash || {}
  end
  
  def title
    "#{summary_type.humanize} Analysis - #{message_count} messages"
  end
  
  def short_summary
    summary.dig(:content_preview)&.first&.dig(:content)&.first(100) || 
    "Analysis of #{message_count} messages from #{conversation.title}"
  end
  
  private
  
  def generate_id
    self.id ||= SecureRandom.uuid
  end
  
  def serialize_data
    self.selected_message_ids = selected_message_id_array.to_json if selected_message_id_array
    self.summary_data = summary_hash.to_json if summary_hash
    self.analysis_metadata = metadata_hash.to_json if metadata_hash
  end
  
  def deserialize_data
    self.selected_message_id_array = JSON.parse(selected_message_ids) if selected_message_ids.present?
    self.summary_hash = JSON.parse(summary_data) if summary_data.present?
    self.metadata_hash = JSON.parse(analysis_metadata) if analysis_metadata.present?
  rescue JSON::ParserError
    # Handle case where data is not valid JSON
    self.selected_message_id_array = []
    self.summary_hash = {}
    self.metadata_hash = {}
  end
end