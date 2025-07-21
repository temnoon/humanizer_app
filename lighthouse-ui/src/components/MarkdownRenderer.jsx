import React, { useEffect, useRef, useState } from 'react';
import { marked } from 'marked';
import { renderMarkdownWithLatex, containsLatex, cleanupLatexRendering } from '../utils/latexUtils';

/**
 * MarkdownRenderer Component
 * 
 * A React component that safely renders both Markdown and LaTeX content.
 * Based on the proven NAB project approach for handling complex content
 * where Markdown processing can corrupt LaTeX and vice versa.
 * 
 * Features:
 * - Placeholder-based LaTeX extraction before Markdown processing
 * - MathJax integration for LaTeX rendering
 * - Support for tables, code blocks, and all standard Markdown features
 * - Automatic LaTeX detection and processing
 */

const MarkdownRenderer = ({ 
  content, 
  className = '', 
  enableTables = true,
  enableCodeHighlighting = true,
  onRenderComplete = null 
}) => {
  const containerRef = useRef(null);
  const [isRendering, setIsRendering] = useState(false);
  const [hasLatex, setHasLatex] = useState(false);
  const [renderError, setRenderError] = useState(null);

  // Configure marked for GitHub Flavored Markdown
  const configureMarked = () => {
    marked.setOptions({
      gfm: true,
      breaks: true,
      tables: enableTables,
      sanitize: false, // We'll handle sanitization ourselves
      smartLists: true,
      smartypants: true
    });

    // Custom renderer for tables to add styling
    const renderer = new marked.Renderer();
    
    // Enhanced table rendering
    renderer.table = function(header, body) {
      return `<table class="markdown-table"><thead>${header}</thead><tbody>${body}</tbody></table>`;
    };
    
    renderer.tablecell = function(content, flags) {
      const type = flags.header ? 'th' : 'td';
      const align = flags.align ? ` style="text-align: ${flags.align}"` : '';
      return `<${type}${align}>${content}</${type}>`;
    };
    
    // Enhanced code block rendering
    renderer.code = function(code, language) {
      const lang = language ? ` class="language-${language}"` : '';
      return `<pre class="markdown-code-block"><code${lang}>${code}</code></pre>`;
    };
    
    // Enhanced inline code rendering
    renderer.codespan = function(code) {
      return `<code class="markdown-inline-code">${code}</code>`;
    };
    
    // Enhanced blockquote rendering
    renderer.blockquote = function(quote) {
      return `<blockquote class="markdown-blockquote">${quote}</blockquote>`;
    };
    
    marked.use({ renderer });
  };

  // Render content when it changes
  useEffect(() => {
    if (!content || !containerRef.current) {
      return;
    }

    const renderContent = async () => {
      setIsRendering(true);
      setRenderError(null);
      
      try {
        // Configure marked
        configureMarked();
        
        // Check if content has LaTeX
        const contentHasLatex = containsLatex(content);
        setHasLatex(contentHasLatex);
        
        // Render content with both Markdown and LaTeX support
        const success = await renderMarkdownWithLatex(
          containerRef.current,
          content,
          (markdownContent) => marked(markdownContent)
        );
        
        if (!success) {
          throw new Error('Failed to render content');
        }
        
        // Call completion callback
        if (onRenderComplete) {
          onRenderComplete({
            hasLatex: contentHasLatex,
            element: containerRef.current
          });
        }
        
      } catch (error) {
        console.error('Error rendering content:', error);
        setRenderError(error.message);
        
        // Fallback to plain text rendering
        if (containerRef.current) {
          containerRef.current.textContent = content;
        }
      } finally {
        setIsRendering(false);
      }
    };

    renderContent();
  }, [content, enableTables, enableCodeHighlighting]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (containerRef.current) {
        cleanupLatexRendering(containerRef.current);
      }
    };
  }, []);

  return (
    <div 
      ref={containerRef}
      className={`markdown-content ${className} ${hasLatex ? 'has-latex' : ''} ${isRendering ? 'rendering' : ''}`}
      style={{
        opacity: isRendering ? 0.7 : 1,
        transition: 'opacity 0.2s ease'
      }}
    >
      {/* Content will be rendered here */}
      {isRendering && (
        <div className="text-gray-500 text-sm">
          Rendering content{hasLatex ? ' with LaTeX' : ''}...
        </div>
      )}
      {renderError && (
        <div className="text-red-500 text-sm border border-red-300 bg-red-50 p-2 rounded">
          <strong>Rendering Error:</strong> {renderError}
        </div>
      )}
    </div>
  );
};

export default MarkdownRenderer;