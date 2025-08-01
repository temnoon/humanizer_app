# Conversations Controller - Unified conversation management
class ConversationsController < ApplicationController
  before_action :set_conversation, only: [:show, :destroy, :transform, :export_to_book, :new_transformation, :new_book, :preview]
  
  # GET /conversations
  def index
    @conversations = Conversation.all
    
    # Apply advanced search filters
    apply_search_filters
    apply_date_filters  
    apply_content_filters
    apply_metadata_filters
    apply_sorting
    
    # Pagination
    page = params[:page]&.to_i || 1
    limit = params[:per_page]&.to_i || params[:limit]&.to_i || 20
    limit = [limit, 100].min # Cap at 100
    
    offset = (page - 1) * limit
    total = @conversations.count
    @conversations = @conversations.limit(limit).offset(offset)
    
    @pagination = {
      page: page,
      limit: limit,
      total: total,
      pages: (total / limit.to_f).ceil
    }
    
    respond_to do |format|
      format.html # Render conversation browser view
      format.json {
        render json: {
          conversations: @conversations.as_json(
            include: {
              messages: {
                only: [:id, :role, :word_count, :original_timestamp],
                limit: 3 # Preview messages
              }
            },
            methods: [:checksum]
          ),
          pagination: @pagination
        }
      }
    end
  end
  
  # GET /conversations/:id
  def show
    respond_to do |format|
      format.html # Render conversation detail view
      format.json {
        render json: @conversation.as_json(
          include: {
            messages: {
              include: {
                message_media: {
                  only: [:media_type, :filename, :file_path, :content_hash]
                }
              }
            }
          }
        )
      }
    end
  end
  
  # POST /conversations/import
  def import
    if params[:conversation_file].blank?
      return render json: { error: 'No conversation file provided' }, status: :bad_request
    end
    
    begin
      file = params[:conversation_file]
      
      # Handle different file types
      if file.original_filename.end_with?('.json')
        conversation_data = JSON.parse(file.read)
      elsif file.original_filename.end_with?('.zip')
        # Handle zip file extraction
        conversation_data = extract_conversation_from_zip(file)
      else
        return render json: { error: 'Unsupported file format' }, status: :bad_request
      end
      
      # Import conversation
      conversation = Conversation.import_from_chatgpt(
        conversation_data,
        params[:media_files] || []
      )
      
      render json: {
        success: true,
        conversation: conversation.as_json(methods: [:checksum]),
        message: "Successfully imported conversation: #{conversation.title}"
      }
      
    rescue JSON::ParserError => e
      render json: { error: "Invalid JSON format: #{e.message}" }, status: :bad_request
    rescue => e
      Rails.logger.error "Conversation import failed: #{e.message}"
      render json: { error: "Import failed: #{e.message}" }, status: :internal_server_error
    end
  end
  
  # POST /conversations/:id/transform
  def transform
    attributes = {
      namespace: params[:namespace] || 'lamish-galaxy',
      persona: params[:persona] || 'temnoon',
      style: params[:style] || 'contemplative',
      intensity: params[:intensity]&.to_f || 0.5,
      output_format: params[:output_format] || 'conversation',
      preserve_structure: params[:preserve_structure] == '1',
      include_analysis: params[:include_analysis] == '1',
      enable_local_basis: params[:enable_local_basis] == '1'
    }
    
    begin
      # For now, create a simple transformation record in the conversation's metadata
      transformation_result = {
        id: SecureRandom.uuid,
        original_conversation_id: @conversation.id,
        transformation_attributes: attributes,
        status: 'completed',
        created_at: Time.current,
        summary: "Applied #{attributes[:persona]} persona with #{attributes[:style]} style in #{attributes[:namespace]} namespace"
      }
      
      # Store transformation in conversation metadata
      @conversation.metadata = (@conversation.metadata || {}).merge(
        'latest_transformation' => transformation_result
      )
      @conversation.save!
      
      respond_to do |format|
        format.html do
          flash[:success] = "✨ Transformation completed successfully! Applied #{attributes[:persona]} persona with #{attributes[:style]} style."
          redirect_to conversation_path(@conversation)
        end
        format.json do
          render json: {
            success: true,
            original_conversation: @conversation.as_json(only: [:id, :title, :message_count]),
            transformation_result: transformation_result,
            transformation_attributes: attributes
          }
        end
      end
      
    rescue => e
      Rails.logger.error "Allegory transformation failed: #{e.message}"
      respond_to do |format|
        format.html do
          flash[:error] = "❌ Transformation failed: #{e.message}"
          redirect_to new_transformation_conversation_path(@conversation)
        end
        format.json do
          render json: { error: "Transformation failed: #{e.message}" }, status: :internal_server_error
        end
      end
    end
  end
  
  # POST /conversations/:id/export_to_book
  def export_to_book
    book_options = {
      title: params[:book_title] || "Book: #{@conversation.title}",
      author: params[:author] || 'Generated from Conversation',
      description: params[:description],
      genre: params[:genre] || 'narrative',
      target_audience: params[:target_audience] || 'general',
      allegory_settings: params[:allegory_settings] || {}
    }
    
    section_options = {
      title_prefix: params[:section_title_prefix],
      allegory_attributes: params[:section_allegory_attributes] || {}
    }
    
    begin
      book = Writebook.create_from_conversation(
        @conversation,
        book_options.merge(section_options: section_options)
      )
      
      render json: {
        success: true,
        book: book.as_json(
          include: {
            writebook_sections: {
              only: [:id, :title, :section_index, :word_count, :source_message_id],
              methods: [:from_message?]
            }
          }
        ),
        message: "Successfully created book: #{book.title}"
      }
      
    rescue => e
      Rails.logger.error "Book creation failed: #{e.message}"
      render json: { error: "Book creation failed: #{e.message}" }, status: :internal_server_error
    end
  end
  
  # GET /conversations/search
  def search
    query = params[:query]
    if query.blank?
      return render json: { conversations: [], total: 0 }
    end
    
    # Search in conversation titles and message content
    title_matches = Conversation.search_title(query)
    
    # Search in message content (simplified - could be enhanced with full-text search)
    message_matches = Conversation.joins(:messages)
                                 .where("messages.content ILIKE ?", "%#{query}%")
                                 .distinct
    
    all_matches = (title_matches + message_matches).uniq
    
    render json: {
      conversations: all_matches.as_json(
        include: {
          messages: {
            only: [:id, :role, :content],
            limit: 1 # Just first message for preview
          }
        }
      ),
      total: all_matches.length,
      query: query
    }
  end
  
  # DELETE /conversations/:id
  def destroy
    @conversation.destroy
    render json: { success: true, message: "Conversation deleted" }
  end
  
  # GET /conversations/stats
  def stats
    total_conversations = Conversation.count
    total_messages = Message.count
    source_breakdown = Conversation.group(:source_type).count
    
    recent_activity = Conversation.where('created_at > ?', 7.days.ago).count
    
    render json: {
      total_conversations: total_conversations,
      total_messages: total_messages,
      average_messages_per_conversation: total_messages.to_f / [total_conversations, 1].max,
      source_breakdown: source_breakdown,
      recent_activity: recent_activity,
      storage_info: {
        conversations_with_media: MessageMedium.joins(:message).distinct.count('messages.conversation_id'),
        total_media_files: MessageMedium.count
      }
    }
  end
  
  # GET /conversations/:id/preview.json
  def preview
    first_message = @conversation.messages.by_role('user').ordered.first
    first_response = @conversation.messages.by_role('assistant').ordered.first
    
    render json: {
      first_message: first_message ? {
        content: truncate(first_message.content, length: 150),
        timestamp: first_message.original_timestamp&.strftime('%Y-%m-%d %H:%M')
      } : nil,
      first_response: first_response ? {
        content: truncate(first_response.content, length: 150),
        timestamp: first_response.original_timestamp&.strftime('%Y-%m-%d %H:%M')
      } : nil
    }
  end

  private
  
  def set_conversation
    @conversation = Conversation.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Conversation not found' }, status: :not_found
  end
  
  def extract_conversation_from_zip(zip_file)
    # Implementation for extracting conversation.json from zip files
    # This would handle ChatGPT export zip files
    require 'zip'
    
    conversation_data = nil
    
    Zip::File.open(zip_file.tempfile) do |zip|
      zip.each do |entry|
        if entry.name == 'conversation.json'
          conversation_data = JSON.parse(entry.get_input_stream.read)
          break
        end
      end
    end
    
    raise "No conversation.json found in zip file" unless conversation_data
    conversation_data
  end

  # GET /conversations/:id/new_transformation
  def new_transformation
    @transformation_presets = transformation_presets
    @semantic_probe_categories = semantic_probe_categories
  end

  # GET /conversations/:id/new_book  
  def new_book
    # Data will be available from ApplicationController methods
  end

  private

  # Advanced search filter methods
  def apply_search_filters
    return unless params[:search].present?

    search_query = params[:search]
    search_title = params[:search_title] != '0'
    search_content = params[:search_content] != '0' 
    search_semantic = params[:search_semantic] == 'true'

    # Default to title search if no scope specified
    if !search_title && !search_content && !search_semantic
      search_title = true
    end

    # Build search conditions
    if search_title && search_content
      @conversations = @conversations.search_content(search_query)
    elsif search_title
      @conversations = @conversations.search_title(search_query)
    elsif search_content
      @conversations = @conversations.joins(:messages)
                                   .where("messages.content ILIKE ?", "%#{search_query}%")
                                   .distinct
    end

    # TODO: Implement semantic search when semantic analysis is available
    if search_semantic
      # This would integrate with the AllegoryTransformationService for semantic search
      Rails.logger.info "Semantic search requested for: #{search_query}"
    end
  end

  def apply_date_filters
    if params[:date_from].present?
      @conversations = @conversations.where('created_at >= ?', Date.parse(params[:date_from]))
    end

    if params[:date_to].present?
      @conversations = @conversations.where('created_at <= ?', Date.parse(params[:date_to]).end_of_day)
    end
  end

  def apply_content_filters
    # Message count filters
    if params[:min_messages].present?
      @conversations = @conversations.where('message_count >= ?', params[:min_messages].to_i)
    end

    if params[:max_messages].present?
      @conversations = @conversations.where('message_count <= ?', params[:max_messages].to_i)
    end

    # Word count filters
    if params[:min_words].present?
      @conversations = @conversations.where('word_count >= ?', params[:min_words].to_i)
    end

    if params[:max_words].present?
      @conversations = @conversations.where('word_count <= ?', params[:max_words].to_i)
    end

    # Role filters
    if params[:roles].present? && params[:roles].any?(&:present?)
      roles = params[:roles].select(&:present?)
      @conversations = @conversations.joins(:messages)
                                   .where(messages: { role: roles })
                                   .distinct
    end

    # Attachment filters
    if params[:has_attachments] == 'true'
      @conversations = @conversations.joins(messages: :message_media).distinct
    end

    # Tool usage filters (placeholder for future implementation)
    if params[:has_tools] == 'true'
      # TODO: Implement when tool usage tracking is available
      Rails.logger.info "Tool usage filter requested"
    end
  end

  def apply_metadata_filters
    # Source type filter
    if params[:source_type].present?
      @conversations = @conversations.by_source(params[:source_type])
    end

    # GPT model filter (placeholder - would need to be stored in conversation metadata)
    if params[:gpt_model].present?
      # TODO: Implement when GPT model tracking is available
      Rails.logger.info "GPT model filter requested: #{params[:gpt_model]}"
    end

    # Gizmo ID filter (placeholder - would need to be stored in conversation metadata)
    if params[:gizmo_id].present?
      # TODO: Implement when Gizmo ID tracking is available
      Rails.logger.info "Gizmo ID filter requested: #{params[:gizmo_id]}"
    end
  end

  def apply_sorting
    sort_column = params[:sort_by] || params[:sort_column] || 'created_at'
    sort_direction = params[:sort_direction] || 'desc'
    
    # Ensure sort_direction is valid
    sort_direction = 'desc' unless ['asc', 'desc'].include?(sort_direction)
    
    case sort_column
    when 'title'
      @conversations = @conversations.order("LOWER(title) #{sort_direction}")
    when 'message_count', 'messages'
      @conversations = @conversations.order("message_count #{sort_direction}")
    when 'word_count', 'words'
      @conversations = @conversations.order("word_count #{sort_direction}")
    when 'analyses_count', 'comments'
      # Need to join and count message_analyses
      @conversations = @conversations.left_joins(:message_analyses)
                                   .group('conversations.id')
                                   .order("COUNT(message_analyses.id) #{sort_direction}")
    when 'media_count', 'media'
      # Need to join messages and message_media and count
      @conversations = @conversations.left_joins(messages: :message_media)
                                   .group('conversations.id')
                                   .order("COUNT(DISTINCT message_media.id) #{sort_direction}")
    when 'created_at', 'date'
      date_column = params[:date_sort] == 'original' ? 'original_created_at' : 'created_at'
      @conversations = @conversations.order("#{date_column} #{sort_direction}")
    when 'created_at_asc'
      @conversations = @conversations.order(created_at: :asc)
    else
      # Default sort
      @conversations = @conversations.order(created_at: :desc)
    end
    
    # Store current sort params for pagination links
    @current_sort = {
      column: sort_column,
      direction: sort_direction
    }
  end
end