# Allegory Transformation Service
# Implements the quantum-inspired narrative transformation framework
# Based on the theoretical foundation from the Narrative Theory Overview
class AllegoryTransformationService
  include HTTParty
  
  # Integration with Python backend for actual LLM processing
  base_uri ENV.fetch('LIGHTHOUSE_API_URL', 'http://localhost:8100')
  
  attr_reader :namespace, :persona, :style, :semantic_probes
  
  def initialize(namespace: 'lamish-galaxy', persona: 'temnoon', style: 'contemplative')
    @namespace = namespace
    @persona = persona  
    @style = style
    @semantic_probes = initialize_semantic_probes
  end
  
  # Main transformation method - implements consciousness transformation protocol
  def transform_content(content:, role:, context: {})
    # Step 1: Semantic Measurement (POVM application)
    semantic_state = measure_semantic_state(content, context)
    
    # Step 2: Apply Attribute Operators (namespace, persona, style)
    transformed_state = apply_attribute_operators(semantic_state)
    
    # Step 3: Collapse to Narrative Text (Born rule analogue)
    generate_narrative_output(transformed_state, content, role, context)
  end
  
  # Create SIC-POVM-like semantic coverage of meaning space
  def initialize_semantic_probes
    # These probes represent informationally complete semantic measurements
    # Based on the theoretical framework's quantum measurement model
    {
      phenomenological: {
        consciousness: 'awareness, subjective experience, qualia',
        temporality: 'time, duration, sequence, memory',
        intentionality: 'meaning, purpose, directedness',
        embodiment: 'physical experience, sensation, presence'
      },
      
      narrative: {
        plot: 'story structure, causation, events',
        character: 'agency, personality, motivation', 
        setting: 'environment, context, atmosphere',
        theme: 'meaning, message, significance'
      },
      
      discourse: {
        voice: 'perspective, tone, point of view',
        register: 'formality, audience, style',
        rhetoric: 'persuasion, argument, appeal',
        genre: 'conventions, expectations, form'
      },
      
      allegory: {
        symbol: 'representation, metaphor, meaning',
        correspondence: 'mapping, analogy, parallel',
        interpretation: 'hermeneutics, decoding, understanding',
        transformation: 'change, development, evolution'
      }
    }
  end
  
  # Measure semantic state using quantum-inspired probes
  def measure_semantic_state(content, context)
    measurement_results = {}
    
    semantic_probes.each do |category, probes|
      measurement_results[category] = {}
      
      probes.each do |probe_name, probe_description|
        # Call Python backend for semantic measurement
        measurement = perform_semantic_measurement(content, probe_description, context)
        measurement_results[category][probe_name] = measurement
      end
    end
    
    # Normalize to valid probability distribution (density matrix constraints)
    normalize_semantic_state(measurement_results)
  end
  
  # Apply namespace, persona, and style transformations (attribute operators)
  def apply_attribute_operators(semantic_state)
    transformed_state = semantic_state.deep_dup
    
    # Namespace transformation (universe of references)
    transformed_state = apply_namespace_operator(transformed_state)
    
    # Persona transformation (worldview and perspective) 
    transformed_state = apply_persona_operator(transformed_state)
    
    # Style transformation (linguistic approach)
    transformed_state = apply_style_operator(transformed_state)
    
    transformed_state
  end

  # New method for analyzing content without full transformation
  def analyze_content(content:, attributes: {})
    # Update instance variables from attributes
    update_attributes(attributes)
    
    # Perform semantic measurement
    semantic_state = measure_semantic_state(content, attributes)
    
    # Calculate complexity metrics
    analysis = {
      semantic_probes: flatten_semantic_state(semantic_state),
      complexity_metrics: calculate_complexity_metrics(content),
      narrative_analysis: analyze_narrative_structure(content),
      discourse_features: extract_discourse_features(content),
      allegory_potential: assess_allegory_potential(semantic_state)
    }
    
    analysis
  end

  # Preview transformation without full processing
  def preview_transformation(content:, attributes: {})
    # Update instance variables from attributes
    update_attributes(attributes)
    
    # Quick semantic analysis
    semantic_state = measure_semantic_state(content, attributes)
    
    # Generate a preview snippet (first 200 characters of transformation)
    preview_content = generate_preview_snippet(content, semantic_state, attributes)
    
    {
      preview_text: preview_content,
      estimated_length: estimate_transformed_length(content),
      transformation_score: calculate_transformation_score(semantic_state),
      applied_attributes: {
        namespace: @namespace,
        persona: @persona,
        style: @style
      }
    }
  end

  private

  def update_attributes(attributes)
    @namespace = attributes[:namespace] if attributes[:namespace]
    @persona = attributes[:persona] if attributes[:persona]
    @style = attributes[:style] if attributes[:style]
  end

  def flatten_semantic_state(semantic_state)
    flattened = {}
    semantic_state.each do |category, probes|
      probes.each do |probe_name, probe_data|
        # Extract the intensity value from the probe data
        intensity = case probe_data
                   when Hash
                     probe_data['intensity'] || probe_data[:intensity] || 0.5
                   when Numeric
                     probe_data
                   else
                     0.5
                   end
        flattened["#{category}_#{probe_name}"] = intensity.to_f
      end
    end
    flattened
  end

  def calculate_complexity_metrics(content)
    words = content.split(/\s+/).length
    sentences = content.split(/[.!?]+/).length
    paragraphs = content.split(/\n\s*\n/).length
    
    {
      word_count: words,
      sentence_count: sentences,
      paragraph_count: paragraphs,
      avg_sentence_length: words.to_f / [sentences, 1].max,
      lexical_density: calculate_lexical_density(content),
      semantic_complexity: [words / 100.0, 1.0].min
    }
  end

  def analyze_narrative_structure(content)
    # Simple narrative analysis
    {
      has_dialogue: content.include?('"') || content.include?("'"),
      temporal_markers: count_temporal_markers(content),
      causal_connectors: count_causal_connectors(content),
      narrative_voice: detect_narrative_voice(content),
      story_elements: detect_story_elements(content)
    }
  end

  def extract_discourse_features(content)
    {
      formality_level: assess_formality(content),
      emotional_tone: assess_emotional_tone(content),
      persuasive_elements: detect_persuasive_elements(content),
      rhetorical_devices: detect_rhetorical_devices(content)
    }
  end

  def assess_allegory_potential(semantic_state)
    allegory_scores = semantic_state[:allegory] || {}
    
    # Extract numeric values from probe data
    values = allegory_scores.values.map do |probe_data|
      case probe_data
      when Hash
        probe_data['intensity'] || probe_data[:intensity] || 0.0
      when Numeric
        probe_data
      else
        0.0
      end
    end
    
    total_score = values.sum.to_f / [values.length, 1].max
    
    {
      overall_score: total_score,
      metaphor_density: extract_intensity(allegory_scores[:symbol]),
      symbolic_richness: extract_intensity(allegory_scores[:correspondence]),
      interpretive_depth: extract_intensity(allegory_scores[:interpretation])
    }
  end

  def generate_preview_snippet(content, semantic_state, attributes)
    # Simple preview generation - in practice, this would call the Python backend
    preview = content.split('.').first
    preview += "... [transformed with #{@persona} perspective in #{@namespace} style]"
    preview[0..200]
  end

  def estimate_transformed_length(content)
    # Estimate based on transformation style
    base_length = content.length
    case @style
    when 'academic'
      (base_length * 1.3).round
    when 'poetic'
      (base_length * 0.8).round
    when 'technical'
      (base_length * 1.5).round
    else
      base_length
    end
  end

  def calculate_transformation_score(semantic_state)
    # Calculate how much transformation is likely based on semantic state
    all_values = semantic_state.values.flat_map(&:values)
    variance = calculate_variance(all_values)
    [variance * 2, 1.0].min
  end

  def calculate_lexical_density(content)
    words = content.downcase.split(/\s+/)
    unique_words = words.uniq.length
    unique_words.to_f / [words.length, 1].max
  end

  def count_temporal_markers(content)
    temporal_words = %w[then now before after during while when since until]
    temporal_words.sum { |word| content.downcase.scan(/\b#{word}\b/).length }
  end

  def count_causal_connectors(content)
    causal_words = %w[because therefore thus hence consequently so]
    causal_words.sum { |word| content.downcase.scan(/\b#{word}\b/).length }
  end

  def detect_narrative_voice(content)
    first_person = content.scan(/\b(I|we|my|our)\b/i).length
    second_person = content.scan(/\byou\b/i).length
    third_person = content.scan(/\b(he|she|they|his|her|their)\b/i).length
    
    max_count = [first_person, second_person, third_person].max
    case [first_person, second_person, third_person].index(max_count)
    when 0 then 'first_person'
    when 1 then 'second_person'
    when 2 then 'third_person'
    else 'indeterminate'
    end
  end

  def detect_story_elements(content)
    {
      characters: content.scan(/[A-Z][a-z]+/).uniq.length,
      locations: content.scan(/\bin\s+[A-Z][a-z]+/).length,
      actions: content.scan(/\b\w+ed\b/).length,
      descriptors: content.scan(/\b\w+ly\b/).length
    }
  end

  def assess_formality(content)
    formal_indicators = content.scan(/\b(therefore|however|furthermore|moreover|consequently)\b/i).length
    informal_indicators = content.scan(/\b(gonna|wanna|kinda|yeah|ok)\b/i).length
    
    if formal_indicators > informal_indicators
      'formal'
    elsif informal_indicators > formal_indicators
      'informal'
    else
      'neutral'
    end
  end

  def assess_emotional_tone(content)
    positive_words = %w[good great excellent wonderful amazing beautiful]
    negative_words = %w[bad terrible awful horrible disappointing ugly]
    
    positive_count = positive_words.sum { |word| content.downcase.scan(/\b#{word}\b/).length }
    negative_count = negative_words.sum { |word| content.downcase.scan(/\b#{word}\b/).length }
    
    if positive_count > negative_count
      'positive'
    elsif negative_count > positive_count
      'negative'
    else
      'neutral'
    end
  end

  def detect_persuasive_elements(content)
    {
      questions: content.scan(/\?/).length,
      imperatives: content.scan(/\b(should|must|need|have to)\b/i).length,
      superlatives: content.scan(/\b(best|worst|most|least)\b/i).length,
      statistics: content.scan(/\b\d+%?\b/).length
    }
  end

  def detect_rhetorical_devices(content)
    {
      repetition: detect_repetition(content),
      metaphors: content.scan(/\bis like\b|\bas\s+\w+\s+as\b/i).length,
      alliteration: detect_alliteration(content),
      parallel_structure: detect_parallel_structure(content)
    }
  end

  def detect_repetition(content)
    words = content.downcase.split(/\s+/)
    word_counts = words.tally
    repeated_words = word_counts.select { |_, count| count > 2 }
    repeated_words.length
  end

  def detect_alliteration(content)
    words = content.split(/\s+/)
    alliterative_pairs = 0
    (0...words.length-1).each do |i|
      if words[i][0]&.downcase == words[i+1][0]&.downcase
        alliterative_pairs += 1
      end
    end
    alliterative_pairs
  end

  def detect_parallel_structure(content)
    # Simple detection of parallel lists
    content.scan(/\w+,\s*\w+,\s*(and\s+)?\w+/).length
  end

  def calculate_variance(values)
    return 0.0 if values.empty?
    
    mean = values.sum.to_f / values.length
    variance = values.sum { |v| (v - mean) ** 2 } / values.length
    Math.sqrt(variance)
  end

  def extract_intensity(probe_data)
    case probe_data
    when Hash
      probe_data['intensity'] || probe_data[:intensity] || 0.0
    when Numeric
      probe_data.to_f
    else
      0.0
    end
  end
  
  # Generate final narrative output using Born rule analogue
  def generate_narrative_output(transformed_state, original_content, role, context)
    # Prepare transformation request for Python backend
    transformation_request = {
      text: original_content,
      role: role,
      namespace: namespace,
      persona: persona,
      style: style,
      semantic_state: transformed_state,
      context: context,
      transformation_type: 'allegory',
      coherence_constraints: calculate_coherence_constraints(transformed_state)
    }
    
    # Call Python backend for actual LLM transformation
    response = call_python_transformation_api(transformation_request)
    
    # Validate coherence using Born rule constraints
    validate_transformation_coherence(response, transformed_state)
    
    response['transformed_text'] || original_content
  end
  
  private
  
  # Apply namespace operator (universe of references transformation)
  def apply_namespace_operator(state)
    namespace_transformations = {
      'lamish-galaxy' => {
        # Specific transformations for lamish-galaxy namespace
        consciousness: { amplification: 1.2, perspective: 'cosmic' },
        temporality: { amplification: 1.0, perspective: 'eternal' },
        embodiment: { amplification: 0.8, perspective: 'ethereal' }
      },
      
      'philosophical' => {
        consciousness: { amplification: 1.5, perspective: 'analytical' },
        temporality: { amplification: 1.1, perspective: 'historical' },
        embodiment: { amplification: 0.9, perspective: 'conceptual' }
      },
      
      'technical' => {
        consciousness: { amplification: 0.7, perspective: 'systematic' },
        temporality: { amplification: 1.0, perspective: 'sequential' },
        embodiment: { amplification: 1.3, perspective: 'practical' }
      }
    }
    
    transformations = namespace_transformations[namespace] || {}
    apply_transformations(state, transformations)
  end
  
  # Apply persona operator (worldview transformation)
  def apply_persona_operator(state)
    persona_transformations = {
      'temnoon' => {
        # Specific transformations for temnoon persona
        voice: { amplification: 1.1, perspective: 'introspective' },
        rhetoric: { amplification: 1.2, perspective: 'contemplative' },
        interpretation: { amplification: 1.3, perspective: 'phenomenological' }
      },
      
      'philosopher' => {
        voice: { amplification: 1.4, perspective: 'analytical' },
        rhetoric: { amplification: 1.5, perspective: 'argumentative' },
        interpretation: { amplification: 1.6, perspective: 'systematic' }
      },
      
      'storyteller' => {
        voice: { amplification: 1.3, perspective: 'narrative' },
        rhetoric: { amplification: 1.1, perspective: 'engaging' },
        interpretation: { amplification: 1.2, perspective: 'metaphorical' }
      }
    }
    
    transformations = persona_transformations[persona] || {}
    apply_transformations(state, transformations)
  end
  
  # Apply style operator (linguistic approach transformation)
  def apply_style_operator(state)
    style_transformations = {
      'contemplative' => {
        register: { amplification: 1.1, perspective: 'reflective' },
        voice: { amplification: 1.2, perspective: 'meditative' },
        theme: { amplification: 1.3, perspective: 'deep' }
      },
      
      'analytical' => {
        register: { amplification: 1.4, perspective: 'precise' },
        voice: { amplification: 1.0, perspective: 'objective' },
        theme: { amplification: 1.2, perspective: 'systematic' }
      },
      
      'casual' => {
        register: { amplification: 0.8, perspective: 'informal' },
        voice: { amplification: 1.0, perspective: 'conversational' },
        theme: { amplification: 0.9, perspective: 'accessible' }
      }
    }
    
    transformations = style_transformations[style] || {}
    apply_transformations(state, transformations)
  end
  
  # Apply transformations to semantic state
  def apply_transformations(state, transformations)
    transformed_state = state.deep_dup
    
    transformations.each do |category, transformation|
      if transformed_state.dig(category.to_s)
        transformed_state[category.to_s].each do |probe, value|
          if transformation[:amplification]
            transformed_state[category.to_s][probe]['intensity'] *= transformation[:amplification]
          end
          
          if transformation[:perspective]
            transformed_state[category.to_s][probe]['perspective'] = transformation[:perspective]
          end
        end
      end
    end
    
    normalize_semantic_state(transformed_state)
  end
  
  # Perform semantic measurement via Python backend
  def perform_semantic_measurement(content, probe_description, context)
    begin
      response = self.class.post('/api/semantic_measurement', {
        body: {
          content: content,
          probe: probe_description,
          context: context
        }.to_json,
        headers: { 'Content-Type' => 'application/json' },
        timeout: 30
      })
      
      if response.success?
        measurement = response.parsed_response
        {
          'intensity' => measurement['intensity'] || 0.5,
          'confidence' => measurement['confidence'] || 0.7,
          'semantic_vector' => measurement['semantic_vector'] || [],
          'probe_response' => measurement['probe_response'] || probe_description
        }
      else
        # Fallback measurement
        default_measurement(content, probe_description)
      end
    rescue => e
      Rails.logger.error "Semantic measurement failed: #{e.message}"
      default_measurement(content, probe_description)
    end
  end
  
  # Call Python backend for transformation
  def call_python_transformation_api(request)
    begin
      response = self.class.post('/api/transform', {
        body: request.to_json,
        headers: { 'Content-Type' => 'application/json' },
        timeout: 60
      })
      
      if response.success?
        response.parsed_response
      else
        Rails.logger.error "Transformation API error: #{response.code} - #{response.message}"
        { 'transformed_text' => request[:text], 'error' => 'Transformation failed' }
      end
    rescue => e
      Rails.logger.error "Transformation API call failed: #{e.message}"
      { 'transformed_text' => request[:text], 'error' => e.message }
    end
  end
  
  # Normalize semantic state to maintain probability constraints
  def normalize_semantic_state(state)
    state.each do |category, probes|
      total_intensity = probes.values.sum { |probe| probe['intensity'] || 0 }
      
      next if total_intensity == 0
      
      # Normalize to maintain coherent probability distribution
      normalization_factor = probes.size.to_f / total_intensity
      
      probes.each do |probe_name, probe_data|
        probe_data['intensity'] = (probe_data['intensity'] || 0) * normalization_factor
        probe_data['normalized'] = true
      end
    end
    
    state
  end
  
  # Calculate coherence constraints based on Born rule analogue
  def calculate_coherence_constraints(semantic_state)
    {
      semantic_coherence: calculate_semantic_coherence(semantic_state),
      narrative_coherence: calculate_narrative_coherence(semantic_state),
      transformation_coherence: calculate_transformation_coherence(semantic_state),
      total_probability: calculate_total_probability(semantic_state)
    }
  end
  
  # Validate transformation maintains coherence
  def validate_transformation_coherence(response, semantic_state)
    # Implementation of coherence validation
    # Based on quantum measurement consistency principles
    constraints = calculate_coherence_constraints(semantic_state)
    
    # Log coherence metrics for analysis
    Rails.logger.info "Transformation coherence: #{constraints}"
    
    # Could add rejection/refinement logic here if coherence is too low
    
    response
  end
  
  # Default measurement when API is unavailable
  def default_measurement(content, probe_description)
    # Simple heuristic-based measurement
    word_count = content.split.length
    complexity = [content.scan(/[.!?]/).length, 1].max
    
    {
      'intensity' => [word_count / 100.0, 1.0].min,
      'confidence' => 0.3, # Low confidence for fallback
      'semantic_vector' => [],
      'probe_response' => "Fallback measurement for: #{probe_description}",
      'fallback' => true
    }
  end
  
  # Coherence calculation methods (simplified implementations)
  def calculate_semantic_coherence(state)
    # Measure consistency across semantic categories
    intensities = state.values.flat_map { |probes| probes.values.map { |p| p['intensity'] || 0 } }
    mean_intensity = intensities.sum / intensities.length.to_f
    variance = intensities.sum { |i| (i - mean_intensity) ** 2 } / intensities.length.to_f
    
    1.0 / (1.0 + variance) # Higher coherence = lower variance
  end
  
  def calculate_narrative_coherence(state)
    # Measure narrative consistency
    narrative_probes = state['narrative'] || {}
    narrative_probes.values.sum { |p| p['confidence'] || 0 } / [narrative_probes.length, 1].max
  end
  
  def calculate_transformation_coherence(state)
    # Measure allegory transformation consistency
    allegory_probes = state['allegory'] || {}
    allegory_probes.values.sum { |p| p['intensity'] || 0 } / [allegory_probes.length, 1].max
  end
  
  def calculate_total_probability(state)
    # Ensure probabilities sum appropriately (Born rule analogue)
    total = state.values.flat_map { |probes| probes.values.map { |p| p['intensity'] || 0 } }.sum
    total / state.values.sum(&:length).to_f # Normalized by total number of probes
  end
end