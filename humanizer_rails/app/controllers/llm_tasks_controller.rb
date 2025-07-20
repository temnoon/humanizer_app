class LlmTasksController < ApplicationController
  before_action :set_llm_task, only: [:show, :update, :destroy]

  def index
    @llm_tasks = LlmTask.recent
    @llm_tasks = @llm_tasks.by_model(params[:model]) if params[:model].present?
    @llm_tasks = @llm_tasks.where(task_type: params[:task_type]) if params[:task_type].present?
    @llm_tasks = @llm_tasks.where(result_status: params[:status]) if params[:status].present?
    
    @llm_tasks = @llm_tasks.limit(20)
    
    render_success(@llm_tasks)
  end

  def show
    render_success(@llm_task)
  end

  def create
    if params[:use_python_api]
      # Route through Python API
      @llm_task = ArchiveClient.process_with_llm(
        llm_task_params[:task_type],
        llm_task_params[:prompt],
        llm_task_params[:input],
        llm_task_params[:model_name] || 'claude-3-sonnet',
        llm_task_params[:temperature] || 0.7
      )
      render_success(@llm_task)
    else
      # Direct creation (for manual/testing purposes)
      @llm_task = LlmTask.new(llm_task_params)
      
      if @llm_task.save
        render_success(@llm_task, 'LLM task created successfully')
      else
        render_error(@llm_task.errors.full_messages.join(', '))
      end
    end
  end

  def update
    if @llm_task.update(llm_task_params)
      render_success(@llm_task, 'LLM task updated successfully')
    else
      render_error(@llm_task.errors.full_messages.join(', '))
    end
  end

  def destroy
    @llm_task.destroy
    render_success({}, 'LLM task deleted successfully')
  end

  # Custom action to get statistics
  def stats
    stats = {
      total_tasks: LlmTask.count,
      successful_tasks: LlmTask.successful.count,
      failed_tasks: LlmTask.failed.count,
      pending_tasks: LlmTask.where(result_status: 'pending').count,
      processing_tasks: LlmTask.where(result_status: 'processing').count,
      models_used: LlmTask.distinct.pluck(:model_name),
      task_types: LlmTask.distinct.pluck(:task_type)
    }
    
    render_success(stats)
  end

  private

  def set_llm_task
    @llm_task = LlmTask.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render_not_found('LLM task not found')
  end

  def llm_task_params
    params.require(:llm_task).permit(
      :task_type, :model_name, :temperature, :prompt, :input, :output, :result_status, :metadata
    )
  end
end
