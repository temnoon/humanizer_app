# Unified conversation model supporting multiple source types
class Conversation < ApplicationRecord
  self.primary_key = :id
  
  has_many :messages, dependent: :destroy
  has_many :writebook_sections, foreign_key: :source_conversation_id, dependent: :nullify
  has_many :discourse_posts, dependent: :destroy
  has_many :message_analyses, dependent: :destroy
  
  validates :title, presence: true
  validates :source_type, presence: true, inclusion: { in: %w[chatgpt discourse manual claude anthropic] }
  validates :id, presence: true, uniqueness: true
  
  scope :recent, -> { order(created_at: :desc) }
  scope :by_source, ->(source) { where(source_type: source) }
  scope :search_title, ->(query) { where("title ILIKE ?", "%#{query}%") }
  scope :with_messages, -> { joins(:messages).distinct }
  
  # Enhanced search that searches titles, summaries, and message content
  scope :search_content, ->(query) {
    return all if query.blank?
    
    # Search in titles and summaries
    title_matches = where("title ILIKE ? OR summary ILIKE ?", "%#{query}%", "%#{query}%")
    
    # Search in message content
    message_matches = joins(:messages).where("messages.content ILIKE ?", "%#{query}%").distinct
    
    # Combine results
    where(id: title_matches.pluck(:id) + message_matches.pluck(:id))
  }
  
  before_validation :generate_id, if: :new_record?
  before_save :update_message_count
  before_save :update_word_count
  
  # Import from ChatGPT conversation.json
  def self.import_from_chatgpt(conversation_data, media_files = [])
    conversation_id = extract_chatgpt_id(conversation_data)
    
    # Check for existing conversation
    existing = find_by(id: conversation_id)
    return existing if existing&.checksum_matches?(conversation_data)
    
    transaction do
      conversation = create_or_update_conversation(conversation_id, conversation_data)
      import_messages(conversation, conversation_data, media_files)
      conversation.reload
    end
  end
  
  # Convert conversation to book sections
  def to_book_sections(writebook, section_options = {})
    sections = []
    
    messages.includes(:message_media).order(:message_index).each_with_index do |message, index|
      section = writebook.writebook_sections.build(
        title: section_options[:title_prefix] ? "#{section_options[:title_prefix]} #{index + 1}" : "Section #{index + 1}",
        content: format_message_content(message),
        source_conversation_id: id,
        source_message_id: message.id,
        section_index: index + 1,
        allegory_attributes: section_options[:allegory_attributes] || {}
      )
      sections << section
    end
    
    sections
  end
  
  # Apply allegory transformation to entire conversation
  def apply_allegory_transformation(attributes = {})
    # Integration point for allegory engine
    # This would call the quantum-inspired narrative transformation
    # Based on the theoretical framework from the Narrative Theory Overview
    
    allegory_service = AllegoryTransformationService.new(
      namespace: attributes[:namespace] || 'lamish-galaxy',
      persona: attributes[:persona] || 'temnoon', 
      style: attributes[:style] || 'contemplative'
    )
    
    # Transform each message through the allegory engine
    transformed_messages = messages.map do |message|
      allegory_service.transform_content(
        content: message.content,
        role: message.role,
        context: conversation_context
      )
    end
    
    # Return new conversation with transformed content
    create_transformed_copy(transformed_messages, attributes)
  end
  
  def conversation_context
    {
      title: title,
      source_type: source_type,
      total_messages: message_count,
      creation_date: original_created_at,
      metadata: metadata
    }
  end
  
  def checksum
    # Create content-based checksum for duplicate detection
    content = messages.order(:message_index).pluck(:content, :role).to_s
    Digest::SHA256.hexdigest("#{title}:#{content}")[0..15]
  end
  
  def checksum_matches?(conversation_data)
    # Compare with incoming conversation data
    incoming_checksum = self.class.calculate_checksum(conversation_data)
    checksum == incoming_checksum
  end
  
  def self.calculate_checksum(conversation_data)
    title = conversation_data.dig('title') || 'Untitled'
    messages = conversation_data.dig('mapping')&.values&.select { |m| m['message'] } || []
    content = messages.map { |m| "#{m.dig('message', 'author', 'role')}:#{m.dig('message', 'content', 'parts')&.join}" }.join
    Digest::SHA256.hexdigest("#{title}:#{content}")[0..15]
  end
  
  private
  
  def generate_id
    self.id ||= SecureRandom.uuid
  end
  
  def update_message_count
    self.message_count = messages.size
  end
  
  def update_word_count
    self.word_count = messages.sum(&:word_count)
  end
  
  def format_message_content(message)
    content = "**#{message.role.capitalize}**: #{message.content}"
    
    if message.message_media.any?
      media_list = message.message_media.map do |media|
        "![#{media.filename}](#{media.file_path})" if media.media_type == 'image'
      end.compact
      content += "\n\n" + media_list.join("\n") if media_list.any?
    end
    
    content
  end
  
  def self.extract_chatgpt_id(conversation_data)
    original_id = conversation_data['conversation_id'] || conversation_data['id']
    checksum = calculate_checksum(conversation_data)
    "chatgpt_#{checksum}"
  end
  
  def self.create_or_update_conversation(conversation_id, conversation_data)
    conversation = find_or_initialize_by(id: conversation_id)
    
    conversation.assign_attributes(
      title: conversation_data['title'] || 'Untitled Conversation',
      source_type: 'chatgpt',
      original_id: conversation_data['conversation_id'],
      summary: extract_summary(conversation_data),
      metadata: {
        create_time: conversation_data['create_time'],
        update_time: conversation_data['update_time'],
        mapping_count: conversation_data['mapping']&.size || 0,
        original_data: conversation_data.except('mapping') # Store non-message metadata
      },
      original_created_at: conversation_data['create_time'] ? Time.at(conversation_data['create_time']) : nil,
      original_updated_at: conversation_data['update_time'] ? Time.at(conversation_data['update_time']) : nil
    )
    
    conversation.save!
    conversation
  end
  
  def self.import_messages(conversation, conversation_data, media_files = [])
    return unless conversation_data['mapping']
    
    # Clear existing messages for reimport
    conversation.messages.destroy_all
    
    message_nodes = conversation_data['mapping'].values
      .select { |node| node['message'] && node['message']['content'] }
      .sort_by { |node| node['message']['create_time'] || 0 }
    
    message_nodes.each_with_index do |node, index|
      message_data = node['message']
      content_parts = message_data.dig('content', 'parts') || []
      content = content_parts.is_a?(Array) ? content_parts.join("\n") : content_parts.to_s
      
      next if content.blank?
      
      message = conversation.messages.build(
        id: message_data['id'] || SecureRandom.uuid,
        role: message_data.dig('author', 'role') || 'unknown',
        content: content,
        parent_message_id: node['parent'],
        message_index: index,
        word_count: content.split.length,
        metadata: {
          create_time: message_data['create_time'],
          author_name: message_data.dig('author', 'name'),
          weight: message_data['weight'],
          end_turn: message_data['end_turn']
        },
        original_timestamp: message_data['create_time'] ? Time.at(message_data['create_time']) : nil
      )
      
      message.save!
      
      # Associate media files if any
      associate_media_files(message, media_files, message_data)
    end
  end
  
  def self.associate_media_files(message, media_files, message_data)
    # Associate media files based on message content or metadata
    # This would match files to messages based on content analysis
    # Implementation depends on how media files are structured in the import
  end
  
  def self.extract_summary(conversation_data)
    # Extract or generate a summary from the conversation
    title = conversation_data['title']
    message_count = conversation_data['mapping']&.size || 0
    "Conversation: #{title} (#{message_count} messages)"
  end
  
  def create_transformed_copy(transformed_messages, attributes)
    # Create a new conversation with transformed content
    # This would be used for allegory transformations
    new_conversation = self.class.new(
      title: "#{title} (#{attributes[:style]} transformation)",
      source_type: 'transformed',
      original_id: id,
      metadata: metadata.merge(
        transformation: attributes,
        original_conversation_id: id,
        transformed_at: Time.current
      )
    )
    
    # Add transformed messages...
    # Implementation continues based on allegory engine results
    
    new_conversation
  end
  
  # Discourse integration methods
  def to_discourse_content
    # Format conversation content for Discourse posting
    content_parts = []
    
    # Add conversation summary
    if summary.present?
      content_parts << "## Summary\n#{summary}\n"
    end
    
    # Add key messages (first user message and assistant responses)
    key_messages = messages.where(role: ['user', 'assistant']).limit(10)
    
    if key_messages.any?
      content_parts << "## Key Exchange\n"
      
      key_messages.each_with_index do |message, index|
        role_emoji = message.role == 'user' ? '👤' : '🤖'
        content_parts << "### #{role_emoji} #{message.role.humanize}\n"
        
        # Truncate very long messages
        content = message.content.length > 500 ? 
          "#{message.content[0..500]}..." : message.content
          
        content_parts << "#{content}\n"
      end
    end
    
    # Add metadata
    content_parts << "\n---\n"
    content_parts << "*Generated from conversation with #{message_count} messages*"
    content_parts << "*Source: #{source_type.humanize}*" if source_type.present?
    
    content_parts.join("\n")
  end
  
  def can_publish_to_discourse?
    messages.any? && title.present?
  end
end