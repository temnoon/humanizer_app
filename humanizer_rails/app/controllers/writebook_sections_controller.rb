class WritebookSectionsController < ApplicationController
  before_action :set_writebook
  before_action :set_section, only: [:show, :update, :destroy, :move_up, :move_down, :generate_content]

  def index
    @sections = @writebook.writebook_sections.ordered
    render_success(@sections)
  end

  def show
    render_success(@section)
  end

  def create
    @section = @writebook.writebook_sections.build(section_params)
    
    if @section.save
      render_success(@section, 'Section created successfully')
    else
      render_error(@section.errors.full_messages.join(', '))
    end
  end

  def update
    if @section.update(section_params)
      render_success(@section, 'Section updated successfully')
    else
      render_error(@section.errors.full_messages.join(', '))
    end
  end

  def destroy
    @section.destroy
    render_success({}, 'Section deleted successfully')
  end

  def move_up
    @section.move_up!
    render_success(@section, 'Section moved up')
  end

  def move_down
    @section.move_down!
    render_success(@section, 'Section moved down')
  end

  def generate_content
    prompt = params[:prompt] || "Generate content for section '#{@section.title}'"
    model_name = params[:model_name] || 'claude-3-sonnet'
    temperature = params[:temperature] || 0.7

    llm_task = @section.generate_content!(prompt, model_name, temperature)
    
    render_success({
      section: @section,
      llm_task: llm_task
    }, 'Content generation started')
  end

  private

  def set_writebook
    @writebook = Writebook.find(params[:writebook_id])
  rescue ActiveRecord::RecordNotFound
    render_not_found('Writebook not found')
  end

  def set_section
    @section = @writebook.writebook_sections.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render_not_found('Section not found')
  end

  def section_params
    params.require(:writebook_section).permit(:title, :content, :linked_archive_id, :projection_notes)
  end
end
