import React, { useState, useEffect } from 'react';
import { Image as ImageIcon, MessageSquare, Calendar, ExternalLink, Search, Filter, Grid, List } from 'lucide-react';

const ImageGallery = () => {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'with_message', 'orphaned'
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    loadImages();
  }, [page, searchTerm, filterType]);

  const loadImages = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/conversations/images?limit=50&offset=${page * 50}&search=${encodeURIComponent(searchTerm)}&filter=${filterType}`);
      
      if (!response.ok) {
        throw new Error('Failed to load images');
      }
      
      const data = await response.json();
      
      if (page === 0) {
        setImages(data.images || []);
      } else {
        setImages(prev => [...prev, ...(data.images || [])]);
      }
      
      setHasMore(data.has_more || false);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
    setPage(0);
    setImages([]);
  };

  const handleFilter = (filter) => {
    setFilterType(filter);
    setPage(0);
    setImages([]);
  };

  const loadMore = () => {
    if (hasMore && !loading) {
      setPage(prev => prev + 1);
    }
  };

  const ImageModal = ({ image, onClose }) => {
    if (!image) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto">
          <div className="p-4 border-b">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-semibold">{image.filename}</h3>
                <p className="text-sm text-gray-600">{new Date(image.created_at).toLocaleDateString()}</p>
              </div>
              <button
                onClick={onClose}
                className="text-gray-500 hover:text-gray-700 text-xl font-bold"
              >
                ×
              </button>
            </div>
          </div>
          
          <div className="p-4">
            <img
              src={`/api/conversations/media/${image.id}`}
              alt={image.filename}
              className="max-w-full max-h-96 mx-auto mb-4"
            />
            
            {image.conversation_title && (
              <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <MessageSquare className="h-4 w-4 text-blue-600" />
                  <span className="font-semibold text-blue-900">From Conversation:</span>
                </div>
                <p className="text-blue-800">{image.conversation_title}</p>
                {image.message_content && (
                  <p className="text-sm text-gray-600 mt-2">{image.message_content}</p>
                )}
              </div>
            )}
            
            <div className="flex gap-2">
              {image.conversation_id && (
                <a
                  href={`/conversations/${image.conversation_id}`}
                  className="flex items-center gap-1 bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                >
                  <ExternalLink className="h-3 w-3" />
                  View Conversation
                </a>
              )}
              {image.message_id && (
                <a
                  href={`/conversations/${image.conversation_id}#message-${image.message_id}`}
                  className="flex items-center gap-1 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                >
                  <MessageSquare className="h-3 w-3" />
                  View Message
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const GridView = () => (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
      {images.map((image) => (
        <div
          key={image.id}
          className="group relative bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
          onClick={() => setSelectedImage(image)}
        >
          <div className="aspect-square overflow-hidden rounded-t-lg">
            <img
              src={`/api/conversations/media/${image.id}/thumbnail`}
              alt={image.filename}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform"
              onError={(e) => {
                // Fallback to full image if thumbnail fails
                e.target.src = `/api/conversations/media/${image.id}`;
              }}
            />
          </div>
          
          <div className="p-2">
            <p className="text-xs font-medium text-gray-900 truncate">{image.filename}</p>
            {image.conversation_title && (
              <p className="text-xs text-gray-600 truncate mt-1">{image.conversation_title}</p>
            )}
            <p className="text-xs text-gray-500 mt-1">
              {new Date(image.created_at).toLocaleDateString()}
            </p>
          </div>
          
          {image.message_id && (
            <div className="absolute top-2 right-2 bg-blue-600 text-white rounded-full p-1">
              <MessageSquare className="h-3 w-3" />
            </div>
          )}
        </div>
      ))}
    </div>
  );

  const ListView = () => (
    <div className="space-y-4">
      {images.map((image) => (
        <div
          key={image.id}
          className="bg-white rounded-lg shadow p-4 flex gap-4 hover:shadow-lg transition-shadow cursor-pointer"
          onClick={() => setSelectedImage(image)}
        >
          <div className="w-24 h-24 flex-shrink-0 overflow-hidden rounded-lg">
            <img
              src={`/api/conversations/media/${image.id}/thumbnail`}
              alt={image.filename}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.src = `/api/conversations/media/${image.id}`;
              }}
            />
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-gray-900 truncate">{image.filename}</h3>
              <span className="text-sm text-gray-500 flex-shrink-0 ml-2">
                {new Date(image.created_at).toLocaleDateString()}
              </span>
            </div>
            
            {image.conversation_title && (
              <div className="mb-2">
                <p className="text-sm text-blue-600 font-medium">{image.conversation_title}</p>
                {image.message_content && (
                  <p className="text-sm text-gray-600 truncate">{image.message_content}</p>
                )}
              </div>
            )}
            
            <div className="flex gap-2">
              {image.conversation_id && (
                <span className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                  <MessageSquare className="h-3 w-3" />
                  Conversation
                </span>
              )}
              {image.message_id && (
                <span className="inline-flex items-center gap-1 bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                  <MessageSquare className="h-3 w-3" />
                  Message
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="p-6 border-b">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <ImageIcon className="h-8 w-8 text-purple-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Image Gallery</h1>
                <p className="text-gray-600">Images from imported conversations</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-purple-100 text-purple-700' : 'text-gray-500 hover:bg-gray-100'}`}
              >
                <Grid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-purple-100 text-purple-700' : 'text-gray-500 hover:bg-gray-100'}`}
              >
                <List className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Search and Filter */}
          <div className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search images by filename or conversation..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <select
                value={filterType}
                onChange={(e) => handleFilter(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="all">All Images</option>
                <option value="with_message">Linked to Messages</option>
                <option value="orphaned">Conversation Only</option>
              </select>
            </div>
          </div>

          {/* Stats */}
          <div className="flex gap-6 text-sm text-gray-600">
            <span>{images.length} images loaded</span>
            {hasMore && <span>More available</span>}
          </div>
        </div>

        <div className="p-6">
          {loading && images.length === 0 ? (
            <div className="text-center py-12">
              <ImageIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Loading images...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={() => {
                  setError('');
                  loadImages();
                }}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
              >
                Try Again
              </button>
            </div>
          ) : images.length === 0 ? (
            <div className="text-center py-12">
              <ImageIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No images found</p>
              <p className="text-sm text-gray-500 mt-2">
                Import conversations with media files to see them here
              </p>
            </div>
          ) : (
            <>
              {viewMode === 'grid' ? <GridView /> : <ListView />}
              
              {hasMore && (
                <div className="text-center mt-8">
                  <button
                    onClick={loadMore}
                    disabled={loading}
                    className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
                  >
                    {loading ? 'Loading...' : 'Load More'}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Image Modal */}
      <ImageModal
        image={selectedImage}
        onClose={() => setSelectedImage(null)}
      />
    </div>
  );
};

export default ImageGallery;