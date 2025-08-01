# frozen_string_literal: true

# Unified Archive Content Model
# Provides Rails access to the PostgreSQL unified archive created by Python services
class ArchivedContent < ApplicationRecord
  # Enum definitions matching Python schema
  enum source_type: {
    node_conversation: 'node_conversation',
    twitter: 'twitter',
    email: 'email',
    slack: 'slack',
    discord: 'discord',
    telegram: 'telegram',
    file_system: 'file_system',
    web_content: 'web_content',
    social_media: 'social_media'
  }, _prefix: :from

  enum content_type: {
    message: 'message',
    conversation: 'conversation',
    thread: 'thread',
    document: 'document',
    media: 'media',
    annotation: 'annotation'
  }, _prefix: :is

  # Commented out - column doesn't exist in database
  # enum processing_status: {
  #   pending: 'pending',
  #   processing: 'processing',
  #   completed: 'completed',
  #   failed: 'failed',
  #   embedded: 'embedded',
  #   analyzed: 'analyzed'
  # }, _prefix: :status

  # Associations
  belongs_to :parent_conversation, class_name: 'ArchivedContent', foreign_key: 'parent_id', optional: true
  has_many :child_messages, class_name: 'ArchivedContent', foreign_key: 'parent_id', dependent: :destroy

  # Scopes for common queries
  scope :conversations, -> { where(content_type: 'conversation') }
  scope :messages, -> { where(content_type: 'message') }
  scope :by_author, ->(author) { where(author: author) }
  scope :by_source, ->(source_type) { where(source_type: source_type) }
  scope :recent, -> { order(timestamp: :desc) }
  # scope :processed, -> { where.not(processing_status: 'pending') }
  scope :high_quality, -> { where('content_quality_score > ?', 0.7) }
  
  # Date range scopes
  scope :from_date, ->(date) { where('timestamp >= ?', date) }
  scope :to_date, ->(date) { where('timestamp <= ?', date) }
  scope :date_range, ->(from_date, to_date) { where(timestamp: from_date..to_date) }

  # Validations
  validates :source_type, presence: true
  validates :source_id, presence: true
  validates :content_type, presence: true
  validates :source_id, uniqueness: { scope: :source_type, message: 'Source ID must be unique within source type' }

  # Callbacks
  before_save :update_word_count
  before_save :extract_search_terms

  # Full-text search using PostgreSQL (disabled - pg_search gem not available)
  # include PgSearch::Model
  # pg_search_scope :search_content,
  #   against: [:title, :body_text],
  #   using: {
  #     tsearch: {
  #       prefix: true,
  #       any_word: true,
  #       dictionary: "english"
  #     }
  #   }

  # Class methods
  class << self
    def import_from_archive_api(api_response)
      """Import content from Archive API response"""
      api_response['results'].map do |item|
        create_or_update_from_api(item)
      end
    end

    def create_or_update_from_api(api_item)
      """Create or update content from API data"""
      content = find_or_initialize_by(
        source_type: api_item['source_type'],
        source_id: api_item['source_id']
      )

      content.assign_attributes(
        content_type: api_item['content_type'],
        title: api_item['title'],
        body_text: api_item['body_text'],
        author: api_item['author'],
        participants: api_item['participants'],
        timestamp: api_item['timestamp']&.to_datetime,
        source_metadata: api_item['source_metadata'] || {},
        extracted_attributes: api_item['extracted_attributes'] || {},
        content_quality_score: api_item['quality_score'],
        processing_status: api_item['processing_status'] || 'pending'
      )

      content.save!
      content
    end

    def statistics
      """Get archive statistics"""
      {
        total_content: count,
        by_source_type: group(:source_type).count,
        by_content_type: group(:content_type).count,
        by_processing_status: group(:processing_status).count,
        conversations_count: conversations.count,
        messages_count: messages.count,
        processed_count: processed.count,
        average_quality_score: average(:content_quality_score)&.round(3)
      }
    end

    def top_authors(limit = 10)
      """Get most active authors"""
      group(:author)
        .where.not(author: [nil, ''])
        .order('count_id DESC')
        .limit(limit)
        .count(:id)
    end

    def content_by_date(days = 30)
      """Get content creation over time"""
      where('created_at >= ?', days.days.ago)
        .group_by_day(:created_at)
        .count
    end

    def search_unified(query, options = {})
      """Unified search across all content"""
      results = all

      # Text search
      if query.present?
        results = results.search_content(query)
      end

      # Apply filters
      results = results.where(source_type: options[:source_types]) if options[:source_types].present?
      results = results.where(content_type: options[:content_types]) if options[:content_types].present?
      results = results.where(author: options[:author]) if options[:author].present?
      results = results.from_date(options[:date_from]) if options[:date_from].present?
      results = results.to_date(options[:date_to]) if options[:date_to].present?

      # Pagination
      results = results.limit(options[:limit] || 50)
      results = results.offset(options[:offset] || 0)

      # Ordering
      results.recent
    end
  end

  # Instance methods
  def conversation_thread
    """Get complete conversation thread"""
    if is_conversation?
      child_messages.order(:timestamp)
    elsif parent_conversation
      parent_conversation.child_messages.order(:timestamp)
    else
      ArchivedContent.none
    end
  end

  def conversation_participants
    """Get all participants in this conversation"""
    if is_conversation?
      participants || []
    elsif parent_conversation
      parent_conversation.participants || []
    else
      [author].compact
    end
  end

  def related_content(limit = 5)
    """Find related content based on various factors"""
    related = ArchivedContent.where.not(id: id)

    # Same conversation
    if parent_id.present?
      related = related.where(parent_id: parent_id)
    end

    # Same author
    if author.present?
      related = related.or(ArchivedContent.where(author: author))
    end

    # Similar timeframe (within 1 hour)
    if timestamp.present?
      time_range = (timestamp - 1.hour)..(timestamp + 1.hour)
      related = related.or(ArchivedContent.where(timestamp: time_range))
    end

    related.recent.limit(limit)
  end

  def summary
    """Generate content summary"""
    {
      id: id,
      source: "#{source_type}/#{source_id}",
      type: content_type,
      title: title,
      author: author,
      timestamp: timestamp&.iso8601,
      word_count: word_count,
      quality_score: content_quality_score,
      status: processing_status,
      preview: body_text&.truncate(200)
    }
  end

  def export_data
    """Export complete data for this content"""
    {
      id: id,
      source_type: source_type,
      source_id: source_id,
      parent_id: parent_id,
      content_type: content_type,
      title: title,
      body_text: body_text,
      raw_content: raw_content,
      author: author,
      participants: participants,
      timestamp: timestamp&.iso8601,
      source_metadata: source_metadata,
      extracted_attributes: extracted_attributes,
      content_quality_score: content_quality_score,
      processing_status: processing_status,
      search_terms: search_terms,
      language_detected: language_detected,
      word_count: word_count,
      created_at: created_at&.iso8601,
      updated_at: updated_at&.iso8601
    }
  end

  def to_writebook_section
    """Convert to WriteBook section format"""
    {
      title: title || "#{source_type.humanize} Content",
      content: body_text,
      metadata: {
        source_type: source_type,
        source_id: source_id,
        author: author,
        timestamp: timestamp&.iso8601,
        quality_score: content_quality_score,
        word_count: word_count
      },
      tags: search_terms || []
    }
  end

  def enhance_with_lpe!
    """Trigger LPE enhancement for this content"""
    # This would make API call to LPE service
    # For now, mark as processing
    update!(processing_status: 'processing')
    
    # Background job would handle actual LPE processing
    ArchiveEnhancementJob.perform_later(id)
  end

  def quality_assessment
    """Get quality assessment details"""
    {
      score: content_quality_score,
      status: processing_status,
      attributes: extracted_attributes,
      word_count: word_count,
      has_author: author.present?,
      has_timestamp: timestamp.present?,
      content_length: body_text&.length || 0
    }
  end

  private

  def update_word_count
    """Update word count when content changes"""
    if body_text.present?
      self.word_count = body_text.split.size
    end
  end

  def extract_search_terms
    """Extract search terms from content"""
    return unless body_text.present?

    # Simple keyword extraction
    # In production, this could use more sophisticated NLP
    words = body_text.downcase.split(/\W+/)
    significant_words = words.select { |word| word.length > 3 }
    self.search_terms = significant_words.uniq.first(20)
  end
end