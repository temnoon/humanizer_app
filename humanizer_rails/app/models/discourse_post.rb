# Discourse Post Model - Integration with Discourse platform
class DiscoursePost < ApplicationRecord
  belongs_to :conversation, optional: true
  belongs_to :writebook, optional: true
  belongs_to :writebook_section, optional: true
  
  validates :title, presence: true
  validates :content, presence: true
  validates :discourse_topic_id, uniqueness: { allow_nil: true }
  validates :discourse_post_id, uniqueness: { allow_nil: true }
  
  enum status: {
    draft: 'draft',
    publishing: 'publishing', 
    published: 'published',
    failed: 'failed',
    updated: 'updated'
  }
  
  scope :published, -> { where(status: 'published') }
  scope :drafts, -> { where(status: 'draft') }
  scope :recent, -> { order(created_at: :desc) }
  scope :by_category, ->(category) { where(discourse_category: category) }
  
  # Publishing workflow
  def publish_to_discourse!
    return false if published? && discourse_topic_id.present?
    
    begin
      update!(status: 'publishing')
      
      discourse_service = DiscourseApiService.new
      result = discourse_service.create_topic(
        title: title,
        raw: formatted_content,
        category: discourse_category,
        tags: discourse_tags
      )
      
      update!(
        discourse_topic_id: result['topic_id'],
        discourse_post_id: result['id'],
        discourse_url: result['topic_slug'] ? 
          "#{Rails.application.config.discourse_base_url}/t/#{result['topic_slug']}/#{result['topic_id']}" : nil,
        status: 'published',
        published_at: Time.current
      )
      
      true
    rescue => e
      Rails.logger.error "Failed to publish to Discourse: #{e.message}"
      update!(status: 'failed', error_message: e.message)
      false
    end
  end
  
  def update_discourse_post!
    return false unless published? && discourse_topic_id.present?
    
    begin
      update!(status: 'publishing')
      
      discourse_service = DiscourseApiService.new
      discourse_service.update_post(
        discourse_post_id,
        raw: formatted_content
      )
      
      update!(status: 'updated', updated_at: Time.current)
      true
    rescue => e
      Rails.logger.error "Failed to update Discourse post: #{e.message}"
      update!(status: 'failed', error_message: e.message)
      false
    end
  end
  
  def sync_from_discourse!
    return false unless discourse_topic_id.present?
    
    begin
      discourse_service = DiscourseApiService.new
      topic_data = discourse_service.get_topic(discourse_topic_id)
      
      # Update local data with Discourse data
      update!(
        reply_count: topic_data['posts_count'] - 1, # Subtract original post
        view_count: topic_data['views'],
        like_count: topic_data['like_count'] || 0,
        last_sync_at: Time.current
      )
      
      true
    rescue => e
      Rails.logger.error "Failed to sync from Discourse: #{e.message}"
      false
    end
  end
  
  # Content formatting for Discourse
  def formatted_content
    content_with_metadata = content.dup
    
    # Add source attribution
    if conversation_id.present?
      content_with_metadata += "\n\n---\n*Generated from conversation via Humanizer Lighthouse Allegory Engine*"
    elsif writebook_id.present?
      content_with_metadata += "\n\n---\n*Published from Writebook: #{writebook.title}*"
    end
    
    # Add allegory transformation note if applicable
    if allegory_attributes.present?
      namespace = allegory_attributes['namespace']
      persona = allegory_attributes['persona'] 
      style = allegory_attributes['style']
      
      content_with_metadata += "\n\n*Allegory Transformation: #{namespace}/#{persona}/#{style}*"
    end
    
    content_with_metadata
  end
  
  # Analytics and insights
  def engagement_score
    return 0 unless published?
    
    # Simple engagement formula - can be enhanced
    (reply_count * 3) + (like_count * 1) + (view_count * 0.1)
  end
  
  def performance_metrics
    {
      engagement_score: engagement_score,
      reply_count: reply_count || 0,
      view_count: view_count || 0,
      like_count: like_count || 0,
      days_published: published_at ? (Time.current - published_at) / 1.day : 0,
      daily_views: view_count && published_at ? 
        (view_count / [(Time.current - published_at) / 1.day, 1].max) : 0
    }
  end
  
  # Class methods for bulk operations
  def self.create_from_conversation(conversation, options = {})
    post = new(
      conversation: conversation,
      title: options[:title] || conversation.title,
      content: options[:content] || conversation.to_discourse_content,
      discourse_category: options[:category],
      discourse_tags: options[:tags] || [],
      allegory_attributes: options[:allegory_attributes] || {}
    )
    
    post.save!
    post
  end
  
  def self.create_from_writebook(writebook, options = {})
    post = new(
      writebook: writebook,
      title: options[:title] || writebook.title,
      content: options[:content] || writebook.to_discourse_content,
      discourse_category: options[:category],
      discourse_tags: options[:tags] || [],
      allegory_attributes: options[:allegory_attributes] || {}
    )
    
    post.save!
    post
  end
  
  def self.sync_all_from_discourse
    published.where.not(discourse_topic_id: nil).find_each do |post|
      post.sync_from_discourse!
    end
  end
end