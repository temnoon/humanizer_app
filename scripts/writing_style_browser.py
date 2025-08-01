#!/usr/bin/env python3
"""
Writing Style Analysis Browser
Interactive tool to explore your personal writing style analysis results
"""

import json
import argparse
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics

class WritingStyleBrowser:
    """Interactive browser for writing style analysis results"""
    
    def __init__(self, analysis_dir: str = "personal_writing_analysis"):
        self.analysis_dir = analysis_dir
        self.available_analyses = self._find_available_analyses()
        
        if not self.available_analyses:
            print("❌ No writing style analyses found!")
            print(f"   Looking in: {os.path.abspath(analysis_dir)}")
            return
        
        print("📊 Writing Style Analysis Browser")
        print("=" * 40)
        print(f"Found {len(self.available_analyses)} analysis sessions")
    
    def _find_available_analyses(self) -> List[Dict[str, str]]:
        """Find all available analysis sessions"""
        analyses = []
        
        if not os.path.exists(self.analysis_dir):
            return analyses
        
        # Look for style profile JSON files
        for filename in os.listdir(self.analysis_dir):
            if filename.startswith('style_profile_') and filename.endswith('.json'):
                timestamp = filename.replace('style_profile_', '').replace('.json', '')
                
                # Check for corresponding files
                report_file = f"style_report_{timestamp}.md"
                samples_file = f"writing_samples_{timestamp}.json"
                
                analyses.append({
                    'timestamp': timestamp,
                    'profile_file': os.path.join(self.analysis_dir, filename),
                    'report_file': os.path.join(self.analysis_dir, report_file) if os.path.exists(os.path.join(self.analysis_dir, report_file)) else None,
                    'samples_file': os.path.join(self.analysis_dir, samples_file) if os.path.exists(os.path.join(self.analysis_dir, samples_file)) else None
                })
        
        # Sort by timestamp (most recent first)
        analyses.sort(key=lambda x: x['timestamp'], reverse=True)
        return analyses
    
    def list_analyses(self):
        """List all available analyses"""
        print("\n📋 Available Writing Style Analyses:")
        print("-" * 50)
        
        for i, analysis in enumerate(self.available_analyses, 1):
            timestamp = analysis['timestamp']
            # Parse timestamp for display
            try:
                dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                date_str = timestamp
            
            print(f"  {i}. {date_str}")
            
            # Try to load basic info
            try:
                with open(analysis['profile_file'], 'r') as f:
                    profile = json.load(f)
                    print(f"     Samples: {profile.get('sample_count', 'Unknown')}")
                    print(f"     Words: {profile.get('total_word_count', 'Unknown'):,}")
                    print(f"     Authenticity: {profile.get('avg_authenticity_score', 'Unknown'):.3f}")
            except:
                print("     (Unable to load details)")
            print()
    
    def show_analysis_summary(self, analysis_index: int = 0):
        """Show comprehensive summary of an analysis"""
        if analysis_index >= len(self.available_analyses):
            print(f"❌ Analysis index {analysis_index} not found")
            return
        
        analysis = self.available_analyses[analysis_index]
        
        try:
            with open(analysis['profile_file'], 'r') as f:
                profile = json.load(f)
            
            print(f"\n📊 Writing Style Analysis Summary")
            print("=" * 50)
            print(f"Analysis Date: {analysis['timestamp']}")
            print(f"Samples Analyzed: {profile['sample_count']:,}")
            print(f"Total Words: {profile['total_word_count']:,}")
            print(f"Average Authenticity: {profile['avg_authenticity_score']:.3f}")
            
            # Date range
            if 'date_range' in profile:
                print(f"Content Date Range: {profile['date_range']['earliest'][:10]} to {profile['date_range']['latest'][:10]}")
            
            print("\n📏 Writing Metrics:")
            print("-" * 20)
            
            # Word length
            if 'avg_word_length' in profile:
                wl = profile['avg_word_length']
                print(f"Average Word Length: {wl['mean']:.2f} characters (median: {wl['median']:.2f})")
            
            # Sentence length
            if 'avg_sentence_length' in profile:
                sl = profile['avg_sentence_length']
                print(f"Average Sentence Length: {sl['mean']:.1f} words (median: {sl['median']:.1f})")
            
            # Complexity
            if 'complexity_ratio' in profile:
                cr = profile['complexity_ratio']
                print(f"Complexity Ratio: {cr['mean']:.3f} (median: {cr['median']:.3f})")
            
            # Punctuation patterns
            print("\n🔤 Punctuation Patterns:")
            print("-" * 25)
            
            if 'exclamation_density' in profile:
                ed = profile['exclamation_density']
                print(f"Exclamation Usage: {ed['mean']:.2f} per 100 words (max: {ed['range'][1]:.1f})")
            
            if 'question_density' in profile:
                qd = profile['question_density']
                print(f"Question Usage: {qd['mean']:.2f} per 100 words (max: {qd['range'][1]:.1f})")
            
            # Tone distribution
            if 'tone_distribution' in profile:
                print("\n🎭 Tone Distribution:")
                print("-" * 20)
                for tone, count in profile['tone_distribution'].items():
                    percentage = (count / profile['sample_count']) * 100
                    print(f"{tone.title()}: {count} samples ({percentage:.1f}%)")
            
            # Common words
            if 'common_words' in profile:
                print("\n🔤 Most Common Words:")
                print("-" * 22)
                for word, count in list(profile['common_words'].items())[:10]:
                    print(f"{word}: {count}")
            
            # Writing patterns
            if 'writing_patterns' in profile:
                print("\n✍️ Writing Patterns:")
                print("-" * 20)
                patterns = profile['writing_patterns']
                
                pattern_checks = [
                    ('prefers_questions', 'Prefers Questions'),
                    ('uses_exclamations', 'Uses Exclamations'),
                    ('conversational_style', 'Conversational Style'),
                    ('technical_focus', 'Technical Focus'),
                    ('personal_voice', 'Personal Voice'),
                    ('uses_contractions', 'Uses Contractions')
                ]
                
                for key, label in pattern_checks:
                    if key in patterns:
                        status = "✅ Yes" if patterns[key] else "❌ No"
                        print(f"{label}: {status}")
            
        except Exception as e:
            print(f"❌ Error loading analysis: {e}")
    
    def show_detailed_metrics(self, analysis_index: int = 0):
        """Show detailed statistical metrics"""
        if analysis_index >= len(self.available_analyses):
            print(f"❌ Analysis index {analysis_index} not found")
            return
        
        analysis = self.available_analyses[analysis_index]
        
        try:
            with open(analysis['profile_file'], 'r') as f:
                profile = json.load(f)
            
            print(f"\n📈 Detailed Statistical Metrics")
            print("=" * 40)
            
            # Statistical metrics with ranges
            metrics = [
                ('avg_word_length', 'Average Word Length'),
                ('avg_sentence_length', 'Average Sentence Length'),
                ('complexity_ratio', 'Complexity Ratio'),
                ('exclamation_density', 'Exclamation Density'),
                ('question_density', 'Question Density'),
                ('contraction_ratio', 'Contraction Ratio'),
                ('personal_pronoun_ratio', 'Personal Pronoun Ratio')
            ]
            
            for key, label in metrics:
                if key in profile:
                    data = profile[key]
                    print(f"\n{label}:")
                    print(f"  Mean: {data['mean']:.3f}")
                    print(f"  Median: {data['median']:.3f}")
                    print(f"  Std Dev: {data['std']:.3f}")
                    print(f"  Range: {data['range'][0]:.3f} - {data['range'][1]:.3f}")
            
            # Show representative samples if available
            if 'representative_samples' in profile:
                print(f"\n📝 Representative Writing Samples:")
                print("-" * 35)
                
                for i, sample in enumerate(profile['representative_samples'][:3], 1):
                    auth_score = sample.get('authenticity_score', 0)
                    print(f"\nSample {i} (Authenticity: {auth_score:.3f}):")
                    text = sample.get('content', sample.get('text', ''))
                    if len(text) > 200:
                        text = text[:200] + "..."
                    print(f"  \"{text}\"")
        
        except Exception as e:
            print(f"❌ Error loading detailed metrics: {e}")
    
    def show_samples(self, analysis_index: int = 0, filter_by: Optional[str] = None, limit: int = 10):
        """Show writing samples with optional filtering"""
        if analysis_index >= len(self.available_analyses):
            print(f"❌ Analysis index {analysis_index} not found")
            return
        
        analysis = self.available_analyses[analysis_index]
        
        if not analysis['samples_file']:
            print("❌ No samples file found for this analysis")
            return
        
        try:
            with open(analysis['samples_file'], 'r') as f:
                samples_data = json.load(f)
            
            # Handle both formats: direct list or wrapped in object
            if isinstance(samples_data, list):
                samples = samples_data
            else:
                samples = samples_data.get('samples', [])
            
            # Apply filtering
            if filter_by:
                if filter_by == 'high_authenticity':
                    samples = [s for s in samples if s.get('authenticity_score', 0) > 0.9]
                elif filter_by == 'technical':
                    samples = [s for s in samples if s.get('style_attributes', {}).get('technical_score', 0) > 1.0]
                elif filter_by == 'casual':
                    samples = [s for s in samples if s.get('style_attributes', {}).get('conversational_score', 0) > 0.5]
                elif filter_by == 'long':
                    samples = [s for s in samples if s.get('word_count', 0) > 50]
                elif filter_by == 'short':
                    samples = [s for s in samples if s.get('word_count', 0) <= 10]
            
            print(f"\n📝 Writing Samples ({len(samples)} total)")
            if filter_by:
                print(f"Filter: {filter_by}")
            print("=" * 50)
            
            for i, sample in enumerate(samples[:limit], 1):
                text = sample.get('content', '')
                word_count = sample.get('word_count', len(text.split()))
                authenticity = sample.get('authenticity_score', 0)
                
                # Determine tone from style attributes
                attrs = sample.get('style_attributes', {})
                tech_score = attrs.get('technical_score', 0)
                conv_score = attrs.get('conversational_score', 0)
                
                if tech_score > 1.0:
                    tone = 'technical'
                elif conv_score > 0.5:
                    tone = 'casual'
                else:
                    tone = 'neutral'
                
                print(f"\nSample {i}:")
                print(f"  Words: {word_count}, Authenticity: {authenticity:.3f}, Tone: {tone}")
                print(f"  Text: \"{text[:150]}{'...' if len(text) > 150 else ''}\"")
        
        except Exception as e:
            print(f"❌ Error loading samples: {e}")
    
    def compare_analyses(self, index1: int = 0, index2: int = 1):
        """Compare two different analyses"""
        if index1 >= len(self.available_analyses) or index2 >= len(self.available_analyses):
            print("❌ One or both analysis indices not found")
            return
        
        try:
            with open(self.available_analyses[index1]['profile_file'], 'r') as f:
                profile1 = json.load(f)
            
            with open(self.available_analyses[index2]['profile_file'], 'r') as f:
                profile2 = json.load(f)
            
            print(f"\n🔄 Analysis Comparison")
            print("=" * 30)
            print(f"Analysis 1: {self.available_analyses[index1]['timestamp']}")
            print(f"Analysis 2: {self.available_analyses[index2]['timestamp']}")
            
            # Compare key metrics
            comparison_metrics = [
                ('sample_count', 'Sample Count'),
                ('total_word_count', 'Total Words'),
                ('avg_authenticity_score', 'Avg Authenticity')
            ]
            
            print(f"\n📊 Basic Comparison:")
            print("-" * 20)
            for key, label in comparison_metrics:
                val1 = profile1.get(key, 0)
                val2 = profile2.get(key, 0)
                
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    diff = val2 - val1
                    change = "↑" if diff > 0 else "↓" if diff < 0 else "="
                    print(f"{label}: {val1} → {val2} {change}")
                else:
                    print(f"{label}: {val1} → {val2}")
            
            # Compare writing patterns
            if 'writing_patterns' in profile1 and 'writing_patterns' in profile2:
                print(f"\n✍️ Pattern Changes:")
                print("-" * 18)
                
                pattern_keys = set(profile1['writing_patterns'].keys()) | set(profile2['writing_patterns'].keys())
                
                for pattern_key in sorted(pattern_keys):
                    val1 = profile1['writing_patterns'].get(pattern_key, False)
                    val2 = profile2['writing_patterns'].get(pattern_key, False)
                    
                    if val1 != val2:
                        status = f"{val1} → {val2}"
                        print(f"{pattern_key.replace('_', ' ').title()}: {status}")
        
        except Exception as e:
            print(f"❌ Error comparing analyses: {e}")
    
    def interactive_browse(self):
        """Interactive browsing session"""
        if not self.available_analyses:
            return
        
        print("\n🔍 Interactive Writing Style Browser")
        print("Commands: list, summary [N], details [N], samples [N] [filter], compare [N1] [N2], help, quit")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command in ['quit', 'q', 'exit']:
                    break
                
                elif command == 'list':
                    self.list_analyses()
                
                elif command.startswith('summary'):
                    parts = command.split()
                    index = int(parts[1]) - 1 if len(parts) > 1 else 0
                    self.show_analysis_summary(index)
                
                elif command.startswith('details'):
                    parts = command.split()
                    index = int(parts[1]) - 1 if len(parts) > 1 else 0
                    self.show_detailed_metrics(index)
                
                elif command.startswith('samples'):
                    parts = command.split()
                    index = int(parts[1]) - 1 if len(parts) > 1 else 0
                    filter_by = parts[2] if len(parts) > 2 else None
                    self.show_samples(index, filter_by)
                
                elif command.startswith('compare'):
                    parts = command.split()
                    index1 = int(parts[1]) - 1 if len(parts) > 1 else 0
                    index2 = int(parts[2]) - 1 if len(parts) > 2 else 1
                    self.compare_analyses(index1, index2)
                
                elif command == 'help':
                    print("\n🆘 Available Commands:")
                    print("  list                 - Show all available analyses")
                    print("  summary [N]          - Show summary of analysis N (default: latest)")
                    print("  details [N]          - Show detailed metrics for analysis N")
                    print("  samples [N] [filter] - Show samples with optional filter")
                    print("  compare [N1] [N2]    - Compare two analyses")
                    print("  help                 - Show this help")
                    print("  quit                 - Exit browser")
                    print("\n  Sample filters: high_authenticity, technical, casual, long, short")
                
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Writing Style Analysis Browser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive browsing
  python writing_style_browser.py browse
  
  # List all analyses
  python writing_style_browser.py list
  
  # Show latest analysis summary  
  python writing_style_browser.py summary
  
  # Show detailed metrics for analysis 2
  python writing_style_browser.py details --index 2
  
  # Show high-authenticity samples
  python writing_style_browser.py samples --filter high_authenticity
        """
    )
    
    parser.add_argument('--analysis-dir', default='personal_writing_analysis',
                       help='Directory containing analysis results')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Browse command (interactive)
    browse_parser = subparsers.add_parser('browse', help='Interactive browsing')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all analyses')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show analysis summary')
    summary_parser.add_argument('--index', type=int, default=1, help='Analysis index (1-based)')
    
    # Details command
    details_parser = subparsers.add_parser('details', help='Show detailed metrics')
    details_parser.add_argument('--index', type=int, default=1, help='Analysis index (1-based)')
    
    # Samples command
    samples_parser = subparsers.add_parser('samples', help='Show writing samples')
    samples_parser.add_argument('--index', type=int, default=1, help='Analysis index (1-based)')
    samples_parser.add_argument('--filter', choices=['high_authenticity', 'technical', 'casual', 'long', 'short'],
                               help='Filter samples by criteria')
    samples_parser.add_argument('--limit', type=int, default=10, help='Number of samples to show')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two analyses')
    compare_parser.add_argument('--index1', type=int, default=1, help='First analysis index')
    compare_parser.add_argument('--index2', type=int, default=2, help='Second analysis index')
    
    args = parser.parse_args()
    
    browser = WritingStyleBrowser(args.analysis_dir)
    
    if args.command == 'browse':
        browser.interactive_browse()
    elif args.command == 'list':
        browser.list_analyses()
    elif args.command == 'summary':
        browser.show_analysis_summary(args.index - 1)
    elif args.command == 'details':
        browser.show_detailed_metrics(args.index - 1)
    elif args.command == 'samples':
        browser.show_samples(args.index - 1, args.filter, args.limit)
    elif args.command == 'compare':
        browser.compare_analyses(args.index1 - 1, args.index2 - 1)
    else:
        # Default to showing latest summary
        browser.show_analysis_summary(0)

if __name__ == "__main__":
    main()