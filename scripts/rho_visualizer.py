#!/usr/bin/env python3
"""
Subjective Status Rho (ρ) Visualization System
Visualizes the subjective transformation state and narrative projection quality
"""

import os
import sys
import json
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import sqlite3
from dataclasses import dataclass

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.patches import Circle, Rectangle
    import matplotlib.patches as mpatches
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

@dataclass
class RhoState:
    """Represents a subjective transformation state"""
    content_id: str
    essence_clarity: float      # How clear the essential meaning is (0-1)
    persona_alignment: float    # How well persona is applied (0-1)
    namespace_coherence: float  # How coherent the namespace is (0-1)
    style_consistency: float    # How consistent the style is (0-1)
    transformation_depth: float # How deep the transformation goes (0-1)
    semantic_preservation: float # How well original meaning is preserved (0-1)
    narrative_flow: float       # How well the narrative flows (0-1)
    timestamp: datetime
    metadata: dict

class RhoVisualizer:
    """Subjective Status Rho visualization system"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.data_dir = self.project_root / "data"
        self.visualizations_dir = self.data_dir / "visualizations"
        self.visualizations_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / "rho_states.db"
        self._init_database()
        
        # Rho state quality thresholds
        self.quality_thresholds = {
            'excellent': 0.85,
            'good': 0.70,
            'fair': 0.55,
            'poor': 0.40
        }
        
        # Color schemes for different visualizations
        self.color_schemes = {
            'quality': ['#d32f2f', '#f57c00', '#fbc02d', '#689f38', '#388e3c'],  # Red to Green
            'dimensions': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2'],
            'flow': ['#0d47a1', '#1976d2', '#42a5f5', '#90caf9']
        }
    
    def _init_database(self):
        """Initialize rho states database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rho_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT UNIQUE,
                    essence_clarity REAL,
                    persona_alignment REAL,
                    namespace_coherence REAL,
                    style_consistency REAL,
                    transformation_depth REAL,
                    semantic_preservation REAL,
                    narrative_flow REAL,
                    overall_rho REAL,
                    quality_level TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content_id ON rho_states (content_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_level ON rho_states (quality_level);")
    
    def calculate_rho(self, content_analysis: Dict[str, Any]) -> RhoState:
        """Calculate subjective status rho from content analysis"""
        
        # Extract or calculate individual dimensions
        essence_clarity = content_analysis.get('essence_clarity', 0.5)
        persona_alignment = content_analysis.get('persona_alignment', 0.5)
        namespace_coherence = content_analysis.get('namespace_coherence', 0.5)
        style_consistency = content_analysis.get('style_consistency', 0.5)
        transformation_depth = content_analysis.get('transformation_depth', 0.5)
        semantic_preservation = content_analysis.get('semantic_preservation', 0.5)
        narrative_flow = content_analysis.get('narrative_flow', 0.5)
        
        # If not provided, estimate from available data
        if 'transformation_result' in content_analysis:
            result = content_analysis['transformation_result']
            
            # Estimate essence clarity from content length and coherence
            if 'narrative' in result:
                narrative = result['narrative']
                essence_clarity = min(1.0, len(narrative.split()) / 200)  # Rough estimate
            
            # Estimate persona alignment from persona match
            if 'persona' in content_analysis:
                persona_alignment = 0.8  # Assume good alignment if persona was applied
            
            # Estimate other dimensions based on available indicators
            if 'reflection' in result:
                transformation_depth = 0.7  # Has reflection = deeper transformation
            
            if len(narrative.split('.')) > 3:  # Multiple sentences
                narrative_flow = 0.6
        
        return RhoState(
            content_id=content_analysis.get('content_id', 'unknown'),
            essence_clarity=essence_clarity,
            persona_alignment=persona_alignment,
            namespace_coherence=namespace_coherence,
            style_consistency=style_consistency,
            transformation_depth=transformation_depth,
            semantic_preservation=semantic_preservation,
            narrative_flow=narrative_flow,
            timestamp=datetime.now(),
            metadata=content_analysis.get('metadata', {})
        )
    
    def store_rho_state(self, rho_state: RhoState) -> bool:
        """Store rho state in database"""
        
        # Calculate overall rho (weighted average)
        weights = {
            'essence_clarity': 0.20,
            'persona_alignment': 0.15,
            'namespace_coherence': 0.15,
            'style_consistency': 0.10,
            'transformation_depth': 0.15,
            'semantic_preservation': 0.15,
            'narrative_flow': 0.10
        }
        
        overall_rho = (
            rho_state.essence_clarity * weights['essence_clarity'] +
            rho_state.persona_alignment * weights['persona_alignment'] +
            rho_state.namespace_coherence * weights['namespace_coherence'] +
            rho_state.style_consistency * weights['style_consistency'] +
            rho_state.transformation_depth * weights['transformation_depth'] +
            rho_state.semantic_preservation * weights['semantic_preservation'] +
            rho_state.narrative_flow * weights['narrative_flow']
        )
        
        # Determine quality level
        if overall_rho >= self.quality_thresholds['excellent']:
            quality_level = 'excellent'
        elif overall_rho >= self.quality_thresholds['good']:
            quality_level = 'good'
        elif overall_rho >= self.quality_thresholds['fair']:
            quality_level = 'fair'
        else:
            quality_level = 'poor'
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO rho_states 
                    (content_id, essence_clarity, persona_alignment, namespace_coherence,
                     style_consistency, transformation_depth, semantic_preservation,
                     narrative_flow, overall_rho, quality_level, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rho_state.content_id,
                    rho_state.essence_clarity,
                    rho_state.persona_alignment,
                    rho_state.namespace_coherence,
                    rho_state.style_consistency,
                    rho_state.transformation_depth,
                    rho_state.semantic_preservation,
                    rho_state.narrative_flow,
                    overall_rho,
                    quality_level,
                    json.dumps(rho_state.metadata)
                ))
            
            return True
            
        except Exception as e:
            print(f"❌ Error storing rho state: {e}")
            return False
    
    def create_radar_chart(self, content_id: str, output_file: str = None) -> str:
        """Create radar chart for individual content rho state"""
        
        if not PLOTTING_AVAILABLE:
            return "Plotting libraries not available"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT essence_clarity, persona_alignment, namespace_coherence,
                           style_consistency, transformation_depth, semantic_preservation,
                           narrative_flow, overall_rho, quality_level
                    FROM rho_states WHERE content_id = ?
                """, (content_id,))
                
                row = cursor.fetchone()
                if not row:
                    return f"No rho state found for content_id: {content_id}"
                
                values = list(row[:7])  # First 7 dimensions
                overall_rho = row[7]
                quality_level = row[8]
                
                # Dimension labels
                labels = [
                    'Essence\nClarity',
                    'Persona\nAlignment', 
                    'Namespace\nCoherence',
                    'Style\nConsistency',
                    'Transformation\nDepth',
                    'Semantic\nPreservation',
                    'Narrative\nFlow'
                ]
                
                # Create radar chart
                angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
                values += [values[0]]  # Complete the circle
                angles += [angles[0]]
                
                fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
                
                # Plot the values
                color = self.color_schemes['quality'][min(4, int(overall_rho * 5))]
                ax.plot(angles, values, 'o-', linewidth=2, color=color, label=f'ρ = {overall_rho:.3f}')
                ax.fill(angles, values, alpha=0.25, color=color)
                
                # Customize the chart
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels)
                ax.set_ylim(0, 1)
                ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
                ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
                ax.grid(True)
                
                plt.title(f'Subjective Status Rho (ρ) - {content_id}\nQuality: {quality_level.upper()}', 
                         size=16, pad=20)
                plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
                
                if output_file is None:
                    output_file = str(self.visualizations_dir / f"rho_radar_{content_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                return output_file
                
        except Exception as e:
            print(f"❌ Error creating radar chart: {e}")
            return f"Failed to create radar chart: {e}"
    
    def create_rho_evolution(self, content_ids: List[str] = None, output_file: str = None) -> str:
        """Create timeline showing rho evolution"""
        
        if not PLOTTING_AVAILABLE:
            return "Plotting libraries not available"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                if content_ids:
                    placeholders = ','.join(['?' for _ in content_ids])
                    cursor = conn.execute(f"""
                        SELECT content_id, overall_rho, quality_level, created_at
                        FROM rho_states 
                        WHERE content_id IN ({placeholders})
                        ORDER BY created_at
                    """, content_ids)
                else:
                    cursor = conn.execute("""
                        SELECT content_id, overall_rho, quality_level, created_at
                        FROM rho_states 
                        ORDER BY created_at
                    """)
                
                data = cursor.fetchall()
                
                if not data:
                    return "No rho states found"
                
                # Extract data for plotting
                timestamps = [datetime.fromisoformat(row[3]) for row in data]
                rho_values = [row[1] for row in data]
                quality_levels = [row[2] for row in data]
                content_ids = [row[0] for row in data]
                
                # Create evolution chart
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
                
                # Top plot: Rho values over time
                colors = [self.color_schemes['quality'][min(4, int(rho * 5))] for rho in rho_values]
                ax1.scatter(timestamps, rho_values, c=colors, s=100, alpha=0.7)
                ax1.plot(timestamps, rho_values, 'b-', alpha=0.3)
                
                ax1.set_ylabel('Overall Rho (ρ)')
                ax1.set_title('Subjective Status Rho Evolution Over Time')
                ax1.grid(True, alpha=0.3)
                ax1.set_ylim(0, 1)
                
                # Add quality threshold lines
                for level, threshold in self.quality_thresholds.items():
                    ax1.axhline(y=threshold, color='gray', linestyle='--', alpha=0.5)
                    ax1.text(timestamps[-1], threshold, level, ha='left', va='bottom')
                
                # Bottom plot: Quality level distribution
                quality_counts = {}
                for level in quality_levels:
                    quality_counts[level] = quality_counts.get(level, 0) + 1
                
                qualities = list(quality_counts.keys())
                counts = list(quality_counts.values())
                colors = [self.color_schemes['quality'][i] for i in range(len(qualities))]
                
                ax2.bar(qualities, counts, color=colors)
                ax2.set_ylabel('Count')
                ax2.set_title('Quality Level Distribution')
                
                plt.tight_layout()
                
                if output_file is None:
                    output_file = str(self.visualizations_dir / f"rho_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                return output_file
                
        except Exception as e:
            print(f"❌ Error creating evolution chart: {e}")
            return f"Failed to create evolution chart: {e}"
    
    def create_dimension_heatmap(self, output_file: str = None) -> str:
        """Create heatmap showing correlation between rho dimensions"""
        
        if not PLOTTING_AVAILABLE or not SKLEARN_AVAILABLE:
            return "Required libraries not available"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT essence_clarity, persona_alignment, namespace_coherence,
                           style_consistency, transformation_depth, semantic_preservation,
                           narrative_flow
                    FROM rho_states
                """)
                
                data = cursor.fetchall()
                
                if len(data) < 2:
                    return "Not enough data for correlation analysis"
                
                # Convert to numpy array
                data_matrix = np.array(data)
                
                # Calculate correlation matrix
                correlation_matrix = np.corrcoef(data_matrix.T)
                
                # Dimension labels
                labels = [
                    'Essence\nClarity',
                    'Persona\nAlignment', 
                    'Namespace\nCoherence',
                    'Style\nConsistency',
                    'Transformation\nDepth',
                    'Semantic\nPreservation',
                    'Narrative\nFlow'
                ]
                
                # Create heatmap
                fig, ax = plt.subplots(figsize=(10, 8))
                
                sns.heatmap(correlation_matrix, 
                           xticklabels=labels,
                           yticklabels=labels,
                           annot=True,
                           cmap='RdYlBu_r',
                           center=0,
                           square=True,
                           ax=ax)
                
                plt.title('Rho Dimensions Correlation Heatmap', size=16, pad=20)
                plt.tight_layout()
                
                if output_file is None:
                    output_file = str(self.visualizations_dir / f"rho_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                return output_file
                
        except Exception as e:
            print(f"❌ Error creating heatmap: {e}")
            return f"Failed to create heatmap: {e}"
    
    def analyze_transformation_data(self, transformation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transformation results to extract rho metrics"""
        
        analysis = {
            'content_id': transformation_results.get('content_id', 'unknown'),
            'metadata': transformation_results.get('metadata', {})
        }
        
        # Extract transformation result
        if 'transformation' in transformation_results:
            transform = transformation_results['transformation']
            
            if 'projection' in transform:
                projection = transform['projection']
                narrative = projection.get('narrative', '')
                reflection = projection.get('reflection', '')
                
                # Analyze narrative quality
                analysis['essence_clarity'] = self._analyze_essence_clarity(narrative)
                analysis['narrative_flow'] = self._analyze_narrative_flow(narrative)
                analysis['transformation_depth'] = 0.7 if reflection else 0.4
                
                # Check for persona/namespace/style indicators
                params = transformation_results.get('parameters', {})
                analysis['persona_alignment'] = self._analyze_persona_alignment(narrative, params.get('persona'))
                analysis['namespace_coherence'] = self._analyze_namespace_coherence(narrative, params.get('namespace'))
                analysis['style_consistency'] = self._analyze_style_consistency(narrative, params.get('style'))
                
                # Estimate semantic preservation (rough heuristic)
                original = transformation_results.get('input_text', '')
                analysis['semantic_preservation'] = self._estimate_semantic_preservation(original, narrative)
        
        return analysis
    
    def _analyze_essence_clarity(self, narrative: str) -> float:
        """Analyze how clear the essential meaning is"""
        # Simple heuristics - in practice, this would use more sophisticated NLP
        words = narrative.split()
        sentences = narrative.split('.')
        
        # Longer, well-structured content tends to be clearer
        clarity_score = min(1.0, len(words) / 100)  # Up to 100 words
        
        # Penalize if too short or too long
        if len(words) < 20:
            clarity_score *= 0.5
        elif len(words) > 500:
            clarity_score *= 0.8
        
        # Good sentence structure
        if len(sentences) > 1:
            avg_sentence_length = len(words) / len(sentences)
            if 10 <= avg_sentence_length <= 25:  # Good range
                clarity_score *= 1.1
        
        return min(1.0, clarity_score)
    
    def _analyze_narrative_flow(self, narrative: str) -> float:
        """Analyze how well the narrative flows"""
        sentences = [s.strip() for s in narrative.split('.') if s.strip()]
        
        if len(sentences) < 2:
            return 0.3
        
        # Look for transition words and coherent structure
        transition_words = ['however', 'therefore', 'moreover', 'furthermore', 'consequently', 'meanwhile', 'thus']
        transition_count = sum(1 for word in transition_words if word in narrative.lower())
        
        flow_score = 0.5 + (transition_count * 0.1)  # Base + transitions
        
        # Good sentence length variety indicates better flow
        sentence_lengths = [len(s.split()) for s in sentences]
        if len(set(sentence_lengths)) > 1:  # Variety in length
            flow_score += 0.1
        
        return min(1.0, flow_score)
    
    def _analyze_persona_alignment(self, narrative: str, persona: str) -> float:
        """Analyze how well the persona is applied"""
        if not persona:
            return 0.5
        
        # Simple keyword-based analysis
        persona_indicators = {
            'philosopher': ['contemplat', 'exist', 'meaning', 'question', 'ponder', 'reflect'],
            'scientist': ['observ', 'analyz', 'hypothes', 'evidence', 'data', 'research'],
            'artist': ['creat', 'express', 'beauty', 'aesthetic', 'inspir', 'visual'],
            'critic': ['evaluat', 'assess', 'judg', 'analyz', 'interpret', 'critiqu']
        }
        
        if persona.lower() in persona_indicators:
            keywords = persona_indicators[persona.lower()]
            matches = sum(1 for keyword in keywords if keyword in narrative.lower())
            return min(1.0, 0.4 + (matches * 0.1))
        
        return 0.6  # Default if persona not recognized
    
    def _analyze_namespace_coherence(self, narrative: str, namespace: str) -> float:
        """Analyze namespace coherence"""
        if not namespace:
            return 0.5
        
        # This would be more sophisticated in practice
        namespace_themes = {
            'classical_literature': ['classic', 'literary', 'ancient', 'tradition'],
            'natural_world': ['nature', 'natural', 'organic', 'environment'],
            'cyberpunk_future': ['digital', 'cyber', 'technology', 'future']
        }
        
        if namespace.lower() in namespace_themes:
            keywords = namespace_themes[namespace.lower()]
            matches = sum(1 for keyword in keywords if keyword in narrative.lower())
            return min(1.0, 0.4 + (matches * 0.15))
        
        return 0.6
    
    def _analyze_style_consistency(self, narrative: str, style: str) -> float:
        """Analyze style consistency"""
        if not style:
            return 0.5
        
        # Simple style analysis
        sentences = narrative.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        style_scores = {
            'formal': 0.8 if avg_length > 15 else 0.6,
            'casual': 0.8 if avg_length < 15 else 0.6,
            'academic': 0.8 if avg_length > 20 else 0.6,
            'poetic': 0.7  # Harder to analyze automatically
        }
        
        return style_scores.get(style.lower(), 0.6)
    
    def _estimate_semantic_preservation(self, original: str, transformed: str) -> float:
        """Estimate how well semantic meaning is preserved"""
        if not original or not transformed:
            return 0.5
        
        # Simple heuristic: length ratio and word overlap
        length_ratio = len(transformed) / len(original) if original else 0
        
        # Ideal ratio is around 1.0-1.5 (transformed should be similar or slightly longer)
        if 0.8 <= length_ratio <= 1.5:
            length_score = 1.0
        elif 0.5 <= length_ratio <= 2.0:
            length_score = 0.8
        else:
            length_score = 0.5
        
        # Word overlap (simple measure)
        original_words = set(original.lower().split())
        transformed_words = set(transformed.lower().split())
        
        if original_words:
            overlap = len(original_words & transformed_words) / len(original_words)
        else:
            overlap = 0
        
        # Combine length and overlap scores
        return (length_score * 0.4) + (overlap * 0.6)
    
    def get_rho_stats(self) -> Dict[str, Any]:
        """Get rho database statistics"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Basic stats
                total_states = conn.execute("SELECT COUNT(*) FROM rho_states").fetchone()[0]
                
                # Average rho by quality level
                quality_stats = conn.execute("""
                    SELECT quality_level, COUNT(*), AVG(overall_rho), 
                           AVG(essence_clarity), AVG(persona_alignment), 
                           AVG(namespace_coherence), AVG(style_consistency),
                           AVG(transformation_depth), AVG(semantic_preservation),
                           AVG(narrative_flow)
                    FROM rho_states 
                    GROUP BY quality_level
                """).fetchall()
                
                # Overall averages
                overall_avg = conn.execute("""
                    SELECT AVG(overall_rho), AVG(essence_clarity), AVG(persona_alignment),
                           AVG(namespace_coherence), AVG(style_consistency),
                           AVG(transformation_depth), AVG(semantic_preservation),
                           AVG(narrative_flow)
                    FROM rho_states
                """).fetchone()
                
                return {
                    'total_states': total_states,
                    'quality_distribution': {
                        row[0]: {
                            'count': row[1],
                            'avg_rho': round(row[2], 3),
                            'dimensions': {
                                'essence_clarity': round(row[3], 3),
                                'persona_alignment': round(row[4], 3),
                                'namespace_coherence': round(row[5], 3),
                                'style_consistency': round(row[6], 3),
                                'transformation_depth': round(row[7], 3),
                                'semantic_preservation': round(row[8], 3),
                                'narrative_flow': round(row[9], 3)
                            }
                        } for row in quality_stats
                    },
                    'overall_averages': {
                        'overall_rho': round(overall_avg[0], 3) if overall_avg[0] else 0,
                        'essence_clarity': round(overall_avg[1], 3) if overall_avg[1] else 0,
                        'persona_alignment': round(overall_avg[2], 3) if overall_avg[2] else 0,
                        'namespace_coherence': round(overall_avg[3], 3) if overall_avg[3] else 0,
                        'style_consistency': round(overall_avg[4], 3) if overall_avg[4] else 0,
                        'transformation_depth': round(overall_avg[5], 3) if overall_avg[5] else 0,
                        'semantic_preservation': round(overall_avg[6], 3) if overall_avg[6] else 0,
                        'narrative_flow': round(overall_avg[7], 3) if overall_avg[7] else 0
                    }
                }
                
        except Exception as e:
            print(f"❌ Error getting rho stats: {e}")
            return {'error': str(e)}


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Subjective Status Rho (ρ) Visualization System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze transformation result and store rho state
  python rho_visualizer.py analyze --file transformation_result.json
  
  # Create radar chart for specific content
  python rho_visualizer.py radar --content-id essay_chunk_0001
  
  # Create evolution timeline
  python rho_visualizer.py evolution --output rho_timeline.png
  
  # Create dimension correlation heatmap
  python rho_visualizer.py heatmap --output correlations.png
  
  # Get statistics
  python rho_visualizer.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze transformation results')
    analyze_parser.add_argument('--file', type=Path, help='Transformation result JSON file')
    analyze_parser.add_argument('--data', help='Direct JSON data as string')
    
    # Radar chart command
    radar_parser = subparsers.add_parser('radar', help='Create radar chart')
    radar_parser.add_argument('--content-id', required=True, help='Content ID')
    radar_parser.add_argument('--output', help='Output file path')
    
    # Evolution command
    evolution_parser = subparsers.add_parser('evolution', help='Create evolution timeline')
    evolution_parser.add_argument('--content-ids', help='Comma-separated content IDs')
    evolution_parser.add_argument('--output', help='Output file path')
    
    # Heatmap command
    heatmap_parser = subparsers.add_parser('heatmap', help='Create correlation heatmap')
    heatmap_parser.add_argument('--output', help='Output file path')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show rho statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check dependencies for visualization commands
    if args.command in ['radar', 'evolution', 'heatmap'] and not PLOTTING_AVAILABLE:
        print("❌ Plotting libraries required. Install with: pip install matplotlib seaborn")
        return
    
    visualizer = RhoVisualizer()
    
    if args.command == 'analyze':
        if args.file:
            if not args.file.exists():
                print(f"❌ File not found: {args.file}")
                return
            
            with open(args.file, 'r') as f:
                data = json.load(f)
        elif args.data:
            data = json.loads(args.data)
        else:
            print("❌ Either --file or --data required")
            return
        
        analysis = visualizer.analyze_transformation_data(data)
        rho_state = visualizer.calculate_rho(analysis)
        
        if visualizer.store_rho_state(rho_state):
            print(f"✅ Rho state stored for content: {rho_state.content_id}")
            print(f"   Overall ρ: {((rho_state.essence_clarity + rho_state.persona_alignment + rho_state.namespace_coherence + rho_state.style_consistency + rho_state.transformation_depth + rho_state.semantic_preservation + rho_state.narrative_flow) / 7):.3f}")
        else:
            print("❌ Failed to store rho state")
    
    elif args.command == 'radar':
        output_file = visualizer.create_radar_chart(args.content_id, args.output)
        print(f"✅ Radar chart created: {output_file}")
    
    elif args.command == 'evolution':
        content_ids = args.content_ids.split(',') if args.content_ids else None
        output_file = visualizer.create_rho_evolution(content_ids, args.output)
        print(f"✅ Evolution chart created: {output_file}")
    
    elif args.command == 'heatmap':
        output_file = visualizer.create_dimension_heatmap(args.output)
        print(f"✅ Heatmap created: {output_file}")
    
    elif args.command == 'stats':
        stats = visualizer.get_rho_stats()
        
        if 'error' in stats:
            print(f"❌ Error getting stats: {stats['error']}")
            return
        
        print("📊 Subjective Status Rho (ρ) Statistics")
        print("=" * 50)
        print(f"Total states: {stats['total_states']}")
        print()
        
        print("Quality Distribution:")
        for quality, data in stats['quality_distribution'].items():
            print(f"  {quality.upper()}: {data['count']} states (avg ρ: {data['avg_rho']})")
        
        print()
        print("Overall Averages:")
        for dimension, value in stats['overall_averages'].items():
            print(f"  {dimension}: {value}")


if __name__ == "__main__":
    main()