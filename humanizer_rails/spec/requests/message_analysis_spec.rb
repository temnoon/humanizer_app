require 'rails_helper'

RSpec.describe "MessageAnalyses", type: :request do
  describe "GET /index" do
    it "returns http success" do
      get "/message_analysis/index"
      expect(response).to have_http_status(:success)
    end
  end

  describe "GET /select_messages" do
    it "returns http success" do
      get "/message_analysis/select_messages"
      expect(response).to have_http_status(:success)
    end
  end

  describe "GET /summarize" do
    it "returns http success" do
      get "/message_analysis/summarize"
      expect(response).to have_http_status(:success)
    end
  end

end
