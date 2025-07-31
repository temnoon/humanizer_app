#!/usr/bin/env python3
"""
Native Humanizer Conversation Format
====================================

Comprehensive format for enriched conversations with AI projections,
translations, and pipelined interpretations. This becomes the foundation
for thread-based social.humanizer.com and Discourse integration.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import uuid

from attribute_taxonomy import AttributeCollection, HumanReadableAttribute


class MessageRole(str, Enum):
    """Message roles in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    NARRATOR = "narrator"  # For Lamish projections


class TransformationType(str, Enum):
    """Types of AI transformations"""
    PHILOSOPHICAL_PROJECTION = "philosophical_projection"
    ACADEMIC_SUMMARY = "academic_summary"
    POETIC_RENDERING = "poetic_rendering"
    SCIENTIFIC_ANALYSIS = "scientific_analysis"
    CULTURAL_TRANSLATION = "cultural_translation"
    HISTORICAL_CONTEXTUALIZATION = "historical_contextualization"
    LAMISH_VEIL = "lamish_veil"  # Public-facing transformation


class InterpretationLayer(str, Enum):
    """Levels of interpretation processing"""
    SURFACE = "surface"           # Direct content
    SEMANTIC = "semantic"         # Meaning extraction
    PRAGMATIC = "pragmatic"       # Context and intent
    HERMENEUTIC = "hermeneutic"   # Deep interpretation
    PHENOMENOLOGICAL = "phenomenological"  # Consciousness exploration


class NativeMessage(BaseModel):
    """Enhanced message with AI projections and interpretations"""
    
    # Core message data
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Original message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Message metadata
    author: Optional[str] = Field(None, description="Message author")
    word_count: int = Field(0, description="Word count")
    character_count: int = Field(0, description="Character count")
    
    # AI Projections and Transformations
    projections: Dict[TransformationType, Dict[str, Any]] = Field(default_factory=dict)
    interpretations: Dict[InterpretationLayer, str] = Field(default_factory=dict)
    
    # Narrative attributes for this message
    extracted_attributes: Optional[AttributeCollection] = Field(None)
    
    # Cross-references and connections
    references_to: List[str] = Field(default_factory=list, description="Message IDs this references")
    referenced_by: List[str] = Field(default_factory=list, description="Message IDs that reference this")
    
    # Quality and processing metadata
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
    quality_score: float = Field(0.0, ge=0.0, le=1.0)
    
    def add_projection(self, transformation_type: TransformationType, result: Dict[str, Any]):
        """Add an AI projection/transformation result"""
        self.projections[transformation_type] = {
            "narrative": result.get("projection", {}).get("narrative", ""),
            "reflection": result.get("projection", {}).get("reflection", ""),
            "created_at": datetime.now().isoformat(),
            "confidence": result.get("confidence", 0.0),
            "processing_steps": result.get("steps", [])
        }
    
    def add_interpretation(self, layer: InterpretationLayer, interpretation: str):
        """Add an interpretation at a specific layer"""
        self.interpretations[layer] = interpretation
    
    def get_best_projection_for_public(self) -> Optional[Dict[str, Any]]:
        """Get the best projection for public consumption (Lamish veil)"""
        if TransformationType.LAMISH_VEIL in self.projections:
            return self.projections[TransformationType.LAMISH_VEIL]
        elif TransformationType.PHILOSOPHICAL_PROJECTION in self.projections:
            return self.projections[TransformationType.PHILOSOPHICAL_PROJECTION]
        return None


class ConversationThread(BaseModel):
    """Thread of messages with collective analysis"""
    
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Thread title")
    messages: List[NativeMessage] = Field(default_factory=list)
    
    # Thread-level metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    participant_count: int = Field(0)
    total_word_count: int = Field(0)
    
    def add_message(self, message: NativeMessage):
        """Add a message to the thread"""
        self.messages.append(message)
        self.last_updated = datetime.now()
        self.total_word_count += message.word_count
        
        # Update participant count
        authors = set(msg.author for msg in self.messages if msg.author)
        self.participant_count = len(authors)


class NativeConversation(BaseModel):
    """Complete native conversation format with all enrichments"""
    
    # Core identification
    conversation_id: str = Field(..., description="Unique conversation identifier")
    original_source_id: str = Field(..., description="Original archive source ID")
    title: str = Field(..., description="Conversation title")
    
    # Conversation structure
    threads: List[ConversationThread] = Field(default_factory=list)
    main_thread: Optional[ConversationThread] = Field(None)
    
    # Conversation metadata
    created_at: datetime = Field(..., description="Original creation time")
    processed_at: datetime = Field(default_factory=datetime.now)
    source_type: str = Field("archive", description="Source system type")
    
    # Participant information
    participants: List[str] = Field(default_factory=list)
    primary_author: Optional[str] = Field(None)
    
    # Content statistics
    total_messages: int = Field(0)
    total_word_count: int = Field(0)
    average_message_length: float = Field(0.0)
    
    # AI Analysis Results
    conversation_attributes: Optional[AttributeCollection] = Field(None)
    dominant_themes: List[str] = Field(default_factory=list)
    conversation_quality_score: float = Field(0.0, ge=0.0, le=1.0)
    
    # Collective transformations (conversation-level projections)
    conversation_projections: Dict[TransformationType, Dict[str, Any]] = Field(default_factory=dict)
    
    # Essay and publication potential
    essay_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    publication_readiness: Dict[str, float] = Field(default_factory=dict)
    
    # Book compilation metadata
    subject_classifications: List[str] = Field(default_factory=list)
    chapter_potential: Dict[str, float] = Field(default_factory=dict)
    
    # Discourse integration metadata
    discourse_thread_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    public_sharing_score: float = Field(0.0, ge=0.0, le=1.0)
    
    def add_thread(self, thread: ConversationThread):
        """Add a thread to the conversation"""
        self.threads.append(thread)
        if not self.main_thread:
            self.main_thread = thread
        self._update_statistics()
    
    def add_conversation_projection(self, transformation_type: TransformationType, result: Dict[str, Any]):
        """Add a conversation-level projection"""
        self.conversation_projections[transformation_type] = {
            "narrative": result.get("projection", {}).get("narrative", ""),
            "reflection": result.get("projection", {}).get("reflection", ""),
            "created_at": datetime.now().isoformat(),
            "conversation_id": self.conversation_id,
            "word_count": len(result.get("projection", {}).get("narrative", "").split()),
            "quality_indicators": result.get("quality_indicators", {})
        }
    
    def assess_essay_potential(self) -> Dict[str, Any]:
        """Assess potential for essay creation"""
        criteria = {
            "length_score": min(1.0, self.total_word_count / 1500),  # Target ~1500 words
            "coherence_score": self.conversation_quality_score,
            "projection_quality": max([
                proj.get("quality_indicators", {}).get("overall_quality", 0.0)
                for proj in self.conversation_projections.values()
            ] + [0.0]),
            "theme_clarity": len(self.dominant_themes) / 5.0,  # Expect ~5 themes
            "participant_engagement": min(1.0, self.participant_count / 3.0)
        }
        
        overall_score = sum(criteria.values()) / len(criteria)
        
        return {
            "overall_essay_score": overall_score,
            "criteria_breakdown": criteria,
            "recommended_transformations": self._recommend_essay_transformations(),
            "target_audience": self._identify_target_audience(),
            "estimated_reading_time": self.total_word_count / 250  # 250 WPM average
        }
    
    def assess_book_chapter_potential(self, subject_area: str) -> Dict[str, Any]:
        """Assess potential as a chapter in a subject-area book"""
        relevance_score = self._calculate_subject_relevance(subject_area)
        
        criteria = {
            "subject_relevance": relevance_score,
            "chapter_length_appropriateness": self._assess_chapter_length(),
            "standalone_readability": self.conversation_quality_score,
            "educational_value": self._assess_educational_value(),
            "narrative_flow": self._assess_narrative_continuity()
        }
        
        return {
            "chapter_suitability_score": sum(criteria.values()) / len(criteria),
            "criteria_breakdown": criteria,
            "recommended_chapter_title": self._generate_chapter_title(subject_area),
            "integration_suggestions": self._suggest_chapter_integration(subject_area)
        }
    
    def assess_discourse_publication_potential(self) -> Dict[str, Any]:
        """Assess potential for Discourse publication"""
        criteria = {
            "public_interest": self._assess_public_interest(),
            "accessibility": self._assess_public_accessibility(),
            "controversy_level": self._assess_controversy_level(),
            "educational_value": self._assess_educational_value(),
            "lamish_veil_effectiveness": self._assess_lamish_veil_quality()
        }
        
        return {
            "publication_readiness_score": sum(criteria.values()) / len(criteria),
            "criteria_breakdown": criteria,
            "recommended_discourse_category": self._recommend_discourse_category(),
            "content_warnings": self._identify_content_warnings(),
            "engagement_predictions": self._predict_engagement_metrics()
        }
    
    def _update_statistics(self):
        """Update conversation statistics"""
        all_messages = []
        for thread in self.threads:
            all_messages.extend(thread.messages)
        
        self.total_messages = len(all_messages)
        self.total_word_count = sum(msg.word_count for msg in all_messages)
        if self.total_messages > 0:
            self.average_message_length = self.total_word_count / self.total_messages
        
        # Update participants
        participants = set()
        for msg in all_messages:
            if msg.author:
                participants.add(msg.author)
        self.participants = list(participants)
    
    def _recommend_essay_transformations(self) -> List[str]:
        """Recommend transformation types for essay creation"""
        recommendations = []
        
        if "philosophy" in self.dominant_themes:
            recommendations.append(TransformationType.PHILOSOPHICAL_PROJECTION)
        if "science" in self.dominant_themes:
            recommendations.append(TransformationType.SCIENTIFIC_ANALYSIS)
        if any(theme in ["culture", "society"] for theme in self.dominant_themes):
            recommendations.append(TransformationType.CULTURAL_TRANSLATION)
        
        # Always recommend Lamish veil for public consumption
        recommendations.append(TransformationType.LAMISH_VEIL)
        
        return recommendations
    
    def _identify_target_audience(self) -> str:
        """Identify target audience for this conversation"""
        if self.conversation_quality_score > 0.8:
            return "academic_researchers"
        elif self.conversation_quality_score > 0.6:
            return "educated_general_public"
        else:
            return "general_public"
    
    def _calculate_subject_relevance(self, subject_area: str) -> float:
        """Calculate relevance to a subject area"""
        # This would use more sophisticated matching in practice
        theme_matches = sum(1 for theme in self.dominant_themes 
                           if subject_area.lower() in theme.lower())
        return min(1.0, theme_matches / len(self.dominant_themes)) if self.dominant_themes else 0.0
    
    def _assess_chapter_length(self) -> float:
        """Assess appropriateness of length for a book chapter"""
        ideal_length = 3000  # ~3000 words per chapter
        return max(0.0, 1.0 - abs(self.total_word_count - ideal_length) / ideal_length)
    
    def _assess_educational_value(self) -> float:
        """Assess educational value of the conversation"""
        # Placeholder - would use more sophisticated analysis
        return min(1.0, (self.conversation_quality_score + len(self.dominant_themes) / 10.0) / 2.0)
    
    def _assess_narrative_continuity(self) -> float:
        """Assess narrative flow and continuity"""
        # Placeholder - would analyze message connections and flow
        return self.conversation_quality_score  # Simplified
    
    def _generate_chapter_title(self, subject_area: str) -> str:
        """Generate a chapter title for the given subject area"""
        return f"{self.title} - A {subject_area} Perspective"
    
    def _suggest_chapter_integration(self, subject_area: str) -> List[str]:
        """Suggest how to integrate this as a chapter"""
        return [
            f"Place in {subject_area} section",
            "Add cross-references to related concepts",
            "Include discussion questions",
            "Provide supplementary reading suggestions"
        ]
    
    def _assess_public_interest(self) -> float:
        """Assess likely public interest level"""
        popular_themes = ["ai", "consciousness", "future", "technology", "philosophy"]
        interest_score = sum(1 for theme in self.dominant_themes 
                           if any(popular in theme.lower() for popular in popular_themes))
        return min(1.0, interest_score / 3.0)
    
    def _assess_public_accessibility(self) -> float:
        """Assess how accessible the content is to general public"""
        # Higher quality score often means more complex content
        # So we inverse this for accessibility
        return max(0.3, 1.0 - (self.conversation_quality_score - 0.5))
    
    def _assess_controversy_level(self) -> float:
        """Assess potential controversy level"""
        # Placeholder - would analyze content for controversial topics
        return 0.3  # Default moderate level
    
    def _assess_lamish_veil_quality(self) -> float:
        """Assess quality of Lamish veil transformation"""
        if TransformationType.LAMISH_VEIL in self.conversation_projections:
            return self.conversation_projections[TransformationType.LAMISH_VEIL].get(
                "quality_indicators", {}
            ).get("overall_quality", 0.0)
        return 0.0
    
    def _recommend_discourse_category(self) -> str:
        """Recommend Discourse category for publication"""
        if "philosophy" in self.dominant_themes:
            return "Philosophy & Ideas"
        elif "science" in self.dominant_themes:
            return "Science & Technology"
        elif "ai" in [theme.lower() for theme in self.dominant_themes]:
            return "AI & Future"
        else:
            return "General Discussion"
    
    def _identify_content_warnings(self) -> List[str]:
        """Identify potential content warnings"""
        warnings = []
        # This would analyze content for potentially sensitive topics
        return warnings
    
    def _predict_engagement_metrics(self) -> Dict[str, float]:
        """Predict engagement metrics for Discourse publication"""
        return {
            "expected_views": self._assess_public_interest() * 1000,
            "expected_replies": self._assess_public_interest() * 50,
            "expected_likes": self.conversation_quality_score * 100
        }


class ConversationCollection(BaseModel):
    """Collection of native conversations for batch processing"""
    
    collection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Collection name")
    conversations: List[NativeConversation] = Field(default_factory=list)
    
    # Collection metadata
    created_at: datetime = Field(default_factory=datetime.now)
    total_conversations: int = Field(0)
    total_word_count: int = Field(0)
    
    # Curation criteria
    subject_focus: Optional[str] = Field(None)
    quality_threshold: float = Field(0.5)
    target_transformations: List[TransformationType] = Field(default_factory=list)
    
    def add_conversation(self, conversation: NativeConversation):
        """Add a conversation to the collection"""
        self.conversations.append(conversation)
        self.total_conversations += 1
        self.total_word_count += conversation.total_word_count
    
    def filter_by_quality(self, min_quality: float = 0.7) -> List[NativeConversation]:
        """Filter conversations by quality score"""
        return [conv for conv in self.conversations 
                if conv.conversation_quality_score >= min_quality]
    
    def group_by_subject(self) -> Dict[str, List[NativeConversation]]:
        """Group conversations by subject classification"""
        groups = {}
        for conv in self.conversations:
            for subject in conv.subject_classifications:
                if subject not in groups:
                    groups[subject] = []
                groups[subject].append(conv)
        return groups
    
    def get_essay_candidates(self, min_score: float = 0.7) -> List[Dict[str, Any]]:
        """Get conversations suitable for essay creation"""
        candidates = []
        for conv in self.conversations:
            essay_assessment = conv.assess_essay_potential()
            if essay_assessment["overall_essay_score"] >= min_score:
                candidates.append({
                    "conversation": conv,
                    "assessment": essay_assessment
                })
        return candidates
    
    def get_book_chapter_candidates(self, subject_area: str, min_score: float = 0.6) -> List[Dict[str, Any]]:
        """Get conversations suitable for book chapters in a subject area"""
        candidates = []
        for conv in self.conversations:
            chapter_assessment = conv.assess_book_chapter_potential(subject_area)
            if chapter_assessment["chapter_suitability_score"] >= min_score:
                candidates.append({
                    "conversation": conv,
                    "assessment": chapter_assessment
                })
        return candidates
    
    def get_discourse_publication_candidates(self, min_score: float = 0.6) -> List[Dict[str, Any]]:
        """Get conversations suitable for Discourse publication"""
        candidates = []
        for conv in self.conversations:
            publication_assessment = conv.assess_discourse_publication_potential()
            if publication_assessment["publication_readiness_score"] >= min_score:
                candidates.append({
                    "conversation": conv,
                    "assessment": publication_assessment
                })
        return candidates


# Factory functions for creating native conversations from archive data

def create_native_conversation_from_archive(archive_data: Dict[str, Any], 
                                          processing_results: Optional[Dict[str, Any]] = None) -> NativeConversation:
    """Create a native conversation from archive data"""
    
    conversation = NativeConversation(
        conversation_id=str(uuid.uuid4()),
        original_source_id=str(archive_data.get('conversation', {}).get('id', 'unknown')),
        title=archive_data.get('conversation', {}).get('title', 'Untitled'),
        created_at=datetime.fromisoformat(
            archive_data.get('conversation', {}).get('timestamp', datetime.now().isoformat())
        ),
        primary_author=archive_data.get('conversation', {}).get('author')
    )
    
    # Create main thread
    main_thread = ConversationThread(
        title=f"Main Thread: {conversation.title}"
    )
    
    # Process messages
    for msg_data in archive_data.get('messages', []):
        message = NativeMessage(
            role=MessageRole(msg_data.get('role', 'user')),
            content=msg_data.get('content', msg_data.get('body_text', '')),
            author=msg_data.get('author'),
            word_count=len(msg_data.get('content', '').split()),
            character_count=len(msg_data.get('content', ''))
        )
        
        if msg_data.get('timestamp'):
            message.timestamp = datetime.fromisoformat(msg_data['timestamp'])
        
        main_thread.add_message(message)
    
    conversation.add_thread(main_thread)
    
    # Add processing results if available
    if processing_results:
        if 'extracted_attributes' in processing_results:
            conversation.conversation_attributes = processing_results['extracted_attributes']
        
        if 'transformations' in processing_results:
            for transform_name, transform_result in processing_results['transformations'].items():
                if transform_name == 'philosophical_projection':
                    conversation.add_conversation_projection(
                        TransformationType.PHILOSOPHICAL_PROJECTION, 
                        transform_result
                    )
                elif transform_name == 'academic_summary':
                    conversation.add_conversation_projection(
                        TransformationType.ACADEMIC_SUMMARY,
                        transform_result
                    )
        
        if 'validation_results' in processing_results:
            conversation.conversation_quality_score = processing_results['validation_results'].get(
                'confidence_score', 0.0
            )
    
    return conversation


if __name__ == "__main__":
    # Example usage
    sample_archive_data = {
        "conversation": {
            "id": 203110,
            "title": "Introduction to GAT Formalisms",
            "author": "user",
            "timestamp": "2024-09-14T00:43:55"
        },
        "messages": [
            {
                "role": "user",
                "content": "Give me a gentle introduction to the formalisms of GAT...",
                "author": "user",
                "timestamp": "2024-09-14T00:43:55"
            },
            {
                "role": "assistant", 
                "content": "General Agent Theory (GAT) provides a framework...",
                "author": "assistant",
                "timestamp": "2024-09-14T00:44:13"
            }
        ]
    }
    
    native_conv = create_native_conversation_from_archive(sample_archive_data)
    print("Created native conversation:")
    print(f"ID: {native_conv.conversation_id}")
    print(f"Title: {native_conv.title}")
    print(f"Messages: {native_conv.total_messages}")
    print(f"Word count: {native_conv.total_word_count}")
    
    # Assess various potentials
    essay_potential = native_conv.assess_essay_potential()
    print(f"Essay potential score: {essay_potential['overall_essay_score']:.2f}")
    
    chapter_potential = native_conv.assess_book_chapter_potential("Computer Science")
    print(f"Chapter potential score: {chapter_potential['chapter_suitability_score']:.2f}")
    
    discourse_potential = native_conv.assess_discourse_publication_potential()
    print(f"Discourse publication score: {discourse_potential['publication_readiness_score']:.2f}")