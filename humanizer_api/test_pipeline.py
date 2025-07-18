#!/usr/bin/env python3
"""
Test script for the complete Humanizer API pipeline
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from pipeline_integration import HumanizerPipelineClient, full_process, quick_assess

async def test_health():
    """Test service health"""
    print("🏥 Testing Service Health")
    print("=" * 50)
    
    client = HumanizerPipelineClient()
    health = await client.health_check_all()
    
    for service, status in health.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {service.upper()} API: {'Healthy' if status else 'Unavailable'}")
    
    all_healthy = all(health.values())
    print(f"\n{'🎉 All services healthy!' if all_healthy else '⚠️  Some services unavailable'}")
    return all_healthy

async def test_individual_services():
    """Test each service individually"""
    print("\n🧪 Testing Individual Services")
    print("=" * 50)
    
    client = HumanizerPipelineClient()
    
    test_content = """
    Artificial intelligence is rapidly transforming how we work and live. 
    This technology offers tremendous potential for solving complex problems, 
    but we must approach its development thoughtfully to ensure it benefits humanity.
    """
    
    # Test Archive API
    print("📚 Testing Archive API...")
    archive_result = await client.ingest_content(
        content=test_content.strip(),
        source="pipeline_test",
        title="Test Content for Pipeline"
    )
    
    if archive_result.success:
        content_id = archive_result.data.get("content_id")
        print(f"✅ Content ingested with ID: {content_id}")
    else:
        print(f"❌ Archive failed: {archive_result.error}")
    
    # Test LPE API
    print("\n🔄 Testing LPE API...")
    lpe_result = await client.transform_content(
        content=test_content.strip(),
        processing_type="projection"
    )
    
    if lpe_result.success:
        transformed = lpe_result.data.get("results", [{}])[0].get("output_content", "")
        print(f"✅ Content transformed: {transformed[:100]}...")
    else:
        print(f"❌ LPE failed: {lpe_result.error}")
    
    # Test Lawyer API
    print("\n⚖️ Testing Lawyer API...")
    lawyer_result = await client.assess_content(
        content=test_content.strip(),
        quality_threshold=0.7
    )
    
    if lawyer_result.success:
        assessment = lawyer_result.data
        scores = assessment.get("scores", {})
        result = assessment.get("result")
        print(f"✅ Assessment complete: {result}")
        print(f"   Overall score: {scores.get('overall', 0):.2f}")
        print(f"   Suggestions: {len(assessment.get('suggestions', []))}")
    else:
        print(f"❌ Lawyer failed: {lawyer_result.error}")

async def test_full_pipeline():
    """Test the complete pipeline"""
    print("\n🚀 Testing Full Pipeline")
    print("=" * 50)
    
    test_content = """
    The integration of AI systems into our daily workflows presents both opportunities 
    and challenges that require careful consideration. While these technologies can 
    enhance productivity and provide valuable insights, we must ensure they are 
    implemented in ways that support human agency and promote meaningful collaboration. 
    
    By focusing on transparency, ethical guidelines, and user-centric design, we can 
    harness the power of AI to create more effective and satisfying work experiences.
    """
    
    print("Processing content through full pipeline...")
    result = await full_process(test_content.strip(), source="full_pipeline_test")
    
    summary = result["summary"]
    print(f"\n{'🎉' if summary['pipeline_success'] else '⚠️'} Pipeline Result:")
    print(f"   Success: {summary['pipeline_success']}")
    print(f"   Stages completed: {', '.join(summary['stages_completed'])}")
    
    if summary["errors"]:
        print(f"   Errors: {'; '.join(summary['errors'])}")
    
    if summary["final_assessment"]:
        assessment = summary["final_assessment"]
        scores = assessment.get("scores", {})
        print(f"\n📊 Final Quality Assessment:")
        print(f"   Result: {assessment.get('result')}")
        print(f"   Overall Score: {scores.get('overall', 0):.2f}")
        print(f"   Clarity: {scores.get('clarity', 0):.2f}")
        print(f"   Coherence: {scores.get('coherence', 0):.2f}")
        print(f"   Tone: {scores.get('tone', 0):.2f}")
        
        suggestions = assessment.get("suggestions", [])
        if suggestions:
            print(f"\n💡 Improvement Suggestions ({len(suggestions)}):")
            for i, suggestion in enumerate(suggestions[:3]):  # Show first 3
                print(f"   {i+1}. {suggestion.get('description', 'N/A')}")

async def test_search_and_assess():
    """Test search and assess functionality"""
    print("\n🔍 Testing Search and Assessment")
    print("=" * 50)
    
    client = HumanizerPipelineClient()
    
    # First add some content to search
    test_contents = [
        "AI technology is revolutionizing healthcare with diagnostic improvements.",
        "Machine learning algorithms can help detect patterns in medical data.",
        "The future of artificial intelligence in education looks promising."
    ]
    
    print("Adding test content for search...")
    for i, content in enumerate(test_contents):
        await client.ingest_content(
            content=content,
            source=f"search_test_{i}",
            title=f"Test Article {i+1}"
        )
    
    print("\nSearching for 'artificial intelligence'...")
    results = await client.search_and_assess("artificial intelligence", limit=3)
    
    if "error" in results:
        print(f"❌ Search failed: {results['error']}")
    else:
        search_results = results.get("search_results", {})
        assessments = results.get("quality_assessments", [])
        
        print(f"✅ Found {len(search_results.get('results', []))} results")
        print(f"✅ Assessed {len(assessments)} items")
        
        for i, assessment in enumerate(assessments[:2]):  # Show first 2
            if assessment.get("assessment"):
                score = assessment["assessment"].get("scores", {}).get("overall", 0)
                result = assessment["assessment"].get("result", "unknown")
                print(f"   {i+1}. {assessment.get('title', 'Untitled')}: {result} ({score:.2f})")

async def show_pipeline_stats():
    """Show statistics from all services"""
    print("\n📈 Pipeline Statistics")
    print("=" * 50)
    
    client = HumanizerPipelineClient()
    stats = await client.get_pipeline_stats()
    
    for service, data in stats.items():
        print(f"\n{service.upper()} API:")
        if "error" in data:
            print(f"   ❌ {data['error']}")
        else:
            # Display key stats for each service
            if service == "archive":
                print(f"   Content items: {data.get('total_content', 0)}")
                print(f"   Sources: {data.get('total_sources', 0)}")
            elif service == "lpe":
                print(f"   Operations: {data.get('total_operations', 0)}")
                print(f"   Sessions: {data.get('total_sessions', 0)}")
            elif service == "lawyer":
                print(f"   Assessments: {data.get('total_assessments', 0)}")
                breakdown = data.get('results_breakdown', {})
                if breakdown:
                    print(f"   Approved: {breakdown.get('approved', 0)}")
                    print(f"   Needs improvement: {breakdown.get('needs_improvement', 0)}")
                    print(f"   Rejected: {breakdown.get('rejected', 0)}")

async def main():
    """Run all tests"""
    print("🧪 Humanizer API Pipeline Test Suite")
    print("=" * 60)
    
    # Check if services are healthy
    all_healthy = await test_health()
    
    if not all_healthy:
        print("\n⚠️  Some services are unavailable. Starting services...")
        print("Run: python smart_start.py")
        return
    
    # Run tests
    await test_individual_services()
    await test_full_pipeline()
    await test_search_and_assess()
    await show_pipeline_stats()
    
    print("\n🎉 Pipeline testing complete!")
    print("\nNext steps:")
    print("   • Test with your own content")
    print("   • Integrate with browser plugin")
    print("   • Connect to discourse platform")

if __name__ == "__main__":
    asyncio.run(main())