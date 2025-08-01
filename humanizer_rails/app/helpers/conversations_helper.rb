module ConversationsHelper
  def source_color(source_type)
    case source_type.to_s.downcase
    when 'chatgpt'
      'green'
    when 'discourse'
      'blue'
    when 'manual'
      'purple'
    when 'transformed'
      'orange'
    else
      'gray'
    end
  end
  
  def format_message_count(count)
    if count < 1000
      count.to_s
    elsif count < 1_000_000
      "#{(count / 1000.0).round(1)}K"
    else
      "#{(count / 1_000_000.0).round(1)}M"
    end
  end
  
  def format_word_count(count)
    number_with_delimiter(count)
  end
  
  def conversation_status_badge(conversation)
    if conversation.messages.any?
      content_tag :span, "✅ Complete", 
                  class: "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
    else
      content_tag :span, "⚠️ Empty", 
                  class: "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800"
    end
  end
  
  def semantic_coherence_indicator(conversation)
    # Calculate coherence from metadata if available
    coherence = conversation.metadata.dig('semantic_coherence') || 0.75
    
    color_class = if coherence > 0.8
      'text-green-600'
    elsif coherence > 0.6
      'text-yellow-600'
    else
      'text-red-600'
    end
    
    content_tag :span, "⚛️ #{(coherence * 100).round}%", class: "text-sm #{color_class}"
  end
  
  def format_metadata_value(key, value)
    # Convert Unix timestamps to readable format
    if key.to_s.include?('time') || key.to_s.include?('date') || key.to_s.include?('created') || key.to_s.include?('updated')
      if value.is_a?(Numeric) && value.to_s.length >= 10
        # Unix timestamp
        Time.at(value).strftime("%Y-%m-%d %H:%M:%S")
      elsif value.is_a?(String) && value.match?(/^\d{10,13}$/)
        # String Unix timestamp
        Time.at(value.to_i).strftime("%Y-%m-%d %H:%M:%S")
      else
        value.to_s
      end
    else
      value.to_s
    end
  end
  
end