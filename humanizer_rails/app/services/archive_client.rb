require 'httparty'

class ArchiveClient
  include HTTParty
  base_uri 'http://localhost:8100'  # Enhanced Lighthouse API port
  
  def self.get_chat_summary(id)
    response = get("/summary/#{id}")
    handle_response(response)
  end

  def self.humanize_text(text, style = 'default')
    response = post('/humanize', {
      body: {
        text: text,
        style: style
      }.to_json,
      headers: { 'Content-Type' => 'application/json' }
    })
    handle_response(response)
  end

  def self.analyze_discourse_posts(posts)
    response = post('/analyze/discourse', {
      body: {
        posts: posts
      }.to_json,
      headers: { 'Content-Type' => 'application/json' }
    })
    handle_response(response)
  end

  def self.get_pipeline_status
    response = get('/status')
    handle_response(response)
  end

  def self.process_with_llm(task_type, prompt, input = nil, model_name = 'claude-3-sonnet', temperature = 0.7)
    # Create LLM task record first
    llm_task = LlmTask.create_from_api_call(
      task_type: task_type,
      model_name: model_name,
      prompt: prompt,
      input: input,
      temperature: temperature
    )

    begin
      llm_task.update!(result_status: 'processing')
      
      response = post('/llm/process', {
        body: {
          task_id: llm_task.id,
          task_type: task_type,
          model_name: model_name,
          prompt: prompt,
          input: input,
          temperature: temperature
        }.to_json,
        headers: { 'Content-Type' => 'application/json' }
      })

      result = handle_response(response)
      
      if result[:success]
        llm_task.complete_with_output!(result[:output], result[:metadata] || {})
      else
        llm_task.fail_with_error!(result[:error] || 'Unknown error')
      end

      llm_task
    rescue => e
      llm_task.fail_with_error!(e.message)
      llm_task
    end
  end

  private

  def self.handle_response(response)
    case response.code
    when 200, 201
      response.parsed_response
    when 404
      { error: 'Resource not found', status: 404 }
    when 500
      { error: 'Internal server error', status: 500 }
    else
      { error: "HTTP #{response.code}: #{response.message}", status: response.code }
    end
  rescue => e
    { error: "Connection error: #{e.message}", status: :connection_error }
  end
end
