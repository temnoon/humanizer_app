# Media files associated with messages
class MessageMedium < ApplicationRecord
  belongs_to :message
  
  validates :media_type, presence: true, inclusion: { in: %w[image audio video document] }
  validates :content_hash, presence: true, uniqueness: true # Prevent duplicates
  validates :file_path, presence: true
  
  scope :images, -> { where(media_type: 'image') }
  scope :audio, -> { where(media_type: 'audio') }
  scope :videos, -> { where(media_type: 'video') }
  scope :documents, -> { where(media_type: 'document') }
  
  before_validation :calculate_content_hash, if: :file_path_changed?
  before_validation :set_filename_from_path, if: :file_path_changed?
  before_validation :determine_media_type, if: :filename_changed?
  
  # Check if this media file is a duplicate
  def duplicate?
    self.class.exists?(content_hash: content_hash)
  end
  
  # Get file extension
  def file_extension
    File.extname(filename).downcase if filename
  end
  
  # Check if file exists on disk
  def file_exists?
    File.exist?(file_path) if file_path
  end
  
  # Get file size in human readable format
  def human_file_size
    return nil unless file_size
    
    units = %w[B KB MB GB TB]
    size = file_size.to_f
    unit_index = 0
    
    while size >= 1024 && unit_index < units.length - 1
      size /= 1024
      unit_index += 1
    end
    
    "#{size.round(1)} #{units[unit_index]}"
  end
  
  # Image-specific methods
  def image?
    media_type == 'image'
  end
  
  def image_dimensions
    return nil unless image? && file_exists?
    
    # This would integrate with an image processing library
    # For now, return placeholder
    metadata['dimensions'] || 'Unknown'
  end
  
  # Generate thumbnail path for images
  def thumbnail_path
    return nil unless image?
    
    base_path = File.dirname(file_path)
    filename_without_ext = File.basename(file_path, '.*')
    extension = File.extname(file_path)
    
    File.join(base_path, 'thumbnails', "#{filename_without_ext}_thumb#{extension}")
  end
  
  # Create thumbnail if it doesn't exist
  def ensure_thumbnail!
    return unless image? && file_exists?
    
    thumb_path = thumbnail_path
    return thumb_path if File.exist?(thumb_path)
    
    # Create thumbnail directory
    FileUtils.mkdir_p(File.dirname(thumb_path))
    
    # This would integrate with an image processing library like MiniMagick
    # For now, just copy the original (placeholder implementation)
    FileUtils.cp(file_path, thumb_path)
    
    thumb_path
  end
  
  private
  
  def calculate_content_hash
    return unless file_path && File.exist?(file_path)
    
    self.content_hash = Digest::SHA256.file(file_path).hexdigest
    self.file_size = File.size(file_path)
  end
  
  def set_filename_from_path
    return unless file_path
    
    self.filename ||= File.basename(file_path) if filename.blank?
  end
  
  def determine_media_type
    return unless filename
    
    extension = file_extension
    
    self.media_type = case extension
    when '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'
      'image'
    when '.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'
      'audio'  
    when '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv'
      'video'
    else
      'document'
    end
  end
end