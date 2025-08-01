module ApplicationHelper
  def render_safe_message_content(content)
    return "" if content.blank?
    
    # Check if content contains HTML/code patterns
    if contains_code_patterns?(content)
      render_as_code_block(content)
    else
      # Safe text rendering with line breaks
      safe_simple_format(content)
    end
  end
  
  private
  
  def contains_code_patterns?(content)
    # Detect HTML, JavaScript, CSS, or other code patterns
    code_indicators = [
      /<[^>]+>/, # HTML tags
      /function\s*\(/, # JavaScript functions
      /\bclass\s+\w+/, # CSS classes or programming classes
      /\{[\s\S]*\}/, # Curly braces (CSS, JS, JSON)
      /(?:import|export|require)\s+/, # Module imports
      /(?:var|let|const|function)\s+/, # JavaScript keywords
      /(?:public|private|protected)\s+/, # Programming access modifiers
      /\$\w+/, # Variables (PHP, jQuery, etc.)
      /\#include|#define/, # C/C++ preprocessor
      /^\s*\/\/|^\s*\/\*/, # Comments
      /\bselect\s+.*\bfrom\b/i, # SQL
      /\b(?:div|span|img|a|p|h\d)\b.*[<>]/ # HTML element patterns
    ]
    
    code_indicators.any? { |pattern| content.match?(pattern) }
  end
  
  def render_as_code_block(content)
    # Detect language for syntax highlighting
    language = detect_language(content)
    
    content_tag :div, class: "bg-gray-100 dark:bg-gray-800 rounded-lg p-4 my-4 overflow-x-auto" do
      content_tag :div, class: "flex items-center justify-between mb-2" do
        concat content_tag(:span, "💻 Code Block", class: "text-sm font-medium text-gray-600 dark:text-gray-400")
        concat content_tag(:span, language.humanize, class: "text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded")
      end +
      content_tag(:pre, class: "text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono leading-relaxed") do
        content_tag(:code, h(content))
      end
    end
  end
  
  def detect_language(content)
    # Simple language detection based on patterns
    return 'html' if content.match?(/<(?:html|head|body|div|span|p|h\d)/)
    return 'javascript' if content.match?(/(?:function|var|let|const|=>|\$\()/)
    return 'css' if content.match?(/\{[^}]*(?:color|background|margin|padding|font)/)
    return 'sql' if content.match?(/\b(?:select|insert|update|delete|from|where)\b/i)
    return 'json' if content.match?(/^\s*\{.*\}\s*$/m) && content.include?('"')
    return 'xml' if content.match?(/<\?xml/) || content.match?(/<\w+[^>]*\/>/)
    return 'php' if content.match?(/<\?php/)
    return 'python' if content.match?(/\bdef\s+\w+\(|import\s+\w+/)
    return 'ruby' if content.match?(/\bdef\s+\w+|require\s+['"]/)
    return 'bash' if content.match?(/^\s*(?:\$|#)/) || content.include?('#!/bin/')
    
    'code'
  end
  
  def safe_simple_format(content)
    # HTML-escape the content and add line breaks
    escaped_content = h(content)
    
    # Convert line breaks to <br> tags
    formatted_content = escaped_content.gsub(/\r?\n/, '<br>')
    
    # Convert double line breaks to paragraphs
    formatted_content = formatted_content.gsub(/(<br>\s*){2,}/, '</p><p class="text-gray-800 dark:text-gray-200 leading-relaxed mb-4">')
    
    # Wrap in paragraph tags
    content_tag :div, class: "text-gray-800 dark:text-gray-200 leading-relaxed" do
      content_tag :p, raw(formatted_content), class: "mb-4"
    end
  end

  # Helper method to extract filter parameters for pagination links
  def filter_params
    base_params = {}
    
    # Extract individual parameters safely
    [:search, :search_title, :search_content, :search_semantic,
     :date_from, :date_to, :source_type, :gpt_model,
     :min_messages, :max_messages, :min_words, :max_words,
     :has_attachments, :has_tools, :gizmo_id,
     :sort_column, :sort_direction, :per_page].each do |key|
      if params[key].present?
        base_params[key] = params[key]
      end
    end
    
    # Handle roles array separately
    if params[:roles].present?
      base_params[:roles] = params[:roles].compact_blank
    end
    
    base_params
  end
end