class DiscourseWebhooksController < ApplicationController
  skip_before_action :verify_authenticity_token
  before_action :verify_webhook_signature
  
  # POST /discourse_webhooks/topic_created
  def topic_created
    topic_data = webhook_params
    
    # Find corresponding discourse post if it exists
    discourse_post = DiscoursePost.find_by(discourse_topic_id: topic_data['id'])
    
    if discourse_post
      # Update with actual Discourse data
      discourse_post.update!(
        discourse_url: "#{Rails.application.config.discourse_base_url}/t/#{topic_data['slug']}/#{topic_data['id']}",
        view_count: topic_data['views'] || 0,
        reply_count: topic_data['posts_count'] || 1 - 1, # Subtract the original post
        published_at: topic_data['created_at'] ? Time.parse(topic_data['created_at']) : nil,
        last_sync_at: Time.current
      )
      
      Rails.logger.info "Updated discourse post #{discourse_post.id} from webhook"
    else
      Rails.logger.info "Received topic_created webhook for unknown topic: #{topic_data['id']}"
    end
    
    render json: { status: 'received' }
  end
  
  # POST /discourse_webhooks/post_created
  def post_created
    post_data = webhook_params
    topic_id = post_data['topic_id']
    
    # Find corresponding discourse post
    discourse_post = DiscoursePost.find_by(discourse_topic_id: topic_id)
    
    if discourse_post
      # Update reply count (exclude the original post)
      current_posts = post_data['post_number'] || 1
      discourse_post.update!(
        reply_count: [current_posts - 1, 0].max,
        last_sync_at: Time.current
      )
      
      Rails.logger.info "Updated reply count for discourse post #{discourse_post.id}: #{discourse_post.reply_count}"
    end
    
    render json: { status: 'received' }
  end
  
  # POST /discourse_webhooks/post_edited
  def post_edited
    post_data = webhook_params
    
    # If this is the original post, we might want to sync content changes
    if post_data['post_number'] == 1
      topic_id = post_data['topic_id']
      discourse_post = DiscoursePost.find_by(discourse_topic_id: topic_id)
      
      if discourse_post
        discourse_post.update!(last_sync_at: Time.current)
        Rails.logger.info "Original post edited for discourse post #{discourse_post.id}"
      end
    end
    
    render json: { status: 'received' }
  end
  
  # POST /discourse_webhooks/topic_destroyed
  def topic_destroyed
    topic_data = webhook_params
    discourse_post = DiscoursePost.find_by(discourse_topic_id: topic_data['id'])
    
    if discourse_post
      # Mark as unpublished rather than deleting
      discourse_post.update!(
        status: 'failed',
        error_message: 'Topic was deleted on Discourse',
        last_sync_at: Time.current
      )
      
      Rails.logger.info "Marked discourse post #{discourse_post.id} as failed due to topic deletion"
    end
    
    render json: { status: 'received' }
  end
  
  # POST /discourse_webhooks/like_created
  def like_created
    like_data = webhook_params
    
    # Find the topic from the post
    if like_data['post_id']
      # We would need to make an API call to get the topic_id from post_id
      # For now, we'll just log it
      Rails.logger.info "Like created on post #{like_data['post_id']}"
    end
    
    render json: { status: 'received' }
  end
  
  # Generic webhook handler for testing
  def handle_webhook
    event_type = request.headers['X-Discourse-Event-Type'] || params[:event_type]
    
    case event_type
    when 'topic_created'
      topic_created
    when 'post_created'
      post_created
    when 'post_edited'
      post_edited
    when 'topic_destroyed'
      topic_destroyed
    when 'like_created'
      like_created
    else
      Rails.logger.info "Received unknown webhook event: #{event_type}"
      render json: { status: 'unknown_event', event_type: event_type }
    end
  end
  
  private
  
  def webhook_params
    params.except(:controller, :action).permit!.to_h
  end
  
  def verify_webhook_signature
    # Verify webhook signature if configured
    webhook_secret = Rails.application.config.discourse_webhook_secret || ENV['DISCOURSE_WEBHOOK_SECRET']
    
    return true unless webhook_secret.present?
    
    signature = request.headers['X-Discourse-Event-Signature']
    return render json: { error: 'Missing signature' }, status: :unauthorized unless signature
    
    # Calculate expected signature
    body = request.raw_post
    expected_signature = "sha256=#{OpenSSL::HMAC.hexdigest('SHA256', webhook_secret, body)}"
    
    unless ActiveSupport::SecurityUtils.secure_compare(signature, expected_signature)
      Rails.logger.warn "Invalid webhook signature from #{request.remote_ip}"
      return render json: { error: 'Invalid signature' }, status: :unauthorized
    end
    
    true
  rescue => e
    Rails.logger.error "Webhook signature verification failed: #{e.message}"
    render json: { error: 'Signature verification failed' }, status: :unauthorized
  end
end