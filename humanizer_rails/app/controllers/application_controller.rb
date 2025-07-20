class ApplicationController < ActionController::API
  before_action :set_default_response_format

  private

  def set_default_response_format
    request.format = :json
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
end
