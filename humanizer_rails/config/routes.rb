Rails.application.routes.draw do
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  get "up" => "rails/health#show", as: :rails_health_check

  # LLM Tasks API
  resources :llm_tasks do
    collection do
      get :stats
    end
  end

  # Writebooks API
  resources :writebooks do
    member do
      patch :publish
      patch :unpublish
      post :create_version
    end
    
    collection do
      get :versions # GET /writebooks/versions?title=SomeTitle
    end

    # Nested sections
    resources :writebook_sections, path: :sections do
      member do
        patch :move_up
        patch :move_down
        post :generate_content
      end
    end
  end

  # Archive/Python API bridge routes
  namespace :api do
    namespace :v1 do
      get 'archive/summary/:id', to: 'archive#summary'
      post 'archive/humanize', to: 'archive#humanize'
      post 'archive/analyze_discourse', to: 'archive#analyze_discourse'
      get 'archive/status', to: 'archive#status'
    end
  end

  # Root route
  root "llm_tasks#index"
end
