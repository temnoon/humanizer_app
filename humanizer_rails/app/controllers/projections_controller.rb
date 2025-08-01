class ProjectionsController < ApplicationController
  def index
    @active_projections = LlmTask.where(
      task_type: 'transform',
      result_status: ['pending', 'processing']
    ).order(created_at: :desc)
    
    @completed_projections = LlmTask.where(
      task_type: 'transform', 
      result_status: 'completed'
    ).order(updated_at: :desc).limit(20)
    
    @failed_projections = LlmTask.where(
      task_type: 'transform',
      result_status: 'failed'
    ).order(updated_at: :desc).limit(10)
    
    @stats = {
      total_projections: LlmTask.where(task_type: 'transform').count,
      active_count: @active_projections.count,
      completed_today: LlmTask.where(
        task_type: 'transform',
        result_status: 'completed',
        updated_at: Date.current.beginning_of_day..Date.current.end_of_day
      ).count,
      average_coherence: calculate_average_coherence
    }
  end
  
  def new
    @conversations = Conversation.includes(:messages).order(created_at: :desc).limit(50)
    @writebooks = Writebook.order(created_at: :desc).limit(50)
    
    @default_attributes = {
      namespace: 'lamish-galaxy',
      persona: 'temnoon',
      style: 'contemplative'
    }
    
    @available_namespaces = [
      'lamish-galaxy',
      'philosophical',
      'technical',
      'poetic',
      'scientific'
    ]
    
    @available_personas = [
      'temnoon',
      'philosopher',
      'storyteller',
      'scientist',
      'poet'
    ]
    
    @available_styles = [
      'contemplative',
      'analytical',
      'casual',
      'formal',
      'mystical'
    ]
  end
  
  def create
    # This would handle creating new projections
    # Implementation depends on the form submission from new.html.erb
  end
  
  def show
    @projection = LlmTask.find(params[:id])
    @semantic_analysis = analyze_semantic_coherence(@projection)
  end
  
  private
  
  def calculate_average_coherence
    recent_projections = LlmTask.where(
      task_type: 'transform',
      result_status: 'completed'
    ).where('updated_at > ?', 7.days.ago)
    
    if recent_projections.any?
      coherence_scores = recent_projections.map do |projection|
        projection.metadata.dig('coherence_constraints', 'total_probability') || 0.75
      end
      coherence_scores.sum / coherence_scores.length
    else
      0.75
    end
  end
  
  def analyze_semantic_coherence(projection)
    metadata = projection.metadata || {}
    
    {
      semantic_coherence: metadata.dig('coherence_constraints', 'semantic_coherence') || 0.75,
      narrative_coherence: metadata.dig('coherence_constraints', 'narrative_coherence') || 0.80,
      transformation_coherence: metadata.dig('coherence_constraints', 'transformation_coherence') || 0.70,
      total_probability: metadata.dig('coherence_constraints', 'total_probability') || 0.75,
      semantic_state: metadata['semantic_state'] || {},
      transformation_attributes: metadata['transformation_attributes'] || {}
    }
  end
end
