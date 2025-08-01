class CustomGpt < ApplicationRecord
  validates :gizmo_id, presence: true, uniqueness: true
  validates :name, presence: true
  
  scope :by_category, ->(category) { where(category: category) }
  scope :search_name, ->(query) { where("name ILIKE ?", "%#{query}%") }
  
  def self.find_by_gizmo_id(gizmo_id)
    find_by(gizmo_id: gizmo_id)
  end
  
  def display_name
    "#{name}#{creator.present? ? " (by #{creator})" : ''}"
  end
  
  def self.register_gizmo(gizmo_id, name, options = {})
    find_or_create_by(gizmo_id: gizmo_id) do |gpt|
      gpt.name = name
      gpt.description = options[:description]
      gpt.creator = options[:creator]
      gpt.category = options[:category]
      gpt.capabilities = options[:capabilities]
      gpt.created_at_gpt = options[:created_at_gpt]
    end
  end
end
