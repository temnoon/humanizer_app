class WritebooksController < ApplicationController
  before_action :set_writebook, only: [:show, :update, :destroy, :publish, :unpublish, :create_version]

  def index
    @writebooks = Writebook.recent
    @writebooks = @writebooks.by_author(params[:author]) if params[:author].present?
    @writebooks = @writebooks.published if params[:published] == 'true'
    
    render_success(@writebooks.includes(:writebook_sections))
  end

  def show
    render_success(@writebook.as_json(include: :writebook_sections))
  end

  def create
    @writebook = Writebook.new(writebook_params)
    
    if @writebook.save
      render_success(@writebook, 'Writebook created successfully')
    else
      render_error(@writebook.errors.full_messages.join(', '))
    end
  end

  def update
    if @writebook.update(writebook_params)
      render_success(@writebook, 'Writebook updated successfully')
    else
      render_error(@writebook.errors.full_messages.join(', '))
    end
  end

  def destroy
    @writebook.destroy
    render_success({}, 'Writebook deleted successfully')
  end

  def publish
    @writebook.publish!
    render_success(@writebook, 'Writebook published successfully')
  end

  def unpublish
    @writebook.unpublish!
    render_success(@writebook, 'Writebook unpublished successfully')
  end

  def create_version
    new_writebook = @writebook.create_new_version!
    render_success(new_writebook, 'New version created successfully')
  end

  # Get all versions of a writebook
  def versions
    title = params[:title]
    versions = Writebook.where(title: title).order(:version)
    render_success(versions)
  end

  private

  def set_writebook
    @writebook = Writebook.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render_not_found('Writebook not found')
  end

  def writebook_params
    params.require(:writebook).permit(:title, :author, :version, :description)
  end
end
