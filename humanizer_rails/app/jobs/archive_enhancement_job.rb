# frozen_string_literal: true

# Background job for enhancing archived content with LPE processing
class ArchiveEnhancementJob < ApplicationJob
  queue_as :default
  
  # Retry configuration
  retry_on StandardError, wait: :exponentially_longer, attempts: 3
  discard_on ActiveJob::DeserializationError

  def perform(content_id)
    content = ArchivedContent.find(content_id)
    Rails.logger.info "Starting LPE enhancement for content #{content_id}"

    # Update status to processing
    content.update!(processing_status: 'processing')

    begin
      # Call LPE API for attribute extraction
      attributes = extract_attributes(content)
      
      # Call Lamish Lawyer API for quality assessment
      quality_score = assess_quality(content)
      
      # Generate semantic embedding if embedding service is available
      embedding_result = generate_embedding(content)
      
      # Update content with results
      content.update!(
        extracted_attributes: attributes,
        content_quality_score: quality_score,
        processing_status: 'completed'
      )
      
      Rails.logger.info "Successfully enhanced content #{content_id} - Quality: #{quality_score}"
      
      # Trigger related content analysis if high quality
      if quality_score && quality_score > 0.8
        AnalyzeRelatedContentJob.perform_later(content_id)
      end
      
    rescue => e
      Rails.logger.error "Failed to enhance content #{content_id}: #{e.message}"
      content.update!(processing_status: 'failed')
      raise e
    end
  end

  private

  def extract_attributes(content)
    return {} unless content.body_text.present?

    lpe_api_url = ENV['LPE_API_URL'] || 'http://localhost:7201'
    
    response = Faraday.post("#{lpe_api_url}/extract-attributes") do |req|
      req.headers['Content-Type'] = 'application/json'
      req.body = {
        content: content.body_text,
        source_metadata: {
          source_type: content.source_type,
          author: content.author,
          timestamp: content.timestamp&.iso8601
        }
      }.to_json
    end

    if response.success?
      result = JSON.parse(response.body)
      Rails.logger.debug "Extracted attributes for content #{content.id}: #{result.keys}"
      result
    else
      Rails.logger.warn "Failed to extract attributes for content #{content.id}: #{response.status}"
      {}
    end
  rescue => e
    Rails.logger.error "Error extracting attributes for content #{content.id}: #{e.message}"
    {}
  end

  def assess_quality(content)
    return nil unless content.body_text.present?

    lawyer_api_url = ENV['LAWYER_API_URL'] || 'http://localhost:7202'
    
    response = Faraday.post("#{lawyer_api_url}/assess-quality") do |req|
      req.headers['Content-Type'] = 'application/json'
      req.body = {
        content: content.body_text,
        metadata: {
          source_type: content.source_type,
          author: content.author,
          word_count: content.word_count,
          timestamp: content.timestamp&.iso8601
        }
      }.to_json
    end

    if response.success?
      result = JSON.parse(response.body)
      score = result['quality_score']
      Rails.logger.debug "Quality score for content #{content.id}: #{score}"
      score
    else
      Rails.logger.warn "Failed to assess quality for content #{content.id}: #{response.status}"
      nil
    end
  rescue => e
    Rails.logger.error "Error assessing quality for content #{content.id}: #{e.message}"
    nil
  end

  def generate_embedding(content)
    return {} unless content.body_text.present?

    archive_api_url = ENV['ARCHIVE_API_URL'] || 'http://localhost:7200'
    
    response = Faraday.post("#{archive_api_url}/content/#{content.id}/generate-embedding") do |req|
      req.headers['Content-Type'] = 'application/json'
    end

    if response.success?
      result = JSON.parse(response.body)
      Rails.logger.debug "Generated embedding for content #{content.id}"
      result
    else
      Rails.logger.warn "Failed to generate embedding for content #{content.id}: #{response.status}"
      {}
    end
  rescue => e
    Rails.logger.error "Error generating embedding for content #{content.id}: #{e.message}"
    {}
  end
end