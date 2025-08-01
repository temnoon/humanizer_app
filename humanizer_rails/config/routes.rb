Rails.application.routes.draw do
  # Message Analysis Routes
  resources :message_analysis, only: [:index] do
    collection do
      get 'select_messages/:conversation_id', to: 'message_analysis#select_messages', as: 'select_messages'
      post 'summarize', to: 'message_analysis#summarize', as: 'summarize'
      get 'show_summary/:conversation_id/:analysis_id', to: 'message_analysis#show_summary', as: 'show_summary'
    end
  end
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  get "up" => "rails/health#show", as: :rails_health_check

  # LLM Tasks API
  resources :llm_tasks do
    collection do
      get :stats
    end
  end

  # Conversations API - Unified conversation management
  resources :conversations do
    member do
      post :transform
      post :export_to_book
      get :new_transformation
      get :new_book
      get :preview, defaults: { format: :json }
    end
    
    collection do
      post :import
      get :search
      get :stats
    end
  end

  # Writebooks API - Enhanced with allegory engine integration
  resources :writebooks do
    member do
      patch :publish
      patch :unpublish
      post :create_version
      post :transform
      get :export
    end
    
    collection do
      get :versions # GET /writebooks/versions?title=SomeTitle
      post :from_conversation
    end

    # Nested sections
    resources :writebook_sections, path: :sections do
      member do
        patch :move_up
        patch :move_down
        post :generate_content
        post :transform
        post :sync_with_source
      end
    end
  end

  # Archive/Python API bridge routes
  namespace :api do
    namespace :v1 do
      # Legacy archive routes
      get 'archive/summary/:id', to: 'archive#summary'
      post 'archive/humanize', to: 'archive#humanize'
      post 'archive/analyze_discourse', to: 'archive#analyze_discourse'
      get 'archive/status', to: 'archive#status'
      
      # Unified Archive routes
      resources :unified_archive, only: [:index, :show] do
        member do
          get :thread
          post :enhance
        end
        
        collection do
          get :search
          get :statistics
          get :sources
          get :authors
          get :timeline
          post :import
          get :export
        end
      end
    end
  end

  # GUI Routes for Allegory Engine Interface
  root "home#index"
  
  # Additional GUI routes
  get '/projections', to: 'projections#index'
  get '/projections/new', to: 'projections#new', as: 'new_projection'
  
  # Attribute extraction and editing interface
  get '/attributes', to: 'attributes#index'
  post '/attributes/analyze', to: 'attributes#analyze'
  post '/attributes/preview', to: 'attributes#preview_transformation'
  post '/attributes/save_preset', to: 'attributes#save_preset'
  
  get '/conversations/import/new', to: 'conversations#new_import', as: 'new_conversation_import'
  get '/conversations/stats', to: 'conversations#stats'
  
  # Discourse Integration API
  resources :discourse_posts do
    member do
      post :publish
      post :sync
      get :preview
    end
    
    collection do
      post :from_conversation
      post :from_writebook
      get :categories
      get :connection_test
      post :sync_all
      get :analytics
    end
  end
  
  # Discourse Webhook Integration
  namespace :discourse_webhooks do
    post :topic_created
    post :post_created
    post :post_edited
    post :topic_destroyed
    post :like_created
    post :handle_webhook
  end
end
