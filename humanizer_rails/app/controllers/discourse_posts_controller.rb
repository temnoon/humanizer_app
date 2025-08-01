class DiscoursePostsController < ApplicationController
  before_action :set_discourse_post, only: [:show, :update, :destroy, :publish, :sync, :preview]
  
  def index
    @discourse_posts = DiscoursePost.all
    
    # Apply filters
    @discourse_posts = @discourse_posts.where(status: params[:status]) if params[:status].present?
    @discourse_posts = @discourse_posts.by_category(params[:category]) if params[:category].present?
    @discourse_posts = @discourse_posts.where(conversation_id: params[:conversation_id]) if params[:conversation_id].present?
    @discourse_posts = @discourse_posts.where(writebook_id: params[:writebook_id]) if params[:writebook_id].present?
    
    # Search
    if params[:search].present?
      search_term = "%#{params[:search]}%"
      @discourse_posts = @discourse_posts.where(
        "title ILIKE ? OR content ILIKE ?", 
        search_term, search_term
      )
    end
    
    # Pagination
    page = params[:page]&.to_i || 1
    limit = params[:per_page]&.to_i || 20
    limit = [limit, 100].min
    
    offset = (page - 1) * limit
    total = @discourse_posts.count
    @discourse_posts = @discourse_posts.limit(limit).offset(offset).recent
    
    @pagination = {
      page: page,
      limit: limit,
      total: total,
      pages: (total / limit.to_f).ceil
    }
    
    respond_to do |format|
      format.html # Render discourse_posts/index.html.erb
      format.json {
        render_success({
          discourse_posts: @discourse_posts.as_json(
            include: {
              conversation: { only: [:id, :title] },
              writebook: { only: [:id, :title] },
              writebook_section: { only: [:id, :title] }
            },
            methods: [:performance_metrics]
          ),
          pagination: @pagination
        })
      }
    end
  end
  
  def show
    respond_to do |format|
      format.html # Render discourse_posts/show.html.erb
      format.json {
        render_success(@discourse_post.as_json(
          include: {
            conversation: { only: [:id, :title] },
            writebook: { only: [:id, :title] },
            writebook_section: { only: [:id, :title] }
          },
          methods: [:performance_metrics, :formatted_content]
        ))
      }
    end
  end
  
  def create
    @discourse_post = DiscoursePost.new(discourse_post_params)
    
    if @discourse_post.save
      render_success(@discourse_post, 'Discourse post created successfully')
    else
      render_error(@discourse_post.errors.full_messages.join(', '))
    end
  end
  
  def update
    if @discourse_post.update(discourse_post_params)
      render_success(@discourse_post, 'Discourse post updated successfully')
    else
      render_error(@discourse_post.errors.full_messages.join(', '))
    end
  end
  
  def destroy
    @discourse_post.destroy
    render_success({}, 'Discourse post deleted successfully')
  end
  
  # POST /discourse_posts/:id/publish
  def publish
    if @discourse_post.publish_to_discourse!
      render_success(@discourse_post, 'Successfully published to Discourse')
    else
      render_error(@discourse_post.error_message || 'Failed to publish to Discourse')
    end
  end
  
  # POST /discourse_posts/:id/sync
  def sync
    if @discourse_post.sync_from_discourse!
      render_success(@discourse_post, 'Successfully synced from Discourse')
    else
      render_error('Failed to sync from Discourse')
    end
  end
  
  # GET /discourse_posts/:id/preview
  def preview
    render json: {
      formatted_content: @discourse_post.formatted_content,
      title: @discourse_post.title,
      category: @discourse_post.discourse_category,
      tags: @discourse_post.discourse_tags
    }
  end
  
  # POST /discourse_posts/from_conversation
  def create_from_conversation
    conversation = Conversation.find(params[:conversation_id])
    
    options = {
      title: params[:title] || conversation.title,
      content: params[:content] || conversation.to_discourse_content,
      category: params[:category],
      tags: params[:tags] || [],
      allegory_attributes: params[:allegory_attributes] || {}
    }
    
    begin
      @discourse_post = DiscoursePost.create_from_conversation(conversation, options)
      
      # Auto-publish if requested
      if params[:auto_publish] == 'true'
        @discourse_post.publish_to_discourse!
      end
      
      render_success(@discourse_post, 'Successfully created Discourse post from conversation')
    rescue => e
      Rails.logger.error "Failed to create Discourse post from conversation: #{e.message}"
      render_error("Failed to create post: #{e.message}")
    end
  rescue ActiveRecord::RecordNotFound
    render_not_found('Conversation not found')
  end
  
  # POST /discourse_posts/from_writebook
  def create_from_writebook
    writebook = Writebook.find(params[:writebook_id])
    
    options = {
      title: params[:title] || writebook.title,
      content: params[:content] || writebook.to_discourse_content,
      category: params[:category],
      tags: params[:tags] || [],
      allegory_attributes: params[:allegory_attributes] || {}
    }
    
    begin
      @discourse_post = DiscoursePost.create_from_writebook(writebook, options)
      
      # Auto-publish if requested
      if params[:auto_publish] == 'true'
        @discourse_post.publish_to_discourse!
      end
      
      render_success(@discourse_post, 'Successfully created Discourse post from writebook')
    rescue => e
      Rails.logger.error "Failed to create Discourse post from writebook: #{e.message}"
      render_error("Failed to create post: #{e.message}")
    end
  rescue ActiveRecord::RecordNotFound
    render_not_found('Writebook not found')
  end
  
  # GET /discourse_posts/categories
  def categories
    begin
      discourse_service = DiscourseApiService.new
      categories = discourse_service.get_categories
      render_success(categories)
    rescue DiscourseApiService::DiscourseApiError => e
      render_error("Failed to fetch categories: #{e.message}")
    end
  end
  
  # GET /discourse_posts/connection_test
  def connection_test
    begin
      discourse_service = DiscourseApiService.new
      result = discourse_service.test_connection
      render_success(result)
    rescue => e
      render_error("Connection test failed: #{e.message}")
    end
  end
  
  # POST /discourse_posts/sync_all
  def sync_all
    begin
      DiscoursePost.sync_all_from_discourse
      render_success({}, 'Successfully synced all posts from Discourse')
    rescue => e
      Rails.logger.error "Failed to sync all posts: #{e.message}"
      render_error("Sync failed: #{e.message}")
    end
  end
  
  # GET /discourse_posts/analytics
  def analytics
    analytics_data = {
      total_posts: DiscoursePost.count,
      published_posts: DiscoursePost.published.count,
      draft_posts: DiscoursePost.drafts.count,
      total_views: DiscoursePost.published.sum(:view_count),
      total_replies: DiscoursePost.published.sum(:reply_count),
      total_likes: DiscoursePost.published.sum(:like_count),
      avg_engagement: DiscoursePost.published.average('reply_count + like_count + (view_count * 0.1)'),
      top_performers: DiscoursePost.published
                                  .joins("LEFT JOIN conversations ON discourse_posts.conversation_id = conversations.id")
                                  .joins("LEFT JOIN writebooks ON discourse_posts.writebook_id = writebooks.id")
                                  .select("discourse_posts.*, conversations.title as conversation_title, writebooks.title as writebook_title")
                                  .order('(reply_count + like_count + (view_count * 0.1)) DESC')
                                  .limit(10)
                                  .as_json(methods: [:performance_metrics])
    }
    
    render_success(analytics_data)
  end
  
  private
  
  def set_discourse_post
    @discourse_post = DiscoursePost.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render_not_found('Discourse post not found')
  end
  
  def discourse_post_params
    params.require(:discourse_post).permit(
      :title, :content, :conversation_id, :writebook_id, :writebook_section_id,
      :discourse_category, :allegory_attributes,
      discourse_tags: []
    )
  end
end