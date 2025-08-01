class MessageAnalysisController < ApplicationController
  before_action :set_conversation, only: [:select_messages, :summarize, :show_summary]
  
  def index
    @conversations = Conversation.includes(:messages)
                                .recent.limit(20)
    @recent_summaries = ConversationSummary.recent.limit(10) if defined?(ConversationSummary)
  end

  def select_messages
    Rails.logger.info "MessageAnalysis#select_messages - START - Conversation: #{@conversation.id}"
    puts "DEBUG: MessageAnalysis#select_messages called for conversation #{@conversation.id}"
    flash.now[:info] = "✅ Successfully loaded message analysis for #{@conversation.title}"
    
    @messages = @conversation.messages.includes(:message_media).ordered
    @user_messages = @messages.by_role('user')
    @assistant_messages = @messages.by_role('assistant')
    @system_messages = @messages.by_role('system')
    @tool_messages = @messages.by_role('tool')
    
    Rails.logger.info "Found #{@messages.count} messages: #{@user_messages.count} user, #{@assistant_messages.count} assistant"
    
    # Group assistant messages by Custom GPT if applicable
    @gpt_groups = @assistant_messages.group_by(&:gizmo_id)
                                    .transform_values { |msgs| msgs.first.custom_gpt }
                                    
    Rails.logger.info "GPT groups: #{@gpt_groups.keys}"
    
    # Add success message
    flash.now[:success] = "Found #{@messages.count} messages ready for analysis"
    Rails.logger.info "MessageAnalysis#select_messages - SUCCESS - Rendering view"
    puts "DEBUG: About to render select_messages view with #{@messages.count} messages"
  rescue => e
    Rails.logger.error "Error in select_messages: #{e.message}"
    Rails.logger.error e.backtrace.join("\n")
    flash[:error] = "Error loading message analysis: #{e.message}"
    redirect_to conversation_path(@conversation)
  end

  def summarize
    selected_message_ids = params[:message_ids] || []
    @selected_messages = @conversation.messages.where(id: selected_message_ids).ordered
    
    if @selected_messages.empty?
      flash[:error] = "Please select at least one message to summarize"
      redirect_to select_messages_message_analysis_index_path(conversation_id: @conversation.id)
      return
    end
    
    summarization_options = {
      include_roles: params[:include_roles] || [],
      exclude_system: params[:exclude_system] == 'true',
      exclude_tools: params[:exclude_tools] == 'true',
      summary_type: params[:summary_type] || 'comprehensive',
      focus_area: params[:focus_area]
    }
    
    # Create analysis summary
    @summary = generate_summary(@selected_messages, summarization_options)
    
    # Save analysis to database
    @message_analysis = MessageAnalysis.new(
      conversation: @conversation,
      summary_type: summarization_options[:summary_type],
      focus_area: summarization_options[:focus_area],
      selected_message_id_array: selected_message_ids,
      summary_hash: @summary,
      metadata_hash: {
        options: summarization_options,
        created_at: Time.current,
        user_agent: request.user_agent
      },
      message_count: @selected_messages.count,
      word_count: @selected_messages.sum(:word_count),
      created_by: 'system' # TODO: Add user authentication
    )
    
    if @message_analysis.save
      respond_to do |format|
        format.html do
          redirect_to show_summary_message_analysis_index_path(
            conversation_id: @conversation.id, 
            analysis_id: @message_analysis.id
          )
        end
        format.json { render json: { 
          analysis_id: @message_analysis.id,
          summary: @summary, 
          message_count: @selected_messages.count 
        } }
      end
    else
      flash[:error] = "Failed to save analysis: #{@message_analysis.errors.full_messages.join(', ')}"
      redirect_to select_messages_message_analysis_index_path(conversation_id: @conversation.id)
    end
  end

  def show_summary
    # Load from database using analysis_id parameter
    analysis_id = params[:analysis_id]
    @message_analysis = MessageAnalysis.find_by(id: analysis_id, conversation: @conversation)
    
    unless @message_analysis
      flash[:error] = "Analysis not found. Please create a new analysis."
      redirect_to select_messages_message_analysis_index_path(conversation_id: @conversation.id)
      return
    end
    
    @summary = @message_analysis.summary
    @selected_messages = @message_analysis.selected_messages
  end
  
  private
  
  def set_conversation
    @conversation = Conversation.find(params[:conversation_id] || params[:id])
  rescue ActiveRecord::RecordNotFound
    flash[:error] = "Conversation not found"
    redirect_to conversations_path
  end
  
  def generate_summary(messages, options = {})
    # Use real LLM analysis service
    llm_service = LlmAnalysisService.new
    llm_service.analyze_messages(messages, options)
  end
  
end
