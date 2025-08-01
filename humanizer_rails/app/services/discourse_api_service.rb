# Discourse API Service - Integration with Discourse platform
class DiscourseApiService
  include HTTParty
  
  BASE_URL = Rails.application.config.discourse_base_url || ENV['DISCOURSE_BASE_URL'] || 'http://localhost:4200'
  API_KEY = Rails.application.config.discourse_api_key || ENV['DISCOURSE_API_KEY']
  API_USERNAME = Rails.application.config.discourse_api_username || ENV['DISCOURSE_API_USERNAME'] || 'system'
  
  base_uri BASE_URL
  headers 'Api-Key' => API_KEY, 'Api-Username' => API_USERNAME, 'Content-Type' => 'application/json'
  
  class DiscourseApiError < StandardError; end
  
  def initialize
    raise DiscourseApiError, "Discourse API key not configured" unless API_KEY.present?
    raise DiscourseApiError, "Discourse base URL not configured" unless BASE_URL.present?
  end
  
  # Topic management
  def create_topic(title:, raw:, category: nil, tags: [])
    payload = {
      title: title,
      raw: raw,
      category: category,
      tags: tags.join(',')
    }.compact
    
    response = self.class.post('/posts.json', body: payload.to_json)
    handle_response(response)
  end
  
  def update_post(post_id, raw:)
    payload = { post: { raw: raw } }
    response = self.class.put("/posts/#{post_id}.json", body: payload.to_json)
    handle_response(response)
  end
  
  def get_topic(topic_id)
    response = self.class.get("/t/#{topic_id}.json")
    handle_response(response)
  end
  
  def delete_topic(topic_id)
    response = self.class.delete("/t/#{topic_id}.json")
    handle_response(response)
  end
  
  # Category management
  def get_categories
    response = self.class.get('/categories.json')
    handle_response(response)['category_list']['categories']
  end
  
  def create_category(name:, description: nil, color: '0088CC', parent_category_id: nil)
    payload = {
      name: name,
      color: color,
      description: description,
      parent_category_id: parent_category_id
    }.compact
    
    response = self.class.post('/categories.json', body: payload.to_json)
    handle_response(response)
  end
  
  # User management
  def get_user(username)
    response = self.class.get("/users/#{username}.json")
    handle_response(response)
  end
  
  def create_user(name:, username:, email:, password:)
    payload = {
      name: name,
      username: username,
      email: email,
      password: password,
      active: true
    }
    
    response = self.class.post('/users.json', body: payload.to_json)
    handle_response(response)
  end
  
  # Search functionality
  def search(query, options = {})
    params = {
      q: query,
      page: options[:page] || 1,
      order: options[:order] || 'latest'
    }
    
    response = self.class.get('/search.json', query: params)
    handle_response(response)
  end
  
  # Webhook management (for receiving Discourse events)
  def create_webhook(payload_url:, event_types: ['topic_created', 'post_created'])
    payload = {
      web_hook: {
        payload_url: payload_url,
        content_type: 1, # JSON
        active: true,
        web_hook_event_types: event_types.map { |type|
          { name: type }
        }
      }
    }
    
    response = self.class.post('/admin/api/web_hooks.json', body: payload.to_json)
    handle_response(response)
  end
  
  # Analytics
  def get_topic_stats(topic_id)
    response = self.class.get("/t/#{topic_id}/posts.json")
    topic_data = handle_response(response)
    
    {
      posts_count: topic_data['posts_count'],
      views: topic_data['views'],
      like_count: topic_data['posts']&.sum { |post| post['actions_summary']&.find { |a| a['id'] == 2 }&.dig('count') || 0 },
      participants: topic_data['details']['participants']&.count || 0
    }
  rescue => e
    Rails.logger.error "Failed to get topic stats: #{e.message}"
    {}
  end
  
  # Site settings and configuration
  def get_site_info
    response = self.class.get('/site.json')
    handle_response(response)
  end
  
  def test_connection
    begin
      site_info = get_site_info
      {
        connected: true,
        site_title: site_info.dig('title'),
        version: site_info.dig('version'),
        user_count: site_info.dig('user_count')
      }
    rescue => e
      {
        connected: false,
        error: e.message
      }
    end
  end
  
  private
  
  def handle_response(response)
    case response.code
    when 200, 201
      response.parsed_response
    when 422
      errors = response.parsed_response['errors'] || ['Invalid request']
      raise DiscourseApiError, "Validation error: #{errors.join(', ')}"
    when 403
      raise DiscourseApiError, "Access forbidden - check API key and permissions"
    when 404
      raise DiscourseApiError, "Resource not found"
    when 429
      raise DiscourseApiError, "Rate limit exceeded"
    else
      raise DiscourseApiError, "HTTP #{response.code}: #{response.message}"
    end
  end
end