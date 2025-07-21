/**
 * LaTeX Utilities for Humanizer Lighthouse
 * 
 * Based on the proven NAB project approach for handling LaTeX rendering
 * when ChatGPT's native LaTeX rendering fails.
 * 
 * Key features:
 * - Placeholder-based system to prevent Markdown corruption
 * - MathJax SVG rendering for cross-platform compatibility
 * - Intelligent LaTeX detection and extraction
 * - Markdown-safe processing order
 */

/**
 * Extracts LaTeX segments from text content and replaces with placeholders
 * 
 * @param {string} text - The input text containing LaTeX notation
 * @returns {Object} Object containing processed text and extracted segments
 */
export function extractLatexSegments(text) {
  if (!text || typeof text !== 'string') {
    return { text: '', segments: [] };
  }
  
  const segments = [];
  let idx = 0;
  
  // Process block LaTeX: \[ ... \] (display math)
  let processedText = text.replace(/\\\[((?:.|\n)+?)\\\]/g, (_, content) => {
    const key = `@@LATEX${idx}@@`;
    segments.push({ key, math: content.trim(), type: 'display' });
    idx++;
    return key;
  });
  
  // Process inline LaTeX: \( ... \) (inline math)
  processedText = processedText.replace(/\\\((.+?)\\\)/g, (_, content) => {
    const key = `@@LATEX${idx}@@`;
    segments.push({ key, math: content.trim(), type: 'inline' });
    idx++;
    return key;
  });
  
  // Process block LaTeX: $$ ... $$ (display math)
  processedText = processedText.replace(/\$\$((?:.|\n)+?)\$\$/g, (_, content) => {
    const key = `@@LATEX${idx}@@`;
    segments.push({ key, math: content.trim(), type: 'display' });
    idx++;
    return key;
  });
  
  // Process inline LaTeX: $ ... $ (but avoid currency symbols)
  // More sophisticated detection to avoid false positives
  processedText = processedText.replace(/(?<![0-9$])\$([^$\n]+?)\$(?![0-9$])/g, (match, content) => {
    // Skip if content looks like currency or plain numbers
    if (/^\s*\d+([.,]\d+)?\s*$/.test(content) || content.includes(',') && !/[a-zA-Z\\]/.test(content)) {
      return match; // Return original, likely currency
    }
    
    // Skip if content is too short or empty
    if (!content.trim() || content.trim().length < 2) {
      return match;
    }
    
    const key = `@@LATEX${idx}@@`;
    segments.push({ key, math: content.trim(), type: 'inline' });
    idx++;
    return key;
  });
  
  return { text: processedText, segments };
}

/**
 * Replaces LaTeX placeholders with properly formatted LaTeX for MathJax
 * 
 * @param {HTMLElement} element - The DOM element containing LaTeX placeholders
 * @param {Array} segments - Array of LaTeX segments with keys and content
 * @returns {boolean} Whether any replacements were made
 */
export function replaceLatexPlaceholders(element, segments) {
  if (!element || !segments || segments.length === 0) {
    return false;
  }
  
  // Create a map for quick lookup
  const segmentMap = {};
  segments.forEach(segment => {
    segmentMap[segment.key] = segment;
  });
  
  // Find all text nodes with placeholders
  const walker = document.createTreeWalker(
    element,
    NodeFilter.SHOW_TEXT,
    { 
      acceptNode: node => node.nodeValue.includes('@@LATEX') ? 
        NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP 
    },
    false
  );
  
  // Collect nodes first (since we'll be modifying the DOM)
  const textNodes = [];
  let currentNode;
  while (currentNode = walker.nextNode()) {
    textNodes.push(currentNode);
  }
  
  // Process each node
  let replacementsCount = 0;
  textNodes.forEach(node => {
    const text = node.nodeValue;
    const placeholderRegex = /@@LATEX(\d+)@@/g;
    
    // Skip if no placeholders
    if (!placeholderRegex.test(text)) return;
    
    // Create document fragment for replacements
    const fragment = document.createDocumentFragment();
    let lastIndex = 0;
    let match;
    
    // Reset regex
    placeholderRegex.lastIndex = 0;
    
    while ((match = placeholderRegex.exec(text)) !== null) {
      const placeholder = match[0];
      
      // Add text before placeholder
      if (match.index > lastIndex) {
        fragment.appendChild(document.createTextNode(text.substring(lastIndex, match.index)));
      }
      
      // Create LaTeX element
      const span = document.createElement('span');
      span.className = 'latex-content';
      span.setAttribute('data-placeholder', placeholder);
      
      // Get segment info
      const segment = segmentMap[placeholder];
      
      if (segment) {
        // Use the actual LaTeX content from the segment
        const math = segment.math;
        
        // Use different delimiters based on type
        if (segment.type === 'display') {
          span.textContent = `\\[${math}\\]`;
          span.classList.add('latex-display');
        } else {
          span.textContent = `\\(${math}\\)`;
          span.classList.add('latex-inline');
        }
      } else {
        // Fallback for orphaned placeholders
        span.textContent = `\\(x^{${match[1]}}\\)`;
        span.classList.add('latex-inline');
      }
      
      // Add span to fragment
      fragment.appendChild(span);
      replacementsCount++;
      
      // Update lastIndex
      lastIndex = match.index + match[0].length;
    }
    
    // Add any remaining text
    if (lastIndex < text.length) {
      fragment.appendChild(document.createTextNode(text.substring(lastIndex)));
    }
    
    // Replace original node with fragment
    if (node.parentNode) {
      node.parentNode.replaceChild(fragment, node);
    }
  });
  
  return replacementsCount > 0;
}

/**
 * Initialize MathJax with optimal configuration for LaTeX rendering
 */
export function initializeMathJax() {
  if (window.MathJax) {
    console.log('MathJax already loaded');
    return Promise.resolve();
  }
  
  return new Promise((resolve, reject) => {
    // Configure MathJax before loading
    window.MathJax = {
      tex: {
        inlineMath: [['\\(', '\\)']],
        displayMath: [['\\[', '\\]']],
        processEscapes: true,
        processEnvironments: true,
        packages: ['base', 'ams', 'newcommand', 'configmacros']
      },
      svg: {
        fontCache: 'global',
        displayAlign: 'left',
        displayIndent: '0'
      },
      options: {
        renderActions: {
          addMenu: [],
          checkLoading: []
        }
      },
      startup: {
        ready: () => {
          console.log('MathJax loaded and ready');
          MathJax.startup.defaultReady();
          resolve();
        }
      }
    };
    
    // Load MathJax script
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
    script.async = true;
    script.onload = () => {
      console.log('MathJax script loaded');
    };
    script.onerror = (error) => {
      console.error('Failed to load MathJax:', error);
      reject(error);
    };
    
    document.head.appendChild(script);
  });
}

/**
 * Render LaTeX in element using MathJax
 * 
 * @param {HTMLElement} element - Element containing LaTeX
 * @param {Array} segments - LaTeX segments (optional, for replacement)
 * @returns {Promise<boolean>} Whether rendering was successful
 */
export async function renderLatexInElement(element, segments = null) {
  if (!element) {
    return false;
  }
  
  try {
    // Initialize MathJax if needed
    if (!window.MathJax) {
      await initializeMathJax();
    }
    
    // Replace placeholders if segments provided
    let replacementsMade = false;
    if (segments) {
      replacementsMade = replaceLatexPlaceholders(element, segments);
    }
    
    // Check if there's any LaTeX content to render
    const latexElements = element.querySelectorAll('.latex-content');
    if (latexElements.length === 0 && !replacementsMade) {
      return false;
    }
    
    // Trigger MathJax rendering
    if (window.MathJax && window.MathJax.typesetPromise) {
      await window.MathJax.typesetPromise([element]);
      console.log(`MathJax rendered ${latexElements.length} LaTeX expressions`);
      return true;
    } else if (window.MathJax && window.MathJax.typeset) {
      window.MathJax.typeset([element]);
      console.log(`MathJax typeset called for ${latexElements.length} expressions`);
      return true;
    }
    
    return false;
  } catch (error) {
    console.error('Error rendering LaTeX:', error);
    return false;
  }
}

/**
 * Process content to handle both Markdown and LaTeX safely
 * 
 * @param {string} content - Raw content with Markdown and LaTeX
 * @returns {Object} Object with markdown-safe content and LaTeX segments
 */
export function processContentForRendering(content) {
  if (!content || typeof content !== 'string') {
    return { content: '', latexSegments: [] };
  }
  
  // Step 1: Extract LaTeX and replace with placeholders
  const { text: markdownSafeContent, segments: latexSegments } = extractLatexSegments(content);
  
  return {
    content: markdownSafeContent,
    latexSegments
  };
}

/**
 * Check if content contains LaTeX expressions
 * 
 * @param {string} content - Content to check
 * @returns {boolean} Whether content contains LaTeX
 */
export function containsLatex(content) {
  if (!content || typeof content !== 'string') {
    return false;
  }
  
  // Check for various LaTeX patterns
  return /(\\\[.*?\\\]|\\\(.*?\\\)|\$\$.*?\$\$|\$[^$\n]+?\$|\\[a-zA-Z]+)/s.test(content);
}

/**
 * Render both Markdown and LaTeX in an element
 * This is the main function to use for complete content rendering
 * 
 * @param {HTMLElement} element - Element to render content in
 * @param {string} content - Raw content with Markdown and LaTeX
 * @param {Function} markdownRenderer - Function to render Markdown (e.g., marked)
 * @returns {Promise<boolean>} Whether rendering was successful
 */
export async function renderMarkdownWithLatex(element, content, markdownRenderer) {
  if (!element || !content) {
    return false;
  }
  
  try {
    // Step 1: Process content to extract LaTeX safely
    const { content: markdownSafeContent, latexSegments } = processContentForRendering(content);
    
    // Step 2: Render Markdown (LaTeX is now safe as placeholders)
    let htmlContent;
    if (markdownRenderer && typeof markdownRenderer === 'function') {
      htmlContent = markdownRenderer(markdownSafeContent);
    } else {
      // Fallback to simple HTML escaping and basic formatting
      htmlContent = markdownSafeContent
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
    }
    
    // Step 3: Set HTML content
    element.innerHTML = htmlContent;
    
    // Step 4: Replace LaTeX placeholders and render
    if (latexSegments.length > 0) {
      await renderLatexInElement(element, latexSegments);
    }
    
    return true;
  } catch (error) {
    console.error('Error rendering Markdown with LaTeX:', error);
    return false;
  }
}

/**
 * Clean up LaTeX rendering artifacts
 * 
 * @param {HTMLElement} element - Element to clean up
 */
export function cleanupLatexRendering(element) {
  if (!element) return;
  
  // Remove any temporary LaTeX elements
  const tempElements = element.querySelectorAll('[data-temp-latex]');
  tempElements.forEach(el => el.remove());
  
  // Clean up MathJax generated elements if needed
  const mathJaxElements = element.querySelectorAll('[data-mathml]');
  mathJaxElements.forEach(el => {
    if (el.style.visibility === 'hidden') {
      el.remove();
    }
  });
}

// Initialize MathJax when module loads
if (typeof window !== 'undefined') {
  // Check if we should auto-initialize MathJax
  if (!window.MathJax) {
    initializeMathJax().catch(error => {
      console.warn('Failed to auto-initialize MathJax:', error);
    });
  }
}

export default {
  extractLatexSegments,
  replaceLatexPlaceholders,
  initializeMathJax,
  renderLatexInElement,
  processContentForRendering,
  containsLatex,
  renderMarkdownWithLatex,
  cleanupLatexRendering
};