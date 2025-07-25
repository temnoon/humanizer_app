import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  BookOpen,
  Save,
  FileText,
  Loader2
} from 'lucide-react';
import { cn } from '../utils';
import AdvancedMarkdownEditor from './AdvancedMarkdownEditor';

const WritebookPageEditor = ({ 
  pageId, 
  onNavigateBack,
  onSave 
}) => {
  const [writebookData, setWritebookData] = useState(null);
  const [pages, setPages] = useState([]);
  const [currentPage, setCurrentPage] = useState(null);
  const [bookTitle, setBookTitle] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [saveStatus, setSaveStatus] = useState(null);

  // Load writebook data
  useEffect(() => {
    const loadData = () => {
      setIsLoading(true);
      
      // First try to load from the editor data (preferred)
      const editorData = localStorage.getItem('writebook_editor_data');
      if (editorData) {
        try {
          const data = JSON.parse(editorData);
          setWritebookData(data.writebookData);
          setPages(data.pages || []);
          setBookTitle(data.writebookData?.title || 'Exported Conversation');
          
          // Find the specific page
          const page = (data.pages || []).find(p => p.id === pageId);
          setCurrentPage(page);
          
          setIsLoading(false);
          return;
        } catch (error) {
          console.warn('Failed to load editor data:', error);
        }
      }
      
      // Fallback: Load from export data
      const exportedData = localStorage.getItem('writebookExportData');
      if (exportedData) {
        try {
          const data = JSON.parse(exportedData);
          setWritebookData(data);
          setPages(data.pages || []);
          setBookTitle(data.title || 'Exported Conversation');
          
          // Find the specific page
          const page = (data.pages || []).find(p => p.id === pageId);
          setCurrentPage(page);
        } catch (error) {
          console.warn('Failed to load export data:', error);
        }
      }
      
      setIsLoading(false);
    };

    loadData();
  }, [pageId]);

  const handleSave = async (content) => {
    if (!currentPage) return;

    setSaveStatus('saving');
    
    try {
      // Update the current page content
      const updatedPage = { ...currentPage, content, lastModified: new Date().toISOString() };
      setCurrentPage(updatedPage);
      
      // Update pages array
      const updatedPages = pages.map(p => p.id === pageId ? updatedPage : p);
      setPages(updatedPages);
      
      // Update writebook data
      const updatedWritebook = {
        ...writebookData,
        title: bookTitle, // Ensure the title is preserved
        pages: updatedPages,
        lastModified: new Date().toISOString()
      };
      setWritebookData(updatedWritebook);
      
      // Save to ALL possible storage locations to ensure persistence and prevent duplicates
      
      // 1. Save to export data (primary)
      localStorage.setItem('writebookExportData', JSON.stringify(updatedWritebook));
      
      // 2. Save to writebook editor data (for current session)
      const editorData = JSON.parse(localStorage.getItem('writebook_editor_data') || '{}');
      editorData.writebookData = updatedWritebook;
      editorData.pages = updatedPages;
      localStorage.setItem('writebook_editor_data', JSON.stringify(editorData));
      
      // 3. CRITICAL: Save to original writebook ID if it exists to prevent duplicates
      if (writebookData?.id) {
        localStorage.setItem(writebookData.id, JSON.stringify(updatedWritebook));
      }
      
      // 4. If this came from a conversation, update that reference too
      if (writebookData?.metadata?.conversation_id) {
        const conversationKey = `writebook_${writebookData.metadata.conversation_id}`;
        const existingData = localStorage.getItem(conversationKey);
        if (existingData) {
          localStorage.setItem(conversationKey, JSON.stringify(updatedWritebook));
        }
      }
      
      // 5. CRITICAL: Also update published books if this writebook is already published
      const publishedBooks = JSON.parse(localStorage.getItem('published_writebooks') || '[]');
      const publishedIndex = publishedBooks.findIndex(book => book.id === writebookData?.id);
      if (publishedIndex >= 0) {
        publishedBooks[publishedIndex] = {
          ...publishedBooks[publishedIndex],
          title: updatedWritebook.title,
          content: { ...updatedWritebook },
          pages: updatedPages,
          updated_at: new Date().toISOString(),
          pages_count: updatedPages.length,
          word_count: updatedPages.reduce((total, page) => total + (page.content?.split(' ').length || 0), 0)
        };
        localStorage.setItem('published_writebooks', JSON.stringify(publishedBooks));
      }
      
      // Call parent save handler if provided
      if (onSave) {
        await onSave(updatedPage, updatedWritebook);
      }
      
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus(null), 2000);
    } catch (error) {
      console.error('Failed to save page:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  const handleContentChange = (newContent) => {
    if (currentPage) {
      setCurrentPage({ ...currentPage, content: newContent });
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-white mx-auto mb-4" />
          <p className="text-white">Loading page...</p>
        </div>
      </div>
    );
  }

  if (!currentPage) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <FileText className="w-16 h-16 text-white mx-auto mb-4 opacity-50" />
          <h1 className="text-2xl font-bold text-white mb-2">Page Not Found</h1>
          <p className="text-gray-300 mb-6">The requested page could not be found.</p>
          <button
            onClick={() => {
              // Clean up editor data after a short delay
              setTimeout(() => {
                localStorage.removeItem('writebook_editor_data');
              }, 100);
              onNavigateBack();
            }}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4 inline mr-2" />
            Back to Writebook
          </button>
        </div>
      </div>
    );
  }

  const pageIndex = pages.findIndex(p => p.id === pageId);
  const pageNumber = pageIndex + 1;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-sm border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => {
                  // Ensure final save before navigating back
                  if (currentPage && currentPage.content) {
                    handleSave(currentPage.content);
                  }
                  
                  // Clean up editor data after a short delay to allow save
                  setTimeout(() => {
                    localStorage.removeItem('writebook_editor_data');
                  }, 100);
                  
                  onNavigateBack();
                }}
                className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Writebook
              </button>
              
              <div className="flex items-center gap-3">
                <BookOpen className="w-6 h-6 text-blue-400" />
                <div>
                  <input
                    type="text"
                    value={bookTitle}
                    onChange={(e) => {
                      const newTitle = e.target.value;
                      setBookTitle(newTitle);
                      
                      // Update writebook data immediately
                      if (writebookData) {
                        const updatedWritebook = {
                          ...writebookData,
                          title: newTitle,
                          lastModified: new Date().toISOString()
                        };
                        setWritebookData(updatedWritebook);
                        
                        // Save to all storage locations to prevent duplicates
                        localStorage.setItem('writebookExportData', JSON.stringify(updatedWritebook));
                        const editorData = JSON.parse(localStorage.getItem('writebook_editor_data') || '{}');
                        editorData.writebookData = updatedWritebook;
                        localStorage.setItem('writebook_editor_data', JSON.stringify(editorData));
                        
                        // CRITICAL: Also update the original writebook location
                        if (writebookData.id) {
                          localStorage.setItem(writebookData.id, JSON.stringify(updatedWritebook));
                        }
                        
                        // CRITICAL: Also update published books if this writebook is already published
                        const publishedBooks = JSON.parse(localStorage.getItem('published_writebooks') || '[]');
                        const publishedIndex = publishedBooks.findIndex(book => book.id === writebookData.id);
                        if (publishedIndex >= 0) {
                          publishedBooks[publishedIndex] = {
                            ...publishedBooks[publishedIndex],
                            title: newTitle,
                            updated_at: new Date().toISOString()
                          };
                          localStorage.setItem('published_writebooks', JSON.stringify(publishedBooks));
                        }
                      }
                    }}
                    className="text-xl font-bold text-white bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-400 rounded px-2 py-1 min-w-0"
                    placeholder="Enter book title..."
                  />
                  <p className="text-sm text-gray-300">
                    {currentPage.type === 'section' ? 'Section' : 'Page'} {pageNumber} of {pages.length}
                  </p>
                </div>
              </div>
            </div>

            {/* Save Status */}
            {saveStatus && (
              <div className="flex items-center gap-2 text-sm">
                {saveStatus === 'saving' && (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                    <span className="text-blue-400">Saving...</span>
                  </>
                )}
                {saveStatus === 'saved' && (
                  <>
                    <Save className="w-4 h-4 text-green-400" />
                    <span className="text-green-400">Saved</span>
                  </>
                )}
                {saveStatus === 'error' && (
                  <span className="text-red-400">Save failed</span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Full-Screen Editor */}
      <div className="max-w-7xl mx-auto p-6">
        <div className="h-[calc(100vh-12rem)]">
          <AdvancedMarkdownEditor
            content={currentPage.content || ''}
            title={currentPage.title || `Page ${pageNumber}`}
            onChange={handleContentChange}
            onSave={handleSave}
            autoSave={true}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
};

export default WritebookPageEditor;