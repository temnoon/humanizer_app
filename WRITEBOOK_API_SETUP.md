# Writebook API Integration Setup

This guide shows how to add the custom API endpoint to your Writebook installation at `writebook.humanizer.com` to enable direct publishing from your local editor.

## Files to Add/Modify

### 1. Add Route (`config/routes.rb`)

Add this line to your Writebook's `config/routes.rb`:

```ruby
# Add near other API routes or at the end
post '/api/import_conversation', to: 'api#import_conversation'
```

### 2. Create API Controller (`app/controllers/api_controller.rb`)

Create a new file `app/controllers/api_controller.rb`:

```ruby
class ApiController < ApplicationController
  # Skip CSRF protection for API endpoints
  skip_before_action :verify_authenticity_token
  
  # Optional: Add authentication if needed
  # before_action :authenticate_api_user!
  
  def import_conversation
    begin
      # Parse the JSON payload from your local editor
      json_data = JSON.parse(request.body.read)
      
      # Validate required fields
      unless json_data['title'].present?
        return render json: { error: 'Title is required' }, status: 400
      end
      
      # Create the book
      book = current_user.books.create!(
        title: json_data['title'],
        public: json_data['is_public'] || false
      )
      
      # Create leaves (pages/sections) from your conversation
      if json_data['leaves'].present?
        json_data['leaves'].each_with_index do |leaf_data, index|
          # Determine the leaf type
          leaf_type = case leaf_data['type']
                     when 'Section'
                       'Section'
                     when 'Picture'
                       'Picture' 
                     else
                       'Page'
                     end
          
          # Create the leaf
          leaf = book.leaves.create!(
            type: leaf_type,
            position: leaf_data['position'] || (index + 1)
          )
          
          # Set content based on leaf type
          case leaf_type
          when 'Section'
            leaf.update!(title: leaf_data['content'])
          when 'Page'
            # Convert content to markdown if needed
            content = leaf_data['content']
            
            # Add metadata as comments if provided
            if leaf_data['metadata'].present?
              metadata = leaf_data['metadata']
              if metadata['original_author'].present?
                content = "<!-- Original Author: #{metadata['original_author']} -->\n#{content}"
              end
              if metadata['original_timestamp'].present?
                content = "<!-- Original Timestamp: #{metadata['original_timestamp']} -->\n#{content}"
              end
            end
            
            leaf.update!(content: content)
          when 'Picture'
            # Handle picture uploads if needed
            leaf.update!(caption: leaf_data['content'])
          end
        end
      end
      
      # Store source metadata if provided
      if json_data['source_metadata'].present?
        # You might want to store this in a custom field or as a comment
        source_info = json_data['source_metadata']
        if source_info['conversation_id'].present?
          book.update!(
            description: "Imported from conversation #{source_info['conversation_id']} on #{source_info['exported_at']}"
          )
        end
      end
      
      # Return success response
      render json: {
        book_id: book.id,
        url: book_url(book),
        message: 'Book created successfully',
        leaves_created: book.leaves.count
      }, status: 201
      
    rescue JSON::ParserError
      render json: { error: 'Invalid JSON format' }, status: 400
    rescue ActiveRecord::RecordInvalid => e
      render json: { error: "Validation failed: #{e.message}" }, status: 422
    rescue StandardError => e
      Rails.logger.error "API Import Error: #{e.message}\n#{e.backtrace.join("\n")}"
      render json: { error: 'Internal server error' }, status: 500
    end
  end
  
  private
  
  def authenticate_api_user!
    # Implement API authentication if needed
    # This could check for API keys, tokens, etc.
    
    # Example simple API key check:
    # api_key = request.headers['Authorization']&.sub('Bearer ', '')
    # unless api_key == Rails.application.credentials.api_key
    #   render json: { error: 'Unauthorized' }, status: 401
    # end
    
    # For now, use the current session user
    unless current_user
      render json: { error: 'Authentication required' }, status: 401
    end
  end
end
```

### 3. Update Application Controller (Optional)

If you need CORS support for cross-origin requests, add this to `app/controllers/application_controller.rb`:

```ruby
class ApplicationController < ActionController::Base
  # ... existing code ...
  
  # Add CORS headers for API endpoints
  before_action :set_cors_headers, if: :api_request?
  
  private
  
  def api_request?
    request.path.start_with?('/api/')
  end
  
  def set_cors_headers
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3100' # Your local dev server
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
  end
end
```

## Testing the API

Once you've added these files to your Writebook installation:

1. **Restart your Writebook server**
2. **Test the endpoint manually**:

```bash
curl -X POST https://writebook.humanizer.com/api/import_conversation \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Import",
    "is_public": false,
    "leaves": [
      {
        "type": "Page",
        "content": "This is a test page from the API",
        "position": 1
      }
    ]
  }'
```

3. **Check your Writebook dashboard** - you should see the new book created

## Security Considerations

- **Authentication**: The current implementation uses session-based auth. Consider adding API key authentication for production.
- **CORS**: Adjust the CORS origins to match your production domains
- **Validation**: Add more robust input validation as needed
- **Rate Limiting**: Consider adding rate limiting to prevent abuse

## Troubleshooting

- **404 Error**: Make sure the route is added correctly and the server is restarted
- **500 Error**: Check the Rails logs for detailed error messages
- **CORS Issues**: Verify the CORS headers are set correctly for your domain
- **Authentication**: Ensure you're logged into Writebook when testing

Once this is set up, your local Writebook Editor will be able to publish directly to your live Writebook installation!