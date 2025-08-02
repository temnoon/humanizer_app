#!/usr/bin/env python3
"""
Comprehensive LaTeX Normalizer for Joplin KaTeX Compatibility
Handles all common LaTeX syntax issues and normalizes for Joplin rendering
"""

import re
import sys
from typing import Dict, List, Any, Optional

class JoplinLatexNormalizer:
    def __init__(self):
        """Initialize the LaTeX normalizer with KaTeX-specific rules"""
        
        # KaTeX environment compatibility mapping
        self.env_mapping = {
            'align': 'aligned',  # KaTeX prefers aligned over align
            'equation': 'equation',  # Keep equation but will convert to $$ format
            'eqnarray': 'aligned',  # Convert to aligned
            'gather': 'gathered',  # KaTeX equivalent
            'multline': 'aligned',  # Fallback to aligned
        }
        
        # Characters that need special handling in KaTeX
        self.problematic_chars = {
            '"': '"',  # Smart quotes issue
            '"': '"',  # Smart quotes issue  
            ''': "'",  # Smart quote to regular quote
            ''': "'",  # Smart quote to regular quote
        }
        
    def normalize_latex_for_joplin(self, content: str) -> str:
        """
        Comprehensive LaTeX normalization for Joplin's KaTeX renderer
        """
        if not content:
            return content
            
        normalized = content
        
        # Step 1: Fix smart quotes and problematic characters
        normalized = self._fix_smart_quotes(normalized)
        
        # Step 2: Normalize LaTeX environments to KaTeX-compatible ones
        normalized = self._normalize_environments(normalized)
        
        # Step 3: Convert various LaTeX syntaxes to dollar sign format
        normalized = self._normalize_math_delimiters(normalized)
        
        # Step 4: Fix display math blocks (critical for rendering)
        normalized = self._fix_display_math_blocks(normalized)
        
        # Step 5: Clean up double escaping and malformed syntax
        normalized = self._fix_escaping_issues(normalized)
        
        # Step 6: Ensure proper newlines around display math
        normalized = self._ensure_display_math_newlines(normalized)
        
        # Step 7: Fix inline math spacing (without breaking word boundaries)
        normalized = self._fix_inline_math_spacing(normalized)
        
        # Step 8: Clean up internal spaces in math expressions (but preserve external spacing)
        # TEMPORARILY DISABLED to test if this is removing word boundary spacing
        # normalized = self._clean_internal_math_spaces(normalized)
        
        return normalized
        
    def _fix_smart_quotes(self, content: str) -> str:
        """Fix smart quotes that interfere with LaTeX prime notation"""
        result = content
        for bad_char, good_char in self.problematic_chars.items():
            result = result.replace(bad_char, good_char)
        return result
        
    def _normalize_environments(self, content: str) -> str:
        """Convert LaTeX environments to KaTeX-compatible equivalents"""
        result = content
        
        for old_env, new_env in self.env_mapping.items():
            # Handle both starred and non-starred versions
            patterns = [
                (rf'\\begin\{{{old_env}\}}(.*?)\\end\{{{old_env}\}}', new_env),
                (rf'\\begin\{{{old_env}\*\}}(.*?)\\end\{{{old_env}\*\}}', new_env),
            ]
            
            for pattern, replacement_env in patterns:
                def replace_env(match):
                    content_inside = match.group(1)
                    if replacement_env == 'equation':
                        # Convert equation environment to display math
                        return f'$$\n{content_inside.strip()}\n$$'
                    else:
                        # Convert to aligned or other environment
                        return f'$$\n\\begin{{{replacement_env}}}\n{content_inside.strip()}\n\\end{{{replacement_env}}}\n$$'
                
                result = re.sub(pattern, replace_env, result, flags=re.DOTALL)
                
        return result
        
    def _normalize_math_delimiters(self, content: str) -> str:
        """Convert various LaTeX math delimiters to dollar sign format"""
        result = content
        
        # Convert \( inline \) to $inline$
        result = re.sub(r'\\\\?\((.*?)\\\\?\)', r'$\1$', result, flags=re.DOTALL)
        
        # Convert \[ display \] to $$display$$
        result = re.sub(r'\\\\?\[(.*?)\\\\?\]', r'$$\1$$', result, flags=re.DOTALL)
        
        # Convert $$$ display $$$ (triple) to $$display$$
        result = re.sub(r'\$\$\$(.*?)\$\$\$', r'$$\1$$', result, flags=re.DOTALL)
        
        return result
        
    def _fix_display_math_blocks(self, content: str) -> str:
        """Fix display math blocks for proper KaTeX rendering"""
        result = content
        
        # Pattern to match $$...$$
        def fix_display_block(match):
            math_content = match.group(1).strip()
            
            # Remove excessive whitespace but preserve structure
            math_content = re.sub(r'\s+', ' ', math_content)
            math_content = re.sub(r'\s*\\\\\s*', r' \\\\ ', math_content)  # Fix line breaks
            
            # Ensure the block is properly formatted
            return f'$$\n{math_content}\n$$'
        
        # Fix display math blocks
        result = re.sub(r'\$\$(.*?)\$\$', fix_display_block, result, flags=re.DOTALL)
        
        return result
        
    def _fix_inline_math_spacing(self, content: str) -> str:
        """Fix inline math spacing while preserving word boundaries"""
        result = content
        
        # First pass: clean up internal spacing in all inline math
        # Pattern 1: Both leading and trailing spaces: $ content $
        result = re.sub(r'\$\s+([^$]+?)\s+\$', r'$\1$', result)
        
        # Pattern 2: Single spaces on both sides: $ content $  
        result = re.sub(r'\$\s([^$]+?)\s\$', r'$\1$', result)
        
        # Pattern 3: Leading space only: $ content$
        result = re.sub(r'\$\s+([^$]+?)\$', r'$\1$', result)
        
        # Pattern 4: Trailing space only: $content $
        result = re.sub(r'\$([^$]+?)\s+\$', r'$\1$', result)
        
        # Second pass: ensure proper word boundaries
        # Fix spacing around both inline ($...$) and display ($$...$$) math
        
        # Fix spacing around display math ($$...$$) - CRITICAL for Joplin rendering
        # Joplin's KaTeX requires spaces around $$ to recognize display math
        
        # Add space before opening $$ if preceded by non-whitespace
        result = re.sub(r'(\S)\$\$', r'\1 $$', result)
        # Add space after closing $$ if followed by non-whitespace  
        result = re.sub(r'\$\$(\S)', r'$$ \1', result)
        
        # Also ensure $$ blocks are on their own lines for better recognition
        # (KaTeX works better when display math has breathing room)
        result = re.sub(r'(\w)\$\$([^$]+?)\$\$(\w)', r'\1\n\n$$\2$$\n\n\3', result)
        
        # Fix spacing around inline math ($...$)
        # This is critical for Joplin - inline math needs spaces for KaTeX recognition
        
        # Add space before $ if preceded by non-whitespace (any character, not just \w)
        result = re.sub(r'(\S)\$([^$]+?)\$', r'\1 $\2$', result)
        # Add space after $ if followed by non-whitespace  
        result = re.sub(r'\$([^$]+?)\$(\S)', r'$\1$ \2', result)
        
        # Note: punctuation cases are now handled by the \S patterns above
        
        return result
        
    def _fix_escaping_issues(self, content: str) -> str:
        """Fix double escaping and other LaTeX escaping issues"""
        result = content
        
        # Fix double-escaped backslashes in math expressions
        # This is tricky - we need to be in math context
        def fix_math_escaping(match):
            delim = match.group(1)  # $ or $$
            math_content = match.group(2)
            
            # Fix common double-escaping issues
            math_content = re.sub(r'\\\\frac', r'\\frac', math_content)
            math_content = re.sub(r'\\\\partial', r'\\partial', math_content)
            math_content = re.sub(r'\\\\mathcal', r'\\mathcal', math_content)
            math_content = re.sub(r'\\\\int', r'\\int', math_content)
            math_content = re.sub(r'\\\\sum', r'\\sum', math_content)
            math_content = re.sub(r'\\\\prod', r'\\prod', math_content)
            math_content = re.sub(r'\\\\left', r'\\left', math_content)
            math_content = re.sub(r'\\\\right', r'\\right', math_content)
            
            # Fix other common LaTeX commands
            math_content = re.sub(r'\\\\([a-zA-Z]+)', r'\\\1', math_content)
            
            return f'{delim}{math_content}{delim}'
        
        # Apply to both inline and display math
        result = re.sub(r'(\$\$?)(.*?)\1', fix_math_escaping, result, flags=re.DOTALL)
        
        return result
        
    def _ensure_display_math_newlines(self, content: str) -> str:
        """Ensure display math blocks have proper newlines (KaTeX requirement)"""
        result = content
        
        # Ensure display math is on its own lines
        def fix_display_newlines(match):
            before = match.group(1)
            math_content = match.group(2)
            after = match.group(3)
            
            # Add newlines if not present
            before_newline = '\n' if before and not before.endswith('\n') else ''
            after_newline = '\n' if after and not after.startswith('\n') else ''
            
            return f'{before}{before_newline}$$\n{math_content.strip()}\n$${after_newline}{after}'
        
        # Pattern: content$$math$$content
        result = re.sub(r'([^\n])\$\$(.*?)\$\$([^\n])', fix_display_newlines, result, flags=re.DOTALL)
        
        # Clean up excessive newlines
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result
        
    def _fix_edge_case_spacing(self, content: str) -> str:
        """
        Final pass to catch edge cases that main processing missed.
        Very targeted fixes to avoid breaking working expressions.
        """
        result = content
        
        # Step 1: Fix internal spacing issues first (the core problem)
        
        # Pattern 1: $expression $ (trailing space)
        result = re.sub(r'\$([^$]+?) \$', r'$\1$', result)
        
        # Pattern 2: $ expression$ (leading space)  
        result = re.sub(r'\$ ([^$]+?)\$', r'$\1$', result)
        
        # Pattern 3: $ expression $ (both spaces)
        result = re.sub(r'\$ ([^$]+?) \$', r'$\1$', result)
        
        # Pattern 4: Multiple internal spaces
        result = re.sub(r'\$\s{2,}([^$]+?)\s{2,}\$', r'$\1$', result)
        result = re.sub(r'\$\s+([^$]+?)\$', r'$\1$', result)
        result = re.sub(r'\$([^$]+?)\s+\$', r'$\1$', result)
        
        # Step 2: Fix word boundaries (add spaces where needed)
        # DISABLED: These patterns were causing problems by interfering with display math
        # The main _fix_inline_math_spacing method handles word boundaries adequately
        
        # # Add space before math if preceded by word character and no space exists
        # result = re.sub(r'(\w)\$([^$]+?)\$', r'\1 $\2$', result)
        # 
        # # Add space after math if followed by word character and no space exists
        # result = re.sub(r'\$([^$]+?)\$(\w)', r'$\1$ \2', result)
        
        return result

    def _clean_internal_math_spaces(self, content: str) -> str:
        """
        Clean up only truly problematic internal spaces while preserving word boundaries.
        Focus on the main issue: missing spaces around math delimiters.
        """
        result = content
        
        # MINIMAL CLEANUP: Only fix the most obvious OCR artifacts
        # Don't remove spaces that might be providing word boundaries
        
        # 1. Only remove excessive multiple spaces inside math content
        result = re.sub(r'\$([^$]*?)\s{3,}([^$]*?)\$', r'$\1 \2$', result)
        
        # 2. Remove spaces only when clearly internal (surrounded by non-space characters)
        # This pattern only matches spaces that are clearly inside the expression
        result = re.sub(r'\$(\S+)\s+(\S[^$]*?)\s+(\S+)\$', r'$\1 \2 \3$', result)
        
        # Don't remove leading/trailing spaces as they might be for word boundaries
        # This was the main problem - being too aggressive with space removal
        
        return result


# Test function
def test_normalizer():
    """Test the LaTeX normalizer with common problematic cases"""
    normalizer = JoplinLatexNormalizer()
    
    test_cases = [
        # Test case 1: Mixed delimiters
        r'The Lagrangian \( \mathcal{L}(\phi_i, \partial_\mu \phi_i, x^\mu) \) and action \[S = \int \mathcal{L} \, d^4x\]',
        
        # Test case 2: Equation environment
        r'\begin{equation}\psi(x,t) = \sum_n c_n \phi_n(x) e^{-iE_n t/\hbar}\end{equation}',
        
        # Test case 3: Spacing issues
        r'Consider $ q_i $ and $ \dot{q}_i $ variables in time $ t $.',
        
        # Test case 4: Display math with content around it
        r'The equation$$F = ma$$shows force.',
        
        # Test case 5: Double escaping
        r'$\\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi_i)}$',
    ]
    
    print("Testing LaTeX Normalizer:")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input:  {test}")
        result = normalizer.normalize_latex_for_joplin(test)
        print(f"Output: {result}")


if __name__ == '__main__':
    test_normalizer()