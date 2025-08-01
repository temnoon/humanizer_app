class Writebook < ApplicationRecord
  has_many :writebook_sections, dependent: :destroy
  has_many :discourse_posts, dependent: :destroy
  has_many :llm_tasks, dependent: :nullify
  has_many :source_conversations, through: :writebook_sections
  has_many :source_messages, through: :writebook_sections

  validates :title, presence: true
  validates :version, presence: true
  validates :genre, inclusion: { in: %w[fiction non_fiction technical philosophical narrative] }, allow_blank: true
  validates :target_audience, inclusion: { in: %w[general academic professional children young_adult] }, allow_blank: true

  scope :recent, -> { order(created_at: :desc) }
  scope :by_author, ->(author) { where(author: author) }
  scope :published, -> { where.not(published_at: nil) }
  scope :by_genre, ->(genre) { where(genre: genre) }
  scope :by_audience, ->(audience) { where(target_audience: audience) }

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

  # Create book from conversation
  def self.create_from_conversation(conversation, options = {})
    book = create!(
      title: options[:title] || "Book: #{conversation.title}",
      author: options[:author] || 'Generated from Conversation',
      description: options[:description] || "Generated from conversation: #{conversation.title}",
      genre: options[:genre] || 'narrative',
      target_audience: options[:target_audience] || 'general',
      allegory_settings: options[:allegory_settings] || {}
    )

    # Convert conversation messages to book sections
    sections = conversation.to_book_sections(book, options.fetch(:section_options, {}))
    sections.each(&:save!)
    
    book.reload
  end

  # Apply allegory transformation to entire book
  def apply_allegory_transformation(attributes = {})
    # Create new version with transformed content
    transformed_book = create_new_version!
    transformed_book.update!(
      title: "#{title} (#{attributes[:style]} transformation)",
      allegory_settings: allegory_settings.merge(
        transformation: attributes,
        transformed_at: Time.current,
        original_book_id: id
      )
    )

    # Transform all sections
    writebook_sections.each do |section|
      if section.source_message
        # Transform using message's allegory transformation
        transformed_message = section.source_message.apply_allegory_transformation(attributes)
        section.dup.tap do |new_section|
          new_section.writebook = transformed_book
          new_section.content = transformed_message.content
          new_section.allegory_attributes = new_section.allegory_attributes.merge(attributes)
          new_section.save!
        end
      else
        # Direct content transformation
        allegory_service = AllegoryTransformationService.new(
          namespace: attributes[:namespace] || 'lamish-galaxy',
          persona: attributes[:persona] || 'temnoon',
          style: attributes[:style] || 'contemplative'
        )
        
        transformed_content = allegory_service.transform_content(
          content: section.content,
          role: 'section',
          context: book_context
        )
        
        section.dup.tap do |new_section|
          new_section.writebook = transformed_book
          new_section.content = transformed_content
          new_section.allegory_attributes = new_section.allegory_attributes.merge(attributes)
          new_section.save!
        end
      end
    end

    transformed_book
  end

  # Export to various formats
  def export_to_format(format, options = {})
    case format.to_s
    when 'pdf'
      export_to_pdf(options)
    when 'writebook'
      export_to_writebook(options)
    when 'markdown'
      export_to_markdown(options)
    when 'epub'
      export_to_epub(options)
    else
      raise ArgumentError, "Unsupported format: #{format}"
    end
  end

  def book_context
    {
      title: title,
      author: author,
      genre: genre,
      target_audience: target_audience,
      section_count: writebook_sections.count,
      total_words: total_word_count,
      source_conversations: source_conversations.pluck(:title).uniq
    }
  end

  private

  def export_to_pdf(options = {})
    # Integration point for PDF generation
    # This would use a library like Prawn or wkhtmltopdf
    PdfExportService.new(self, options).generate
  end

  def export_to_writebook(options = {})
    # Export to actual WriteBooks format
    # This preserves the structure for WriteBooks compatibility
    WritebookExportService.new(self, options).generate
  end

  def export_to_markdown(options = {})
    # Generate markdown version
    sections_markdown = writebook_sections.ordered.map do |section|
      "## #{section.title}\n\n#{section.content}\n\n"
    end

    "# #{title}\n\n**Author**: #{author}\n\n#{description}\n\n#{sections_markdown.join}"
  end

  def export_to_epub(options = {})
    # Integration point for EPUB generation
    EpubExportService.new(self, options).generate
  end
  
  # Discourse integration methods
  def to_discourse_content
    # Format writebook content for Discourse posting
    content_parts = []
    
    # Add book header
    content_parts << "# #{title}"
    content_parts << "*by #{author}*\n" if author.present?
    
    # Add description
    if description.present?
      content_parts << "## Description\n#{description}\n"
    end
    
    # Add key sections (limit to prevent overwhelming posts)
    key_sections = writebook_sections.ordered.limit(5)
    
    if key_sections.any?
      content_parts << "## Preview\n"
      
      key_sections.each do |section|
        content_parts << "### #{section.title}\n"
        
        # Truncate very long sections
        content = section.content.length > 800 ? 
          "#{section.content[0..800]}..." : section.content
          
        content_parts << "#{content}\n"
      end
      
      # Note if there are more sections
      if writebook_sections.count > 5
        remaining = writebook_sections.count - 5
        content_parts << "*... and #{remaining} more sections*\n"
      end
    end
    
    # Add metadata
    content_parts << "\n---\n"
    content_parts << "*#{sections_count} sections, #{total_word_count} words total*"
    content_parts << "*Genre: #{genre}*" if genre.present?
    content_parts << "*Target Audience: #{target_audience}*" if target_audience.present?
    
    content_parts.join("\n")
  end
  
  def can_publish_to_discourse?
    writebook_sections.any? && title.present?
  end
end
