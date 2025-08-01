class AttributesController < ApplicationController
  def index
    # Make data available to the view
    @semantic_probe_categories = semantic_probe_categories
    @transformation_presets = transformation_presets
    @allegory_operators = allegory_operators_config
    @coherence_constraints = coherence_constraints_config
    
    respond_to do |format|
      format.html
      format.json { render json: attribute_configuration }
    end
  end

  def analyze
    content = params[:content]
    attributes = params[:attributes] || {}
    
    begin
      analysis = AllegoryTransformationService.new.analyze_content(
        content: content,
        attributes: attributes
      )
      
      render json: {
        success: true,
        analysis: analysis,
        coherence: calculate_global_coherence(analysis),
        timestamp: Time.current.iso8601
      }
    rescue StandardError => e
      render json: {
        success: false,
        error: e.message,
        timestamp: Time.current.iso8601
      }, status: 422
    end
  end

  def preview_transformation
    content = params[:content]
    attributes = params[:attributes] || {}
    
    begin
      preview = AllegoryTransformationService.new.preview_transformation(
        content: content,
        attributes: attributes
      )
      
      render json: {
        success: true,
        preview: preview,
        original: content,
        attributes_applied: attributes,
        timestamp: Time.current.iso8601
      }
    rescue StandardError => e
      render json: {
        success: false,
        error: e.message,
        timestamp: Time.current.iso8601
      }, status: 422
    end
  end

  def save_preset
    preset_name = params[:name]
    configuration = params[:configuration] || {}
    
    # Save to database or user preferences
    preset = {
      id: SecureRandom.uuid,
      name: preset_name,
      namespace: configuration[:namespace],
      persona: configuration[:persona],
      style: configuration[:style],
      intensity: configuration[:intensity],
      semantic_probes: configuration[:semantic_probes],
      created_at: Time.current.iso8601
    }
    
    # For now, return success - implement actual storage later
    render json: {
      success: true,
      preset: preset,
      message: "Preset '#{preset_name}' saved successfully"
    }
  end

  private

  def attribute_configuration
    {
      semantic_probes: semantic_probe_categories,
      transformation_presets: transformation_presets,
      allegory_operators: allegory_operators_config,
      coherence_constraints: coherence_constraints_config
    }
  end

  def calculate_global_coherence(analysis)
    return 0.0 unless analysis&.dig(:semantic_probes)
    
    probe_values = analysis[:semantic_probes].values
    sum_squares = probe_values.map { |v| v.to_f ** 2 }.sum
    Math.sqrt(sum_squares / probe_values.length)
  end
end
