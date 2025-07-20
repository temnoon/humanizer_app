class Writebook < ApplicationRecord
  has_many :writebook_sections, dependent: :destroy
  has_many :llm_tasks, dependent: :nullify

  validates :title, presence: true
  validates :version, presence: true

  scope :recent, -> { order(created_at: :desc) }
  scope :by_author, ->(author) { where(author: author) }
  scope :published, -> { where.not(published_at: nil) }

  # Helper methods
  def published?
    published_at.present?
  end

  def publish!
    update!(published_at: Time.current)
  end

  def unpublish!
    update!(published_at: nil)
  end

  def sections_count
    writebook_sections.count
  end

  def total_word_count
    writebook_sections.sum { |section| section.content&.split&.length || 0 }
  end

  # Generate a new version
  def create_new_version!
    new_version = version.to_f + 0.1
    self.class.create!(
      title: title,
      author: author,
      version: new_version.to_s,
      description: description,
      writebook_sections: writebook_sections.map(&:dup)
    )
  end

  # Get latest version of this writebook
  def self.latest_version(title)
    where(title: title).order(:version).last
  end

  # Get all versions of this writebook
  def all_versions
    self.class.where(title: title).order(:version)
  end
end
