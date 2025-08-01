#!/usr/bin/env python3
"""
Agentic Assessment Framework
Uses metadata patterns and LLM analysis for intelligent content evaluation and rating
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from dataclasses import dataclass
import requests
from collections import defaultdict
import argparse

@dataclass
class AssessmentTask:
    """Represents an assessment task for agentic evaluation"""
    task_id: str
    task_type: str  # 'quality_rating', 'editorial_assessment', 'topic_classification', 'gem_detection'
    conversation_ids: List[int]
    assessment_criteria: Dict[str, Any]
    metadata_requirements: List[str]
    llm_prompt_template: str
    scoring_function: Optional[Callable] = None
    batch_size: int = 10

@dataclass
class AssessmentResult:
    """Results from an agentic assessment"""
    task_id: str
    conversation_id: int
    scores: Dict[str, float]
    reasoning: str
    confidence: float
    metadata_used: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

class AgenticAssessor:
    """Intelligent assessment system using metadata patterns and LLM analysis"""
    
    def __init__(self, 
                 database_url: str = "postgresql://tem@localhost/humanizer_archive",
                 ollama_host: str = "http://localhost:11434"):
        self.database_url = database_url
        self.ollama_host = ollama_host
        self.assessment_history = []
        
        # Predefined assessment tasks
        self.task_templates = {
            'gem_detection': self._create_gem_detection_task,
            'editorial_assessment': self._create_editorial_assessment_task,
            'quality_enhancement': self._create_quality_enhancement_task,
            'topic_depth_analysis': self._create_topic_depth_task,
            'narrative_potential': self._create_narrative_potential_task,
            'cross_conversation_patterns': self._create_pattern_analysis_task
        }
        
        print("🤖 Agentic Assessment Framework")
        print("=" * 40)
    
    def create_assessment_task(self, 
                             task_type: str,
                             conversation_ids: Optional[List[int]] = None,
                             custom_criteria: Optional[Dict] = None,
                             batch_size: int = 10) -> AssessmentTask:
        """Create a new assessment task"""
        
        if task_type in self.task_templates:
            return self.task_templates[task_type](conversation_ids, custom_criteria, batch_size)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def _create_gem_detection_task(self, conversation_ids, custom_criteria, batch_size) -> AssessmentTask:
        """Task to detect exceptional insights or 'gems' in conversations"""
        
        criteria = {
            'novelty_weight': 0.3,
            'depth_weight': 0.25,
            'coherence_weight': 0.2,
            'insight_density_weight': 0.15,
            'cross_domain_connections_weight': 0.1,
            'min_word_count': 200,
            'require_high_quality': True
        }
        
        if custom_criteria:
            criteria.update(custom_criteria)
        
        prompt_template = """
        Analyze this conversation for exceptional insights or "gems" - moments of profound understanding, 
        novel connections, or transformative ideas.
        
        CONVERSATION METADATA:
        - Quality Score: {composite_score}
        - Category: {category}
        - Word Count: {word_count}
        - Primary Topic: {primary_topic}
        
        CONVERSATION CONTENT:
        {conversation_text}
        
        Rate on scales of 0-1:
        1. NOVELTY: How original or unique are the insights?
        2. DEPTH: How profound or significant are the ideas?
        3. COHERENCE: How well-structured and logical is the thinking?
        4. INSIGHT_DENSITY: How many valuable insights per unit of text?
        5. CROSS_DOMAIN: How well does it connect different fields/concepts?
        
        Respond in JSON format:
        {
            "novelty": 0.0-1.0,
            "depth": 0.0-1.0,
            "coherence": 0.0-1.0,
            "insight_density": 0.0-1.0,
            "cross_domain": 0.0-1.0,
            "overall_gem_score": 0.0-1.0,
            "reasoning": "Detailed explanation of scores",
            "key_insights": ["insight1", "insight2", ...],
            "gem_potential": "none|low|medium|high|exceptional",
            "recommended_uses": ["use1", "use2", ...]
        }
        """
        
        return AssessmentTask(
            task_id=f"gem_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_type='gem_detection',
            conversation_ids=conversation_ids or [],
            assessment_criteria=criteria,
            metadata_requirements=['composite_score', 'category', 'word_count', 'primary_topic'],
            llm_prompt_template=prompt_template,
            batch_size=batch_size
        )
    
    def _create_editorial_assessment_task(self, conversation_ids, custom_criteria, batch_size) -> AssessmentTask:
        """Task to assess editorial potential for books, articles, posts"""
        
        criteria = {
            'article_potential_weight': 0.25,
            'book_chapter_potential_weight': 0.25,
            'blog_post_potential_weight': 0.2,
            'discourse_post_potential_weight': 0.15,
            'social_media_potential_weight': 0.15,
            'min_editorial_score': 0.6
        }
        
        if custom_criteria:
            criteria.update(custom_criteria)
        
        prompt_template = """
        Assess this conversation's potential for transformation into various editorial formats.
        
        CONVERSATION METADATA:
        - Quality Score: {composite_score}
        - Category: {category}
        - Word Count: {word_count}
        - Editorial Potential: {editorial_potential}
        
        CONVERSATION CONTENT:
        {conversation_text}
        
        Evaluate potential for different formats (0-1 scale):
        1. ARTICLE: Structured, informative piece for publication
        2. BOOK_CHAPTER: Extended treatment as part of larger work
        3. BLOG_POST: Engaging, accessible web content
        4. DISCOURSE_POST: Community discussion starter
        5. SOCIAL_MEDIA: Condensed, shareable insights
        
        Respond in JSON format:
        {
            "article_potential": 0.0-1.0,
            "book_chapter_potential": 0.0-1.0,
            "blog_post_potential": 0.0-1.0,
            "discourse_post_potential": 0.0-1.0,
            "social_media_potential": 0.0-1.0,
            "best_format": "article|book_chapter|blog_post|discourse_post|social_media",
            "transformation_effort": "minimal|moderate|significant|extensive",
            "editorial_improvements": ["improvement1", "improvement2", ...],
            "target_audience": "general|technical|academic|enthusiast",
            "estimated_word_count_after_editing": number
        }
        """
        
        return AssessmentTask(
            task_id=f"editorial_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_type='editorial_assessment',
            conversation_ids=conversation_ids or [],
            assessment_criteria=criteria,
            metadata_requirements=['composite_score', 'category', 'word_count', 'editorial_potential'],
            llm_prompt_template=prompt_template,
            batch_size=batch_size
        )
    
    def _create_quality_enhancement_task(self, conversation_ids, custom_criteria, batch_size) -> AssessmentTask:
        """Task to identify specific quality improvement opportunities"""
        
        criteria = {
            'clarity_improvement_weight': 0.25,
            'structure_improvement_weight': 0.25,
            'depth_enhancement_weight': 0.2,
            'coherence_improvement_weight': 0.15,
            'completeness_improvement_weight': 0.15
        }
        
        if custom_criteria:
            criteria.update(custom_criteria)
        
        prompt_template = """
        Analyze this conversation for specific quality improvement opportunities.
        
        CURRENT QUALITY SCORES:
        - Composite: {composite_score}
        - Readability: {readability_score}
        - Coherence: {coherence_score}
        - Depth: {depth_score}
        - Completeness: {completeness_score}
        
        CONVERSATION CONTENT:
        {conversation_text}
        
        Identify improvement potential in each dimension (0-1 scale):
        
        Respond in JSON format:
        {
            "clarity_improvement_potential": 0.0-1.0,
            "structure_improvement_potential": 0.0-1.0,
            "depth_enhancement_potential": 0.0-1.0,
            "coherence_improvement_potential": 0.0-1.0,
            "completeness_improvement_potential": 0.0-1.0,
            "predicted_quality_after_improvement": 0.0-1.0,
            "specific_improvements": [
                {"type": "clarity|structure|depth|coherence|completeness", "description": "...", "priority": "high|medium|low"},
                ...
            ],
            "improvement_effort_estimate": "low|medium|high",
            "roi_assessment": "low|medium|high"
        }
        """
        
        return AssessmentTask(
            task_id=f"quality_enhancement_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_type='quality_enhancement', 
            conversation_ids=conversation_ids or [],
            assessment_criteria=criteria,
            metadata_requirements=['composite_score', 'readability_score', 'coherence_score', 'depth_score', 'completeness_score'],
            llm_prompt_template=prompt_template,
            batch_size=batch_size
        )
    
    def _create_topic_depth_task(self, conversation_ids, custom_criteria, batch_size) -> AssessmentTask:
        """Task to analyze topic depth and expertise level"""
        
        criteria = {
            'expertise_depth_weight': 0.3,
            'topic_coverage_weight': 0.25,
            'conceptual_sophistication_weight': 0.2,
            'practical_applicability_weight': 0.15,
            'interdisciplinary_connections_weight': 0.1
        }
        
        prompt_template = """
        Analyze the depth and sophistication of topic treatment in this conversation.
        
        METADATA:
        - Category: {category}
        - Primary Topic: {primary_topic}
        - Word Count: {word_count}
        
        CONTENT:
        {conversation_text}
        
        Assess topic treatment depth:
        
        Respond in JSON format:
        {
            "expertise_level": "novice|intermediate|advanced|expert",
            "topic_depth_score": 0.0-1.0,
            "conceptual_sophistication": 0.0-1.0,
            "practical_applicability": 0.0-1.0,
            "interdisciplinary_connections": 0.0-1.0,
            "subtopics_covered": ["subtopic1", "subtopic2", ...],
            "missing_aspects": ["aspect1", "aspect2", ...],
            "recommended_depth_enhancements": ["enhancement1", "enhancement2", ...],
            "target_audience_level": "general|informed|specialist|expert"
        }
        """
        
        return AssessmentTask(
            task_id=f"topic_depth_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_type='topic_depth_analysis',
            conversation_ids=conversation_ids or [],
            assessment_criteria=criteria,
            metadata_requirements=['category', 'primary_topic', 'word_count'],
            llm_prompt_template=prompt_template,
            batch_size=batch_size
        )
    
    def _create_narrative_potential_task(self, conversation_ids, custom_criteria, batch_size) -> AssessmentTask:
        """Task to assess narrative and storytelling potential"""
        
        criteria = {
            'story_arc_potential': 0.25,
            'character_development': 0.2,
            'conflict_tension': 0.2,
            'emotional_resonance': 0.2,
            'universal_themes': 0.15
        }
        
        prompt_template = """
        Analyze the narrative and storytelling potential of this conversation.
        
        METADATA:
        - Category: {category}
        - Word Count: {word_count}
        - Quality Score: {composite_score}
        
        CONTENT:
        {conversation_text}
        
        Assess narrative elements:
        
        Respond in JSON format:
        {
            "story_arc_potential": 0.0-1.0,
            "character_development_potential": 0.0-1.0,
            "conflict_tension_present": 0.0-1.0,
            "emotional_resonance": 0.0-1.0,
            "universal_themes_score": 0.0-1.0,
            "narrative_structure": "none|weak|moderate|strong",
            "storytelling_elements": ["element1", "element2", ...],
            "narrative_transformation_suggestions": ["suggestion1", "suggestion2", ...],
            "genre_potential": ["genre1", "genre2", ...],
            "target_medium": "text|audio|visual|interactive"
        }
        """
        
        return AssessmentTask(
            task_id=f"narrative_potential_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_type='narrative_potential',
            conversation_ids=conversation_ids or [],
            assessment_criteria=criteria,
            metadata_requirements=['category', 'word_count', 'composite_score'],
            llm_prompt_template=prompt_template,
            batch_size=batch_size
        )
    
    def _create_pattern_analysis_task(self, conversation_ids, custom_criteria, batch_size) -> AssessmentTask:
        """Task to identify patterns across multiple conversations"""
        
        criteria = {
            'thematic_consistency': 0.3,
            'conceptual_evolution': 0.25,
            'cross_reference_density': 0.2,
            'knowledge_building': 0.15,
            'synthesis_potential': 0.1
        }
        
        prompt_template = """
        Analyze patterns and connections across this set of conversations.
        
        CONVERSATIONS METADATA:
        {conversations_metadata}
        
        COMBINED CONTENT SUMMARY:
        {combined_content}
        
        Identify cross-conversation patterns:
        
        Respond in JSON format:
        {
            "recurring_themes": ["theme1", "theme2", ...],
            "conceptual_evolution_detected": true/false,
            "knowledge_building_progression": 0.0-1.0,
            "cross_reference_opportunities": ["ref1", "ref2", ...],
            "synthesis_potential": 0.0-1.0,
            "recommended_groupings": [
                {"conversations": [id1, id2, ...], "theme": "...", "synthesis_approach": "..."},
                ...
            ],
            "meta_insights": ["insight1", "insight2", ...],
            "collection_coherence": 0.0-1.0
        }
        """
        
        return AssessmentTask(
            task_id=f"pattern_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_type='cross_conversation_patterns',
            conversation_ids=conversation_ids or [],
            assessment_criteria=criteria,
            metadata_requirements=['category', 'primary_topic', 'composite_score', 'word_count'],
            llm_prompt_template=prompt_template,
            batch_size=batch_size
        )
    
    def execute_assessment_task(self, task: AssessmentTask) -> List[AssessmentResult]:
        """Execute an assessment task on specified conversations"""
        
        print(f"🔄 Executing assessment task: {task.task_type}")
        print(f"   Task ID: {task.task_id}")
        print(f"   Conversations: {len(task.conversation_ids)}")
        
        results = []
        
        # Get conversation data with required metadata
        conversations = self._get_conversation_data(task.conversation_ids, task.metadata_requirements)
        
        # Process in batches
        for i in range(0, len(conversations), task.batch_size):
            batch = conversations[i:i+task.batch_size]
            batch_results = self._process_assessment_batch(task, batch)
            results.extend(batch_results)
            
            print(f"   Processed batch {i//task.batch_size + 1}/{(len(conversations) + task.batch_size - 1)//task.batch_size}")
        
        # Store results
        self._store_assessment_results(results)
        self.assessment_history.extend(results)
        
        print(f"✅ Assessment complete: {len(results)} conversations assessed")
        return results
    
    def _get_conversation_data(self, conversation_ids: List[int], metadata_requirements: List[str]) -> List[Dict]:
        """Get conversation data with required metadata"""
        
        with psycopg2.connect(self.database_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            
            # Build query to get required metadata
            base_fields = ['ac.id', 'ac.title', 'ac.body_text', 'ac.word_count', 'ac.category']
            quality_fields = ['cqa.composite_score', 'cqa.readability_score', 'cqa.coherence_score', 
                            'cqa.depth_score', 'cqa.completeness_score', 'cqa.primary_topic', 'cqa.editorial_potential']
            
            all_fields = base_fields + quality_fields
            
            if conversation_ids:
                placeholders = ','.join(['%s'] * len(conversation_ids))
                query = f"""
                    SELECT {', '.join(all_fields)}
                    FROM archived_content ac
                    LEFT JOIN conversation_quality_assessments cqa ON ac.id = cqa.conversation_id
                    WHERE ac.id IN ({placeholders}) AND ac.content_type = 'conversation'
                """
                cursor.execute(query, conversation_ids)
            else:
                # Get high-quality conversations if no specific IDs provided
                query = f"""
                    SELECT {', '.join(all_fields)}
                    FROM archived_content ac
                    LEFT JOIN conversation_quality_assessments cqa ON ac.id = cqa.conversation_id
                    WHERE ac.content_type = 'conversation' 
                        AND cqa.composite_score > 0.4
                        AND ac.word_count > 200
                    ORDER BY cqa.composite_score DESC
                    LIMIT 100
                """
                cursor.execute(query)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def _process_assessment_batch(self, task: AssessmentTask, conversations: List[Dict]) -> List[AssessmentResult]:
        """Process a batch of conversations for assessment"""
        
        batch_results = []
        
        for conversation in conversations:
            try:
                # Prepare conversation text (truncate if too long)
                conv_text = conversation.get('body_text', '')[:4000]
                
                # Fill template with conversation data
                prompt = task.llm_prompt_template.format(
                    conversation_text=conv_text,
                    **{key: conversation.get(key, 'N/A') for key in task.metadata_requirements}
                )
                
                # Get LLM assessment
                llm_response = self._get_llm_assessment(prompt)
                
                if llm_response:
                    # Parse LLM response
                    assessment_data = self._parse_llm_response(llm_response)
                    
                    # Calculate composite scores based on task criteria
                    composite_scores = self._calculate_composite_scores(assessment_data, task.assessment_criteria)
                    
                    # Create result
                    result = AssessmentResult(
                        task_id=task.task_id,
                        conversation_id=conversation['id'],
                        scores=composite_scores,
                        reasoning=assessment_data.get('reasoning', ''),
                        confidence=assessment_data.get('confidence', 0.7),
                        metadata_used={key: conversation.get(key) for key in task.metadata_requirements},
                        recommendations=assessment_data.get('recommended_uses', []) or assessment_data.get('editorial_improvements', []) or [],
                        timestamp=datetime.now()
                    )
                    
                    batch_results.append(result)
                
            except Exception as e:
                print(f"⚠️ Error processing conversation {conversation['id']}: {e}")
                continue
        
        return batch_results
    
    def _get_llm_assessment(self, prompt: str) -> Optional[str]:
        """Get assessment from LLM"""
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
        
        except Exception as e:
            print(f"⚠️ LLM request failed: {e}")
        
        return None
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        except json.JSONDecodeError:
            print(f"⚠️ Failed to parse LLM response as JSON: {response[:200]}...")
            return {}
    
    def _calculate_composite_scores(self, assessment_data: Dict, criteria: Dict) -> Dict[str, float]:
        """Calculate composite scores based on task criteria"""
        
        scores = {}
        
        # Extract numerical scores from assessment data
        numerical_scores = {k: v for k, v in assessment_data.items() if isinstance(v, (int, float)) and 0 <= v <= 1}
        
        # Calculate weighted composite if criteria weights are provided
        weighted_sum = 0
        total_weight = 0
        
        for score_name, weight in criteria.items():
            if score_name.endswith('_weight'):
                base_name = score_name.replace('_weight', '')
                if base_name in numerical_scores:
                    weighted_sum += numerical_scores[base_name] * weight
                    total_weight += weight
        
        if total_weight > 0:
            scores['composite'] = weighted_sum / total_weight
        
        # Include all individual scores
        scores.update(numerical_scores)
        
        return scores
    
    def _store_assessment_results(self, results: List[AssessmentResult]):
        """Store assessment results in database"""
        
        with psycopg2.connect(self.database_url) as conn:
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agentic_assessments (
                    id SERIAL PRIMARY KEY,
                    task_id VARCHAR(255),
                    conversation_id BIGINT,
                    task_type VARCHAR(100),
                    scores JSONB,
                    reasoning TEXT,
                    confidence REAL,
                    metadata_used JSONB,
                    recommendations JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Insert results
            for result in results:
                cursor.execute("""
                    INSERT INTO agentic_assessments 
                    (task_id, conversation_id, task_type, scores, reasoning, confidence, metadata_used, recommendations)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    result.task_id,
                    result.conversation_id,
                    result.task_id.split('_')[0],  # Extract task type
                    json.dumps(result.scores),
                    result.reasoning,
                    result.confidence,
                    json.dumps(result.metadata_used, default=str),
                    json.dumps(result.recommendations)
                ))
            
            conn.commit()
    
    def get_assessment_results(self, task_id: Optional[str] = None, 
                             task_type: Optional[str] = None,
                             min_score: Optional[float] = None) -> List[Dict]:
        """Retrieve assessment results with filtering"""
        
        with psycopg2.connect(self.database_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            
            conditions = []
            params = []
            
            if task_id:
                conditions.append("task_id = %s")
                params.append(task_id)
            
            if task_type:
                conditions.append("task_type = %s")
                params.append(task_type)
            
            if min_score:
                conditions.append("(scores->>'composite')::float >= %s")
                params.append(min_score)
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            query = f"""
                SELECT aa.*, ac.title, ac.category, ac.word_count
                FROM agentic_assessments aa
                JOIN archived_content ac ON aa.conversation_id = ac.id
                {where_clause}
                ORDER BY (aa.scores->>'composite')::float DESC NULLS LAST, aa.created_at DESC
            """
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def generate_assessment_report(self, results: List[AssessmentResult]) -> Dict[str, Any]:
        """Generate comprehensive assessment report"""
        
        if not results:
            return {}
        
        # Group by task type
        by_task_type = defaultdict(list)
        for result in results:
            task_type = result.task_id.split('_')[0]
            by_task_type[task_type].append(result)
        
        report = {
            'summary': {
                'total_assessments': len(results),
                'task_types': list(by_task_type.keys()),
                'avg_confidence': np.mean([r.confidence for r in results]),
                'date_range': {
                    'earliest': min(r.timestamp for r in results).isoformat(),
                    'latest': max(r.timestamp for r in results).isoformat()
                }
            },
            'by_task_type': {},
            'top_performers': [],
            'recommendations_summary': defaultdict(list)
        }
        
        # Analyze by task type
        for task_type, task_results in by_task_type.items():
            scores = [r.scores.get('composite', 0) for r in task_results if 'composite' in r.scores]
            
            report['by_task_type'][task_type] = {
                'count': len(task_results),
                'avg_score': np.mean(scores) if scores else 0,
                'score_distribution': {
                    'excellent': len([s for s in scores if s >= 0.8]),
                    'good': len([s for s in scores if 0.6 <= s < 0.8]),
                    'fair': len([s for s in scores if 0.4 <= s < 0.6]),
                    'poor': len([s for s in scores if s < 0.4])
                },
                'top_results': sorted(task_results, key=lambda r: r.scores.get('composite', 0), reverse=True)[:5]
            }
        
        # Top performers across all tasks
        all_with_composite = [r for r in results if 'composite' in r.scores]
        report['top_performers'] = sorted(all_with_composite, key=lambda r: r.scores['composite'], reverse=True)[:10]
        
        # Aggregate recommendations
        for result in results:
            for rec in result.recommendations:
                task_type = result.task_id.split('_')[0]
                report['recommendations_summary'][task_type].append(rec)
        
        return report

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Agentic Assessment Framework")
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Assess command
    assess_parser = subparsers.add_parser('assess', help='Run assessment task')
    assess_parser.add_argument('task_type', choices=['gem_detection', 'editorial_assessment', 'quality_enhancement', 
                                                   'topic_depth_analysis', 'narrative_potential', 'cross_conversation_patterns'])
    assess_parser.add_argument('--conversation-ids', nargs='+', type=int, help='Specific conversation IDs')
    assess_parser.add_argument('--batch-size', type=int, default=10, help='Batch size for processing')
    assess_parser.add_argument('--min-quality', type=float, help='Minimum quality threshold for auto-selection')
    
    # Results command
    results_parser = subparsers.add_parser('results', help='View assessment results')
    results_parser.add_argument('--task-id', help='Specific task ID')
    results_parser.add_argument('--task-type', help='Task type filter')
    results_parser.add_argument('--min-score', type=float, help='Minimum composite score')
    results_parser.add_argument('--report', action='store_true', help='Generate comprehensive report')
    
    args = parser.parse_args()
    
    assessor = AgenticAssessor()
    
    if args.command == 'assess':
        # Create and execute assessment task
        task = assessor.create_assessment_task(
            args.task_type,
            conversation_ids=args.conversation_ids,
            batch_size=args.batch_size
        )
        
        results = assessor.execute_assessment_task(task)
        
        # Show summary
        if results:
            print(f"\n📊 Assessment Results Summary:")
            scores = [r.scores.get('composite', 0) for r in results if 'composite' in r.scores]
            if scores:
                print(f"   Average Score: {np.mean(scores):.3f}")
                print(f"   Best Score: {max(scores):.3f}")
                print(f"   Score Range: {min(scores):.3f} - {max(scores):.3f}")
            
            # Show top results
            top_results = sorted(results, key=lambda r: r.scores.get('composite', 0), reverse=True)[:5]
            print(f"\n🏆 Top Results:")
            for i, result in enumerate(top_results):
                score = result.scores.get('composite', 0)
                print(f"   {i+1}. Conversation {result.conversation_id}: {score:.3f}")
    
    elif args.command == 'results':
        results_data = assessor.get_assessment_results(
            task_id=args.task_id,
            task_type=args.task_type,
            min_score=args.min_score
        )
        
        print(f"📊 Found {len(results_data)} assessment results")
        
        if args.report and results_data:
            # Convert to AssessmentResult objects for report generation
            assessment_results = []
            for data in results_data:
                assessment_results.append(AssessmentResult(
                    task_id=data['task_id'],
                    conversation_id=data['conversation_id'],
                    scores=data['scores'],
                    reasoning=data['reasoning'],
                    confidence=data['confidence'],
                    metadata_used=data['metadata_used'],
                    recommendations=data['recommendations'],
                    timestamp=data['created_at']
                ))
            
            report = assessor.generate_assessment_report(assessment_results)
            
            print("\n📊 Assessment Report:")
            print(f"   Total Assessments: {report['summary']['total_assessments']}")
            print(f"   Task Types: {', '.join(report['summary']['task_types'])}")
            print(f"   Average Confidence: {report['summary']['avg_confidence']:.3f}")
            
            print("\n🏆 Top Performers:")
            for i, result in enumerate(report['top_performers'][:5]):
                score = result.scores.get('composite', 0)
                print(f"   {i+1}. Conversation {result.conversation_id}: {score:.3f}")
        
        else:
            # Show results list
            for result in results_data[:20]:
                score = result['scores'].get('composite', 0)
                title = result.get('title', 'Untitled')[:50]
                print(f"   [{result['conversation_id']:5d}] {score:.3f} | {result['task_type']:15s} | {title}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()