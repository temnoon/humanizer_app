class Api::V1::ArchiveController < ApplicationController
  def summary
    result = ArchiveClient.get_chat_summary(params[:id])
    
    if result[:error]
      render_error(result[:error], result[:status] || :service_unavailable)
    else
      render_success(result)
    end
  end

  def humanize
    text = params[:text]
    style = params[:style] || 'default'
    
    if text.blank?
      render_error('Text parameter is required')
      return
    end

    result = ArchiveClient.humanize_text(text, style)
    
    if result[:error]
      render_error(result[:error], result[:status] || :service_unavailable)
    else
      render_success(result)
    end
  end

  def analyze_discourse
    posts = params[:posts]
    
    if posts.blank?
      render_error('Posts parameter is required')
      return
    end

    result = ArchiveClient.analyze_discourse_posts(posts)
    
    if result[:error]
      render_error(result[:error], result[:status] || :service_unavailable)
    else
      render_success(result)
    end
  end

  def status
    result = ArchiveClient.get_pipeline_status
    
    if result[:error]
      render_error(result[:error], result[:status] || :service_unavailable)
    else
      render_success(result)
    end
  end
end
