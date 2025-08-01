class ApplicationController < ActionController::Base
  # Enable both API and HTML responses
  protect_from_forgery with: :null_session
  
  before_action :set_response_format

  private

  def set_response_format
    # Don't override the format if it's explicitly set via extension (.json, .html)
    return if request.format && request.format != :*
    
    # Default to JSON for API routes, HTML for GUI routes
    if request.path.start_with?('/api') || request.xhr?
      request.format = :json
    else
      request.format = :html
    end
  end

  def render_success(data = {}, message = 'Success')
    render json: {
      success: true,
      message: message,
      data: data
    }
  end

  def render_error(message = 'Error', status = :unprocessable_entity)
    render json: {
      success: false,
      message: message
    }, status: status
  end

  def render_not_found(message = 'Resource not found')
    render_error(message, :not_found)
  end

  # Semantic probe configuration for the allegory engine
  def semantic_probe_categories
    [
      # Phenomenological probes (4)
      { key: 'consciousness', name: 'Consciousness', icon: '🧠', value: 0.5, coherence: 0.8 },
      { key: 'intentionality', name: 'Intentionality', icon: '🎯', value: 0.6, coherence: 0.7 },
      { key: 'temporality', name: 'Temporality', icon: '⏰', value: 0.4, coherence: 0.9 },
      { key: 'embodiment', name: 'Embodiment', icon: '🚶', value: 0.5, coherence: 0.6 },
      
      # Narrative probes (4)
      { key: 'causality', name: 'Causality', icon: '🔗', value: 0.7, coherence: 0.8 },
      { key: 'agency', name: 'Agency', icon: '⚡', value: 0.6, coherence: 0.7 },
      { key: 'perspective', name: 'Perspective', icon: '👁️', value: 0.5, coherence: 0.9 },
      { key: 'transformation', name: 'Transformation', icon: '🔄', value: 0.8, coherence: 0.6 },
      
      # Discourse probes (4)
      { key: 'reference', name: 'Reference', icon: '📌', value: 0.5, coherence: 0.8 },
      { key: 'modality', name: 'Modality', icon: '🔮', value: 0.4, coherence: 0.7 },
      { key: 'pragmatics', name: 'Pragmatics', icon: '🎭', value: 0.6, coherence: 0.8 },
      { key: 'coherence', name: 'Coherence', icon: '🌐', value: 0.7, coherence: 0.9 },
      
      # Allegory probes (4)
      { key: 'metaphor', name: 'Metaphor', icon: '🌙', value: 0.6, coherence: 0.7 },
      { key: 'symbol', name: 'Symbol', icon: '⚡', value: 0.5, coherence: 0.8 },
      { key: 'archetype', name: 'Archetype', icon: '👑', value: 0.4, coherence: 0.6 },
      { key: 'transcendence', name: 'Transcendence', icon: '✨', value: 0.7, coherence: 0.9 }
    ]
  end

  # Transformation presets for quick configuration
  def transformation_presets
    [
      {
        id: 'academic',
        name: 'Academic',
        icon: '🎓',
        namespace: 'Scientific Domain',
        persona: 'Academic Scholar',
        style: 'Academic Precision'
      },
      {
        id: 'storyteller',
        name: 'Storyteller',
        icon: '📚',
        namespace: 'Literary Universe',
        persona: 'Master Storyteller',
        style: 'Narrative Drama'
      },
      {
        id: 'philosopher',
        name: 'Philosopher',
        icon: '🤔',
        namespace: 'Philosophical Realm',
        persona: 'Deep Philosopher',
        style: 'Poetic Expression'
      },
      {
        id: 'scientist',
        name: 'Scientist',
        icon: '🔬',
        namespace: 'Scientific Domain',
        persona: 'Research Scientist',
        style: 'Technical Detail'
      },
      {
        id: 'mythic',
        name: 'Mythic',
        icon: '🌟',
        namespace: 'Mythological Space',
        persona: 'Creative Artist',
        style: 'Poetic Expression'
      },
      {
        id: 'conversational',
        name: 'Casual',
        icon: '💬',
        namespace: 'Universal Reality',
        persona: 'Neutral Observer',
        style: 'Conversational Ease'
      }
    ]
  end

  # Allegory operators configuration
  def allegory_operators_config
    {
      namespace: {
        name: 'Namespace (Ω)',
        description: 'Universe of references and context',
        options: [
          { value: 'universal', label: 'Universal Reality' },
          { value: 'scientific', label: 'Scientific Domain' },
          { value: 'mythological', label: 'Mythological Space' },
          { value: 'literary', label: 'Literary Universe' },
          { value: 'philosophical', label: 'Philosophical Realm' },
          { value: 'historical', label: 'Historical Context' }
        ]
      },
      persona: {
        name: 'Persona (Ψ)',
        description: 'Worldview and perspective operator',
        options: [
          { value: 'neutral', label: 'Neutral Observer' },
          { value: 'scholar', label: 'Academic Scholar' },
          { value: 'storyteller', label: 'Master Storyteller' },
          { value: 'scientist', label: 'Research Scientist' },
          { value: 'philosopher', label: 'Deep Philosopher' },
          { value: 'artist', label: 'Creative Artist' }
        ]
      },
      style: {
        name: 'Style (Σ)',
        description: 'Linguistic approach and expression',
        options: [
          { value: 'natural', label: 'Natural Flow' },
          { value: 'academic', label: 'Academic Precision' },
          { value: 'narrative', label: 'Narrative Drama' },
          { value: 'poetic', label: 'Poetic Expression' },
          { value: 'technical', label: 'Technical Detail' },
          { value: 'conversational', label: 'Conversational Ease' }
        ]
      }
    }
  end

  # Coherence constraints based on Born rule analogue
  def coherence_constraints_config
    {
      name: 'Born Rule Constraint',
      formula: 'Σ|⟨ψᵢ|φ⟩|² = 1',
      description: 'Semantic measurement probabilities must sum to unity',
      tolerance: 0.05,
      min_coherence: 0.3,
      max_coherence: 1.0
    }
  end
end
