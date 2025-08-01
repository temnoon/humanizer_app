require 'rails_helper'

RSpec.describe "Attributes", type: :request do
  describe "GET /index" do
    it "returns http success" do
      get "/attributes/index"
      expect(response).to have_http_status(:success)
    end
  end

end
