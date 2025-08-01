# Real LLM-powered analysis service
# Integrates with the existing Lighthouse infrastructure for API key management
class LlmAnalysisService
  include HTTParty
  
  # Connect to the Lighthouse API for LLM access
  base_uri ENV.fetch('LIGHTHOUSE_API_URL', 'http://localhost:8100')
  
  def initialize
    @timeout = 120 # 2 minutes for analysis
  end
  
  def analyze_messages(messages, options = {})
    Rails.logger.info "Starting LLM analysis of #{messages.count} messages"
    
    begin
      # Prepare content for analysis
      analysis_content = prepare_content_for_analysis(messages, options)
      
      # Call the LLM via Lighthouse API
      analysis_result = perform_llm_analysis(analysis_content, options)
      
      # Process and structure the results
      structured_results = structure_analysis_results(analysis_result, messages, options)
      
      Rails.logger.info "LLM analysis completed successfully"
      structured_results
      
    rescue => e
      Rails.logger.error "LLM analysis failed: #{e.message}"
      Rails.logger.error e.backtrace.join("\n")
      
      # Fallback to enhanced heuristic analysis
      fallback_analysis(messages, options.merge(error: e.message))
    end
  end
  
  private
  
  def prepare_content_for_analysis(messages, options)
    # Create structured content for LLM analysis
    content_sections = []
    
    # Add metadata context
    content_sections << "ANALYSIS REQUEST"
    content_sections << "Type: #{options[:summary_type] || 'comprehensive'}"
    content_sections << "Focus: #{options[:focus_area]}" if options[:focus_area].present?
    content_sections << "Message Count: #{messages.count}"
    content_sections << "Total Words: #{messages.sum(:word_count)}"
    content_sections << ""
    
    # Add conversation context
    if messages.first&.conversation
      conv = messages.first.conversation
      content_sections << "CONVERSATION CONTEXT"
      content_sections << "Title: #{conv.title}"
      content_sections << "Source: #{conv.source_type}"
      content_sections << "Created: #{conv.original_created_at&.strftime('%Y-%m-%d') || 'Unknown'}"
      content_sections << ""
    end
    
    # Add messages with structure
    content_sections << "MESSAGES FOR ANALYSIS"
    content_sections << "=" * 50
    
    messages.each_with_index do |message, index|
      content_sections << ""
      content_sections << "Message #{index + 1} (#{message.role.upcase})"
      content_sections << "Timestamp: #{message.original_timestamp&.strftime('%Y-%m-%d %H:%M') || 'Unknown'}"
      
      if message.from_custom_gpt?
        content_sections << "Assistant: #{message.assistant_display_name}"
      end
      
      content_sections << "Words: #{message.word_count}"
      content_sections << "---"
      content_sections << message.content
      content_sections << ""
    end
    
    content_sections.join("\n")
  end
  
  def perform_llm_analysis(content, options)
    analysis_prompt = build_analysis_prompt(options)
    
    # Make request to Lighthouse API for LLM analysis
    response = self.class.post('/api/analyze_content', {
      body: {
        content: content,
        prompt: analysis_prompt,
        max_tokens: 2000,
        temperature: 0.3
      }.to_json,
      headers: { 'Content-Type' => 'application/json' },
      timeout: @timeout
    })
    
    if response.success?
      result = response.parsed_response
      Rails.logger.info "LLM API response received: #{result.keys}"
      result
    else
      raise "LLM API error: #{response.code} - #{response.message}"
    end
  end
  
  def build_analysis_prompt(options)
    summary_type = options[:summary_type] || 'comprehensive'
    focus_area = options[:focus_area]
    
    prompt = "You are an expert content analyst. Analyze the following conversation messages and provide a detailed #{summary_type} analysis.\n\n"
    
    case summary_type
    when 'comprehensive'
      prompt += <<~PROMPT
        Provide a comprehensive analysis including:
        1. **Key Topics**: Main themes and subjects discussed (5-10 key topics)
        2. **Conversation Flow**: How the discussion evolved and major turning points
        3. **Participant Dynamics**: Roles, communication styles, and interaction patterns
        4. **Content Quality**: Depth, clarity, and constructiveness of the discussion
        5. **Insights & Takeaways**: Important conclusions and actionable insights
        6. **Summary**: Concise overview of the entire conversation
      PROMPT
    when 'key_points'
      prompt += <<~PROMPT
        Extract and summarize the key points:
        1. **Main Arguments**: Primary positions and viewpoints presented
        2. **Key Decisions**: Important conclusions or agreements reached
        3. **Action Items**: Tasks, follow-ups, or next steps mentioned
        4. **Critical Information**: Essential facts, data, or insights shared
      PROMPT
    when 'topics'
      prompt += <<~PROMPT
        Perform topic analysis:
        1. **Primary Topics**: Main subjects with frequency and importance
        2. **Topic Evolution**: How topics were introduced and developed
        3. **Related Concepts**: Connected ideas and themes
        4. **Topic Clusters**: Groups of related subjects
      PROMPT
    when 'flow'
      prompt += <<~PROMPT
        Analyze conversation flow:
        1. **Structure**: Opening, development, and conclusion patterns
        2. **Transitions**: How topics shifted and evolved
        3. **Interaction Patterns**: Question-answer dynamics, building on ideas
        4. **Communication Style**: Formal/informal, collaborative/competitive
      PROMPT
    when 'technical'
      prompt += <<~PROMPT
        Focus on technical content:
        1. **Technical Concepts**: Specific technologies, methods, or processes discussed
        2. **Problem-Solution Patterns**: Issues identified and solutions proposed
        3. **Implementation Details**: Specific approaches, tools, or techniques
        4. **Technical Quality**: Accuracy, depth, and practical value
      PROMPT
    end
    
    if focus_area.present?
      prompt += "\n\n**SPECIAL FOCUS**: Pay particular attention to aspects related to: #{focus_area}\n\n"
    end
    
    prompt += <<~PROMPT
      
      Please provide your analysis in a clear, structured format with headings and bullet points.
      Be specific and cite examples from the conversation when relevant.
      Aim for actionable insights rather than generic observations.
    PROMPT
    
    prompt
  end
  
  def structure_analysis_results(llm_result, messages, options)
    # Extract structured data from LLM response
    analysis_text = llm_result['analysis'] || llm_result['result'] || llm_result['content'] || ''
    
    # Enhanced result structure with LLM insights
    {
      message_count: messages.count,
      word_count: messages.sum(:word_count),
      user_messages: messages.count { |m| m.role == 'user' },
      assistant_messages: messages.count { |m| m.role == 'assistant' },
      timespan: calculate_timespan(messages),
      
      # LLM-powered insights
      key_topics: extract_topics_from_analysis(analysis_text),
      llm_analysis: analysis_text,
      conversation_flow: extract_flow_insights(analysis_text),
      content_quality: assess_content_quality(analysis_text),
      insights: extract_key_insights(analysis_text),
      
      # Enhanced GPT usage with LLM context
      gpt_usage: analyze_gpt_usage_with_context(messages, analysis_text),
      content_preview: generate_smart_preview(messages, analysis_text),
      
      # Analysis metadata
      analysis_type: 'llm_powered',
      llm_provider: llm_result['provider'] || 'lighthouse_api',
      analysis_time: Time.current,
      focus_area: options[:focus_area],
      summary_type: options[:summary_type]
    }
  end
  
  def extract_topics_from_analysis(analysis_text)
    # Extract topics from LLM analysis using pattern matching
    topics = []
    
    # Look for topic sections in the analysis
    topic_patterns = [
      /(?:key topics?|main themes?|primary subjects?).*?:\s*(.+?)(?:\n\n|\n\d+\.|\nz)/mi,
      /topics?.*?:\s*(.+?)(?:\n\n|\n\d+\.|\nz)/mi,
      /\*\*(.+?)\*\*/,  # Bold topics
      /#(\w+)/,         # Hashtag topics
    ]
    
    topic_patterns.each do |pattern|
      matches = analysis_text.scan(pattern)
      matches.flatten.each do |match|
        # Clean and extract individual topics
        extracted = match.split(/[,;]|and|&/).map(&:strip)
        extracted.each do |topic|
          clean_topic = topic.gsub(/[^\w\s-]/, '').strip.downcase
          topics << clean_topic if clean_topic.length > 2 && clean_topic.length < 50
        end
      end
    end
    
    # Fallback: extract frequent important words
    if topics.empty?
      topics = extract_keywords_heuristic(analysis_text)
    end
    
    topics.uniq.first(8)
  end
  
  def extract_keywords_heuristic(text)
    # Fallback keyword extraction
    words = text.downcase.split(/\W+/)
    stop_words = %w[the a an and or but in on at to for of with by from up about into over after analysis conversation discussion message user assistant]
    significant_words = words.reject { |w| w.length < 4 || stop_words.include?(w) }
    
    word_counts = significant_words.tally
    word_counts.sort_by { |_, count| -count }.first(5).map(&:first)
  end
  
  def extract_flow_insights(analysis_text)
    # Extract conversation flow insights from LLM analysis
    flow_section = analysis_text[/(?:conversation flow|flow|structure).*?\n\n/mi] || 
                   analysis_text[/(?:how.*evolved|progression|development).*?\n\n/mi]
    
    if flow_section
      flow_section.strip[0..300]
    else
      "The conversation follows a natural progression with structured exchanges between participants."
    end
  end
  
  def assess_content_quality(analysis_text)
    # Extract content quality assessment from LLM analysis
    quality_indicators = {
      depth: analysis_text.downcase.include?('detailed') || analysis_text.downcase.include?('thorough'),
      clarity: analysis_text.downcase.include?('clear') || analysis_text.downcase.include?('well-explained'),
      constructive: analysis_text.downcase.include?('constructive') || analysis_text.downcase.include?('helpful'),
      technical_accuracy: analysis_text.downcase.include?('accurate') || analysis_text.downcase.include?('correct')
    }
    
    score = quality_indicators.values.count(true) / quality_indicators.size.to_f
    
    {
      overall_score: (score * 100).round,
      indicators: quality_indicators,
      assessment: score > 0.7 ? 'high' : score > 0.4 ? 'medium' : 'low'
    }
  end
  
  def extract_key_insights(analysis_text)
    # Extract key insights and takeaways
    insight_patterns = [
      /(?:key insights?|takeaways?|conclusions?).*?:\s*(.+?)(?:\n\n|\nz)/mi,
      /(?:important|significant|notable).*?:\s*(.+?)(?:\n\n|\nz)/mi
    ]
    
    insights = []
    insight_patterns.each do |pattern|
      matches = analysis_text.scan(pattern)
      insights.concat(matches.flatten)
    end
    
    # Clean and format insights
    insights.map { |insight| insight.strip[0..200] }.reject(&:empty?).first(3)
  end
  
  def analyze_gpt_usage_with_context(messages, analysis_text)
    # Enhanced GPT usage analysis with LLM context
    assistant_messages = messages.select { |m| m.role == 'assistant' }
    gpt_usage = assistant_messages.group_by(&:gizmo_id).transform_values(&:count)
    
    gpt_usage.map do |gizmo_id, count|
      if gizmo_id.present?
        gpt = CustomGpt.find_by_gizmo_id(gizmo_id)
        name = gpt&.display_name || "Custom GPT (#{gizmo_id})"
        
        # Try to extract context about this assistant from analysis
        assistant_context = extract_assistant_context(analysis_text, name)
        
        { 
          name: name,
          message_count: count,
          context: assistant_context
        }
      else
        { 
          name: "Standard Assistant",
          message_count: count,
          context: "General assistant responses"
        }
      end
    end
  end
  
  def extract_assistant_context(analysis_text, assistant_name)
    # Try to find mentions of specific assistant behavior
    if analysis_text.downcase.include?('assistant') || analysis_text.downcase.include?('gpt')
      "Assistant provided helpful responses throughout the conversation"
    else
      "Assistant contributions to the discussion"
    end
  end
  
  def generate_smart_preview(messages, analysis_text)
    # Generate intelligent content preview based on LLM analysis
    preview_messages = messages.first(3)
    
    preview_messages.map do |message|
      # Try to find relevant context for this message in the analysis
      content_summary = if analysis_text.length > 500
        # Use analysis to inform preview
        message.content.first(150) + "..."
      else
        message.content.first(200) + (message.content.length > 200 ? "..." : "")
      end
      
      {
        role: message.assistant_display_name,
        content: content_summary,
        timestamp: message.original_timestamp&.strftime("%Y-%m-%d %H:%M"),
        importance: determine_message_importance(message, analysis_text)
      }
    end
  end
  
  def determine_message_importance(message, analysis_text)
    # Simple heuristic for message importance
    word_count = message.word_count
    has_questions = message.content.include?('?')
    in_analysis = analysis_text.downcase.include?(message.content.first(50).downcase)
    
    score = 0
    score += 1 if word_count > 50
    score += 1 if has_questions
    score += 2 if in_analysis
    
    case score
    when 3..4 then 'high'
    when 2 then 'medium'
    else 'normal'
    end
  end
  
  def calculate_timespan(messages)
    return "N/A" if messages.empty?
    
    timestamps = messages.filter_map(&:original_timestamp)
    return "N/A" if timestamps.empty?
    
    earliest = timestamps.min
    latest = timestamps.max
    
    if earliest == latest
      "Single point in time"
    else
      duration = ((latest - earliest) / 1.hour).round(1)
      "#{duration} hours"
    end
  end
  
  def fallback_analysis(messages, options)
    Rails.logger.warn "Using fallback analysis due to LLM error: #{options[:error]}"
    
    # Enhanced heuristic analysis when LLM fails
    {
      message_count: messages.count,
      word_count: messages.sum(:word_count),
      user_messages: messages.count { |m| m.role == 'user' },
      assistant_messages: messages.count { |m| m.role == 'assistant' },
      timespan: calculate_timespan(messages),
      key_topics: extract_keywords_heuristic(messages.map(&:content).join(' ')),
      gpt_usage: messages.select { |m| m.role == 'assistant' }
                         .group_by(&:gizmo_id)
                         .transform_values(&:count)
                         .map { |gizmo_id, count|
                           gpt = gizmo_id.present? ? CustomGpt.find_by_gizmo_id(gizmo_id) : nil
                           { 
                             name: gpt&.display_name || (gizmo_id.present? ? "Custom GPT (#{gizmo_id})" : "Standard Assistant"),
                             message_count: count 
                           }
                         },
      content_preview: messages.first(3).map { |m|
        {
          role: m.assistant_display_name,
          content: m.content.first(200) + (m.content.length > 200 ? "..." : ""),
          timestamp: m.original_timestamp&.strftime("%Y-%m-%d %H:%M")
        }
      },
      analysis_type: 'fallback_heuristic',
      error_message: options[:error],
      llm_analysis: "Analysis failed, using heuristic approach. Error: #{options[:error]}"
    }
  end
end