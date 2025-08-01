require_relative "boot"

require "rails/all"

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module HumanizerRails
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 7.2

    # Configuration for the application, engines, and railties goes here.
    #
    # These settings can be overridden in specific environments using the files
    # in config/environments, which are processed later.
    #
    # config.time_zone = "Central Time (US & Canada)"
    # config.eager_load_paths << Rails.root.join("extras")

    # Enable full Rails stack for GUI frontend
    # config.api_only = true  # Disabled for GUI support

    # CORS configuration
    config.middleware.insert_before 0, Rack::Cors do
      allow do
        origins 'localhost:3000', 'localhost:5173', '127.0.0.1:3000', '127.0.0.1:5173'
        resource '*',
          headers: :any,
          methods: [:get, :post, :put, :patch, :delete, :options, :head],
          credentials: true
      end
    end

    # Discourse Integration Configuration
    config.discourse_base_url = ENV['DISCOURSE_BASE_URL'] || 'http://localhost:4200'
    config.discourse_api_key = ENV['DISCOURSE_API_KEY']
    config.discourse_api_username = ENV['DISCOURSE_API_USERNAME'] || 'system'
    config.discourse_webhook_secret = ENV['DISCOURSE_WEBHOOK_SECRET']

    # Archive API Configuration  
    config.archive_api_url = ENV['ARCHIVE_API_URL'] || 'http://localhost:7200'
    config.lpe_api_url = ENV['LPE_API_URL'] || 'http://localhost:7201'
    
    # Python backend configuration
    config.lighthouse_api_url = ENV['LIGHTHOUSE_API_URL'] || 'http://localhost:8100'
  end
end
