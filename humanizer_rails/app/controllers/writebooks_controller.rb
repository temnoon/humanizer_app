class WritebooksController < ApplicationController
  before_action :set_writebook, only: [:show, :update, :destroy, :publish, :unpublish, :create_version, :transform, :export]

  def index
    @writebooks = Writebook.recent
    @writebooks = @writebooks.by_author(params[:author]) if params[:author].present?
    @writebooks = @writebooks.by_genre(params[:genre]) if params[:genre].present?
    @writebooks = @writebooks.by_audience(params[:target_audience]) if params[:target_audience].present?
    @writebooks = @writebooks.published if params[:published] == 'true'
    
    # For pagination
    page = params[:page]&.to_i || 1
    limit = params[:per_page]&.to_i || 20
    limit = [limit, 100].min
    
    offset = (page - 1) * limit
    total = @writebooks.count
    @writebooks = @writebooks.includes(:writebook_sections).limit(limit).offset(offset)
    
    @pagination = {
      page: page,
      limit: limit,
      total: total,
      pages: (total / limit.to_f).ceil
    }
    
    respond_to do |format|
      format.html # Render books/index.html.erb
      format.json {
        render_success(
          @writebooks.as_json(
            include: {
              writebook_sections: { 
                only: [:id, :title, :section_index, :word_count, :source_conversation_id, :source_message_id],
                methods: [:from_conversation?, :from_message?]
              }
            },
            methods: [:total_word_count, :sections_count]
          )
        )
      }
    end
  end

  def show
    respond_to do |format|
      format.html # Render writebooks/show.html.erb
      format.json {
        render_success(@writebook.as_json(include: :writebook_sections))
      }
    end
  end

  def create
    @writebook = Writebook.new(writebook_params)
    
    if @writebook.save
      render_success(@writebook, 'Writebook created successfully')
    else
      render_error(@writebook.errors.full_messages.join(', '))
    end
  end

  def update
    if @writebook.update(writebook_params)
      render_success(@writebook, 'Writebook updated successfully')
    else
      render_error(@writebook.errors.full_messages.join(', '))
    end
  end

  def destroy
    @writebook.destroy
    render_success({}, 'Writebook deleted successfully')
  end

  def publish
    @writebook.publish!
    render_success(@writebook, 'Writebook published successfully')
  end

  def unpublish
    @writebook.unpublish!
    render_success(@writebook, 'Writebook unpublished successfully')
  end

  def create_version
    new_writebook = @writebook.create_new_version!
    render_success(new_writebook, 'New version created successfully')
  end

  # Get all versions of a writebook
  def versions
    title = params[:title]
    versions = Writebook.where(title: title).order(:version)
    render_success(versions)
  end

  private

  def set_writebook
    @writebook = Writebook.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render_not_found('Writebook not found')
  end

  # POST /writebooks/:id/transform
  def transform
    attributes = {
      namespace: params[:namespace] || 'lamish-galaxy',
      persona: params[:persona] || 'temnoon',
      style: params[:style] || 'contemplative'
    }
    
    begin
      transformed_book = @writebook.apply_allegory_transformation(attributes)
      
      render_success({
        original_book: @writebook.as_json(only: [:id, :title, :sections_count, :total_word_count]),
        transformed_book: transformed_book.as_json(
          include: {
            writebook_sections: {
              only: [:id, :title, :section_index, :word_count, :allegory_attributes]
            }
          }
        ),
        transformation_attributes: attributes
      }, 'Book transformed successfully')
      
    rescue => e
      Rails.logger.error "Book transformation failed: #{e.message}"
      render_error("Transformation failed: #{e.message}")
    end
  end
  
  # GET /writebooks/:id/export
  def export
    format = params[:format] || 'markdown'
    
    begin
      export_result = @writebook.export_to_format(format, params[:export_options] || {})
      
      case format
      when 'markdown'
        render plain: export_result, content_type: 'text/markdown'
      when 'pdf'
        send_file export_result[:file_path], type: 'application/pdf', filename: "#{@writebook.title}.pdf"
      when 'writebook'
        render json: export_result
      else
        render json: { export_data: export_result, format: format }
      end
      
    rescue => e
      Rails.logger.error "Book export failed: #{e.message}"
      render_error("Export failed: #{e.message}")
    end
  end
  
  # POST /writebooks/from_conversation
  def create_from_conversation
    conversation = Conversation.find(params[:conversation_id])
    
    book_options = {
      title: params[:title] || "Book: #{conversation.title}",
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
        conversation,
        book_options.merge(section_options: section_options)
      )
      
      render_success(
        book.as_json(
          include: {
            writebook_sections: {
              only: [:id, :title, :section_index, :word_count, :source_message_id],
              methods: [:from_message?]
            }
          }
        ),
        "Successfully created book: #{book.title}"
      )
      
    rescue => e
      Rails.logger.error "Book creation from conversation failed: #{e.message}"
      render_error("Book creation failed: #{e.message}")
    end
  rescue ActiveRecord::RecordNotFound
    render_not_found('Conversation not found')
  end

  def writebook_params
    params.require(:writebook).permit(:title, :author, :version, :description, :genre, :target_audience, allegory_settings: {})
  end
end
