#!/usr/bin/env python3
"""
Pipeline Manager CLI - Formal interface to Content Pipeline API
Provides comprehensive pipeline management through API calls
"""

import requests
import json
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

class PipelineManager:
    """CLI interface to Content Pipeline API"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:7204"):
        self.api_base_url = api_base_url
        
        # Check API connectivity
        if not self._check_api_health():
            print("❌ Pipeline API is not running!")
            print("💡 Start it with: haw api start pipeline-api")
            sys.exit(1)
        
        print("🔄 Pipeline Manager CLI")
        print("======================")
    
    def _check_api_health(self) -> bool:
        """Check if Pipeline API is running"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make API request with error handling"""
        try:
            url = f"{self.api_base_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = requests.get(url, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code >= 400:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"❌ API Error ({response.status_code}): {error_detail}")
                return {}
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def list_rules(self):
        """List all pipeline rules"""
        print("📋 Pipeline Rules:")
        print("-" * 50)
        
        rules = self._make_request('GET', '/rules')
        
        if not rules:
            print("   No rules found")
            return
        
        for rule in rules:
            status = "🟢 Active" if rule['active'] else "🔴 Inactive"
            print(f"   {status} [{rule['priority']:2d}] {rule['name']}")
            print(f"      ID: {rule['rule_id']}")
            print(f"      Conditions: {self._format_conditions(rule['conditions'])}")
            print(f"      Transformations: {', '.join(rule['transformations'])}")
            print(f"      Destinations: {', '.join(rule['destinations'])}")
            print()
    
    def _format_conditions(self, conditions: Dict) -> str:
        """Format rule conditions for display"""
        formatted = []
        
        if 'min_quality' in conditions and conditions['min_quality'] is not None:
            formatted.append(f"quality >= {conditions['min_quality']}")
        
        if 'max_quality' in conditions and conditions['max_quality'] is not None:
            formatted.append(f"quality <= {conditions['max_quality']}")
        
        if 'min_words' in conditions and conditions['min_words'] is not None:
            formatted.append(f"words >= {conditions['min_words']}")
        
        if 'max_words' in conditions and conditions['max_words'] is not None:
            formatted.append(f"words <= {conditions['max_words']}")
        
        if 'category' in conditions and conditions['category']:
            formatted.append(f"category = {conditions['category']}")
        
        return ', '.join(formatted) if formatted else 'none'
    
    def create_rule(self, name: str, description: str, **conditions):
        """Create a new pipeline rule interactively"""
        print(f"🔧 Creating pipeline rule: {name}")
        
        # Get transformations
        print("\nAvailable transformations:")
        transformations = [
            "quality_enhancement", "structural_improvement", "tone_adjustment",
            "length_optimization", "audience_adaptation", "format_conversion"
        ]
        
        for i, t in enumerate(transformations, 1):
            print(f"  {i}. {t}")
        
        selected_transformations = []
        transform_input = input("\nSelect transformations (comma-separated numbers): ").strip()
        if transform_input:
            try:
                indices = [int(x.strip()) - 1 for x in transform_input.split(',')]
                selected_transformations = [transformations[i] for i in indices if 0 <= i < len(transformations)]
            except ValueError:
                print("⚠️ Invalid selection, using quality_enhancement as default")
                selected_transformations = ["quality_enhancement"]
        
        # Get destinations
        print("\nAvailable destinations:")
        destinations = [
            "humanizer_thread", "book_chapter", "discourse_post", 
            "blog_post", "social_media", "academic_paper", "newsletter"
        ]
        
        for i, d in enumerate(destinations, 1):
            print(f"  {i}. {d}")
        
        selected_destinations = []
        dest_input = input("\nSelect destinations (comma-separated numbers): ").strip()
        if dest_input:
            try:
                indices = [int(x.strip()) - 1 for x in dest_input.split(',')]
                selected_destinations = [destinations[i] for i in indices if 0 <= i < len(destinations)]
            except ValueError:
                print("⚠️ Invalid selection, using book_chapter as default")
                selected_destinations = ["book_chapter"]
        
        # Get priority
        priority = 50
        priority_input = input(f"\nPriority (1-100, default {priority}): ").strip()
        if priority_input:
            try:
                priority = int(priority_input)
                priority = max(1, min(100, priority))
            except ValueError:
                print(f"⚠️ Invalid priority, using {priority}")
        
        # Create rule data
        rule_data = {
            "name": name,
            "description": description,
            "conditions": {k: v for k, v in conditions.items() if v is not None},
            "transformations": selected_transformations,
            "destinations": selected_destinations,
            "priority": priority,
            "active": True
        }
        
        # Submit to API
        result = self._make_request('POST', '/rules', rule_data)
        
        if result:
            print(f"✅ Created rule: {result['name']} (ID: {result['rule_id']})")
        else:
            print("❌ Failed to create rule")
    
    def delete_rule(self, rule_id: str):
        """Delete a pipeline rule"""
        result = self._make_request('DELETE', f'/rules/{rule_id}')
        
        if result:
            print(f"✅ Deleted rule: {rule_id}")
        else:
            print(f"❌ Failed to delete rule: {rule_id}")
    
    def execute_pipeline(self, **kwargs):
        """Execute pipeline with specified parameters"""
        print("🚀 Executing pipeline...")
        
        # Prepare execution request
        request_data = {}
        
        if kwargs.get('conversation_ids'):
            request_data['conversation_ids'] = kwargs['conversation_ids']
        
        if kwargs.get('name'):
            request_data['name'] = kwargs['name']
        
        # Add filters if provided
        filters = {}
        if kwargs.get('min_quality') is not None:
            filters['min_quality'] = kwargs['min_quality']
        if kwargs.get('max_quality') is not None:
            filters['max_quality'] = kwargs['max_quality']
        if kwargs.get('category'):
            filters['category'] = kwargs['category']
        if kwargs.get('min_words') is not None:
            filters['min_words'] = kwargs['min_words']
        if kwargs.get('max_words') is not None:
            filters['max_words'] = kwargs['max_words']
        
        if filters:
            request_data['filters'] = filters
        
        if kwargs.get('limit'):
            request_data['limit'] = kwargs['limit']
        
        if kwargs.get('dry_run'):
            request_data['dry_run'] = True
        
        # Execute
        result = self._make_request('POST', '/execute', request_data)
        
        if result:
            execution_id = result['execution_id']
            print(f"✅ Started execution: {execution_id}")
            
            if result.get('status') == 'completed' and result.get('results', {}).get('dry_run'):
                # Dry run results
                print(f"📊 Dry run results:")
                print(f"   Would process: {result['results']['would_process']} conversations")
                print(f"   Preview IDs: {result['results']['preview']}")
            else:
                # Monitor execution
                self._monitor_execution(execution_id)
        else:
            print("❌ Failed to start execution")
    
    def _monitor_execution(self, execution_id: str):
        """Monitor pipeline execution progress"""
        print(f"📊 Monitoring execution: {execution_id}")
        
        while True:
            execution = self._make_request('GET', f'/executions/{execution_id}')
            
            if not execution:
                print("❌ Failed to get execution status")
                break
            
            status = execution['status']
            progress = execution.get('progress', {})
            
            if status in ['pending', 'running']:
                total = progress.get('total', 0)
                completed = progress.get('completed', 0)
                failed = progress.get('failed', 0)
                
                print(f"   Status: {status} - {completed}/{total} completed, {failed} failed")
                time.sleep(2)
                
            elif status == 'completed':
                results = execution.get('results', {})
                print(f"✅ Execution completed!")
                print(f"   Total processed: {results.get('total_processed', 0)}")
                print(f"   Successful: {results.get('successful', 0)}")
                print(f"   Failed: {results.get('failed', 0)}")
                break
                
            elif status == 'failed':
                error_msg = execution.get('error_message', 'Unknown error')
                print(f"❌ Execution failed: {error_msg}")
                break
                
            elif status == 'cancelled':
                print(f"⚠️ Execution was cancelled")
                break
    
    def list_executions(self, status: Optional[str] = None, limit: int = 10):
        """List pipeline executions"""
        print("📊 Pipeline Executions:")
        print("-" * 50)
        
        params = f"?limit={limit}"
        if status:
            params += f"&status={status}"
        
        executions = self._make_request('GET', f'/executions{params}')
        
        if not executions:
            print("   No executions found")
            return
        
        for exec_data in executions:
            status_emoji = {
                'pending': '⏳',
                'running': '🔄', 
                'completed': '✅',
                'failed': '❌',
                'cancelled': '⚠️'
            }.get(exec_data['status'], '❓')
            
            print(f"   {status_emoji} {exec_data['execution_id']}")
            
            if exec_data.get('name'):
                print(f"      Name: {exec_data['name']}")
            
            print(f"      Status: {exec_data['status']}")
            print(f"      Created: {exec_data['created_at']}")
            print(f"      Conversations: {len(exec_data['conversation_ids'])}")
            
            if exec_data.get('results'):
                results = exec_data['results']
                print(f"      Results: {results.get('successful', 0)} successful, {results.get('failed', 0)} failed")
            
            print()
    
    def show_stats(self):
        """Show pipeline system statistics"""
        print("📊 Pipeline System Statistics:")
        print("-" * 40)
        
        stats = self._make_request('GET', '/stats')
        
        if not stats:
            print("   Unable to retrieve statistics")
            return
        
        print(f"   Active Rules: {stats.get('active_rules', 0)}")
        print(f"   Current Executions: {stats.get('current_executions', 0)}")
        
        if 'execution_stats' in stats:
            exec_stats = stats['execution_stats']
            print(f"\n📈 Execution Stats (7 days):")
            print(f"   Total: {exec_stats.get('total_executions', 0)}")
            print(f"   Completed: {exec_stats.get('completed', 0)}")
            print(f"   Failed: {exec_stats.get('failed', 0)}")
            print(f"   Running: {exec_stats.get('running', 0)}")
        
        if 'destination_stats' in stats:
            dest_stats = stats['destination_stats']
            if dest_stats:
                print(f"\n📍 Destination Stats (7 days):")
                for dest, count in dest_stats.items():
                    print(f"   {dest}: {count}")

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Pipeline Manager - Formal API-based pipeline management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all pipeline rules
  python pipeline_manager.py rules list
  
  # Create a new rule
  python pipeline_manager.py rules create "High Quality Content" --min-quality 0.8
  
  # Execute pipeline with filters
  python pipeline_manager.py execute --min-quality 0.7 --limit 5
  
  # Dry run to preview what would be processed
  python pipeline_manager.py execute --min-quality 0.8 --dry-run
  
  # Monitor executions
  python pipeline_manager.py executions list
  
  # System statistics
  python pipeline_manager.py stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Rules management
    rules_parser = subparsers.add_parser('rules', help='Manage pipeline rules')
    rules_subparsers = rules_parser.add_subparsers(dest='rules_action', help='Rules actions')
    
    # List rules
    rules_subparsers.add_parser('list', help='List all pipeline rules')
    
    # Create rule
    create_rule_parser = rules_subparsers.add_parser('create', help='Create new pipeline rule')
    create_rule_parser.add_argument('name', help='Rule name')
    create_rule_parser.add_argument('--description', default='', help='Rule description')
    create_rule_parser.add_argument('--min-quality', type=float, help='Minimum quality score')
    create_rule_parser.add_argument('--max-quality', type=float, help='Maximum quality score')
    create_rule_parser.add_argument('--min-words', type=int, help='Minimum word count')
    create_rule_parser.add_argument('--max-words', type=int, help='Maximum word count')
    create_rule_parser.add_argument('--category', help='Content category')
    
    # Delete rule
    delete_rule_parser = rules_subparsers.add_parser('delete', help='Delete pipeline rule')
    delete_rule_parser.add_argument('rule_id', help='Rule ID to delete')
    
    # Pipeline execution
    exec_parser = subparsers.add_parser('execute', help='Execute pipeline')
    exec_parser.add_argument('--name', help='Execution name')
    exec_parser.add_argument('--conversation-ids', nargs='+', type=int, help='Specific conversation IDs')
    exec_parser.add_argument('--min-quality', type=float, help='Minimum quality score')
    exec_parser.add_argument('--max-quality', type=float, help='Maximum quality score')
    exec_parser.add_argument('--category', help='Category filter')
    exec_parser.add_argument('--min-words', type=int, help='Minimum word count')
    exec_parser.add_argument('--max-words', type=int, help='Maximum word count')
    exec_parser.add_argument('--limit', type=int, default=10, help='Limit conversations')
    exec_parser.add_argument('--dry-run', action='store_true', help='Preview without executing')
    
    # Executions management
    exec_list_parser = subparsers.add_parser('executions', help='Manage executions')
    exec_list_subparsers = exec_list_parser.add_subparsers(dest='exec_action', help='Execution actions')
    
    list_exec_parser = exec_list_subparsers.add_parser('list', help='List executions')
    list_exec_parser.add_argument('--status', help='Filter by status')
    list_exec_parser.add_argument('--limit', type=int, default=10, help='Limit results')
    
    # Statistics
    subparsers.add_parser('stats', help='Show system statistics')
    
    args = parser.parse_args()
    
    manager = PipelineManager()
    
    if args.command == 'rules':
        if args.rules_action == 'list':
            manager.list_rules()
        elif args.rules_action == 'create':
            manager.create_rule(
                name=args.name,
                description=args.description,
                min_quality=args.min_quality,
                max_quality=args.max_quality,
                min_words=args.min_words,
                max_words=args.max_words,
                category=args.category
            )
        elif args.rules_action == 'delete':
            manager.delete_rule(args.rule_id)
    
    elif args.command == 'execute':
        manager.execute_pipeline(
            name=args.name,
            conversation_ids=args.conversation_ids,
            min_quality=args.min_quality,
            max_quality=args.max_quality,
            category=args.category,
            min_words=args.min_words,
            max_words=args.max_words,
            limit=args.limit,
            dry_run=args.dry_run
        )
    
    elif args.command == 'executions':
        if args.exec_action == 'list':
            manager.list_executions(status=args.status, limit=args.limit)
    
    elif args.command == 'stats':
        manager.show_stats()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()