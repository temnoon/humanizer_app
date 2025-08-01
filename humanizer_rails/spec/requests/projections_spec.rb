require 'rails_helper'

RSpec.describe "Projections", type: :request do
  describe "GET /index" do
    it "returns http success" do
      get "/projections/index"
      expect(response).to have_http_status(:success)
    end
  end

  describe "GET /new" do
    it "returns http success" do
      get "/projections/new"
      expect(response).to have_http_status(:success)
    end
  end

end
