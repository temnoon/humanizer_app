#!/usr/bin/env python3
"""
Test script for the Unified API v1 with real embeddings
"""

import requests
import json
import time
from typing import Dict, Any

API_BASE = "http://127.0.0.1:8101"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{API_BASE}/v1/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Version: {data['version']}")
        print(f"Embedding model: {data['capabilities']['embedding_models'][0]}")
        print(f"Embedding dim: {data['capabilities']['max_embedding_dim']}")
        print(f"Index vectors: {data['index_stats']['total_vectors']}")
    print()

def test_ingest():
    """Test document ingestion"""
    print("📥 Testing document ingestion...")
    
    request_data = {
        "source": {
            "kind": "conversation",
            "title": "Test Conversation",
            "provenance": {
                "platform": "TestSuite",
                "uri": "test://conversation/1",
                "captured_at": "2025-07-30T10:00:00Z"
            }
        },
        "document": {
            "mime": "application/json",
            "structure": {"type": "json"},
            "content": {
                "messages": [
                    {"role": "user", "text": "What is machine learning?"},
                    {"role": "assistant", "text": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to analyze data, identify patterns, and make predictions or decisions."},
                    {"role": "user", "text": "How does deep learning differ from traditional machine learning?"},
                    {"role": "assistant", "text": "Deep learning uses neural networks with multiple layers to automatically learn complex patterns in data. Unlike traditional machine learning, which requires manual feature engineering, deep learning can automatically extract relevant features from raw data. This makes it particularly effective for tasks like image recognition, natural language processing, and speech recognition."}
                ]
            }
        },
        "chunking": {
            "max_tokens": 400,
            "overlap_pct": 0.1
        }
    }
    
    response = requests.post(f"{API_BASE}/v1/ingest", json=request_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Document ID: {data['doc_id']}")
        print(f"Chunks created: {len(data['chunk_ids'])}")
        return data
    else:
        print(f"Error: {response.text}")
        return None
    print()

def test_embed(chunk_ids):
    """Test embedding generation"""
    print("🧠 Testing embedding generation...")
    
    request_data = {
        "chunk_ids": chunk_ids,
        "model": "all-mpnet-base-v2"
    }
    
    response = requests.post(f"{API_BASE}/v1/embed", json=request_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Embedded chunks: {data['embedded_count']}")
        print(f"Model used: {data['model']}")
        print(f"Embedding dimension: {data['dim']}")
        print(f"FAISS IDs: {data['faiss_ids']}")
        return data
    else:
        print(f"Error: {response.text}")
        return None
    print()

def test_attributes(chunk_ids):
    """Test attribute extraction"""
    print("🏷️ Testing attribute extraction...")
    
    request_data = {
        "chunk_ids": chunk_ids,
        "families": ["style_probe_v2", "persona_probe_v1", "namespace_probe_v1"]
    }
    
    response = requests.post(f"{API_BASE}/v1/attributes", json=request_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Attributes extracted: {len(data['attribute_ids'])}")
        print(f"Families used: {data['families_used']}")
        return data
    else:
        print(f"Error: {response.text}")
        return None
    print()

def test_kernel(chunk_ids):
    """Test kernel building"""
    print("⚛️ Testing kernel (ρ snapshot) building...")
    
    request_data = {
        "chunk_ids": chunk_ids,
        "aggregation": "weighted"
    }
    
    response = requests.post(f"{API_BASE}/v1/kernel", json=request_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Kernel ID: {data['kernel_id']}")
        print(f"Chunks used: {data['chunk_count']}")
        print(f"Attribute types: {data['attribute_types']}")
        return data
    else:
        print(f"Error: {response.text}")
        return None
    print()

def test_search():
    """Test vector search"""
    print("🔍 Testing vector search...")
    
    # Test text-based search
    request_data = {
        "text": "artificial intelligence and machine learning",
        "k": 5,
        "return_embeddings": False
    }
    
    response = requests.post(f"{API_BASE}/v1/search", json=request_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"Search results: {len(results)}")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. Chunk: {result['chunk_id']} (score: {result['similarity_score']:.3f})")
            print(f"     Preview: {result['text_preview'][:100]}...")
        return results
    else:
        print(f"Error: {response.text}")
        return None
    print()

def test_project(kernel_id):
    """Test narrative projection"""
    print("🎭 Testing narrative projection...")
    
    request_data = {
        "kernel_id": kernel_id,
        "constraints": {
            "namespace": "academic_review",
            "persona": "reviewer",
            "style": "concise",
            "length": "500-800 words"
        },
        "preserve_document_structure": True,
        "reproducibility": {
            "seed": 42,
            "models": {
                "llm": "mock-v1",
                "embed": "all-mpnet-base-v2"
            }
        }
    }
    
    response = requests.post(f"{API_BASE}/v1/project", json=request_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Projection ID: {data['projection_id']}")
        print(f"Sections: {len(data['render']['sections'])}")
        print(f"Kernel alignment: {data['faithfulness']['kernel_alignment']:.3f}")
        
        print("\nProjected content:")
        for section in data['render']['sections'][:2]:  # Show first 2 sections
            print(f"  Section {section['section_ref']}:")
            print(f"    {section['text'][:200]}...")
        
        return data
    else:
        print(f"Error: {response.text}")
        return None
    print()

def test_embedding_stats():
    """Test embedding statistics"""
    print("📊 Testing embedding statistics...")
    
    response = requests.get(f"{API_BASE}/v1/embedding-stats")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"Model: {stats['model_name']}")
        print(f"Dimension: {stats['embedding_dim']}")
        print(f"Total vectors: {stats['total_vectors']}")
        print(f"Index size: {stats['index_size_mb']:.2f} MB")
        return stats
    else:
        print(f"Error: {response.text}")
        return None
    print()

def run_full_pipeline_test():
    """Run complete pipeline test"""
    print("🚀 RUNNING FULL PIPELINE TEST")
    print("=" * 50)
    
    # Test health
    test_health()
    
    # Test ingest
    ingest_result = test_ingest()
    if not ingest_result:
        print("❌ Ingestion failed, stopping test")
        return
    
    chunk_ids = ingest_result['chunk_ids']
    
    # Test embedding
    embedding_result = test_embed(chunk_ids)
    if not embedding_result:
        print("❌ Embedding failed, stopping test")
        return
    
    # Test attributes
    attributes_result = test_attributes(chunk_ids)
    if not attributes_result:
        print("❌ Attribute extraction failed, stopping test")
        return
    
    # Test kernel
    kernel_result = test_kernel(chunk_ids)
    if not kernel_result:
        print("❌ Kernel building failed, stopping test")
        return
    
    kernel_id = kernel_result['kernel_id']
    
    # Test search
    search_result = test_search()
    
    # Test projection
    projection_result = test_project(kernel_id)
    
    # Test stats
    stats_result = test_embedding_stats()
    
    print("✅ PIPELINE TEST COMPLETE")
    print("=" * 50)
    
    return {
        "ingest": ingest_result,
        "embedding": embedding_result,
        "attributes": attributes_result,
        "kernel": kernel_result,
        "search": search_result,
        "projection": projection_result,
        "stats": stats_result
    }

if __name__ == "__main__":
    print("🧪 Unified API v1 Test Suite")
    print("Make sure the API server is running on port 8101")
    print()
    
    try:
        results = run_full_pipeline_test()
        print("\n🎉 All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Please start the server first:")
        print("   python unified_api_v1.py")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")