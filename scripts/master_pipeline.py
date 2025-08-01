#!/usr/bin/env python3
"""
Master Integration Pipeline
Coordinates all Humanizer automation tools for complete content workflows
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import yaml

class MasterPipeline:
    """Master pipeline coordinator for all Humanizer automation tools"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.scripts_dir = self.project_root / "scripts"
        self.exports_dir = self.project_root / "exports"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def check_dependencies(self) -> Dict[str, bool]:
        """Check availability of all pipeline components"""
        status = {}
        
        # Check Python scripts
        scripts_to_check = [
            'content_processor.py',
            'format_generator.py'
        ]
        
        for script in scripts_to_check:
            script_path = self.scripts_dir / script
            status[script] = script_path.exists() and os.access(script_path, os.X_OK)
        
        # Check bash scripts
        bash_scripts = [
            'export_book.sh',
            'organize_exports.sh'
        ]
        
        for script in bash_scripts:
            script_path = self.scripts_dir / script
            status[script] = script_path.exists() and os.access(script_path, os.X_OK)
        
        # Check CLI tools
        try:
            result = subprocess.run(['humanizer-archive', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            status['humanizer-archive'] = result.returncode == 0
        except:
            status['humanizer-archive'] = False
        
        # Check API health
        try:
            import requests
            response = requests.get("http://127.0.0.1:8100/health", timeout=5)
            status['lighthouse-api'] = response.status_code == 200
        except:
            status['lighthouse-api'] = False
        
        return status
    
    def full_content_pipeline(self, input_file: Path, 
                             persona: str = None,
                             namespace: str = None, 
                             style: str = None,
                             export_formats: List[str] = None,
                             publish: bool = False) -> Dict[str, Any]:
        """Run complete content processing pipeline"""
        
        results = {
            'pipeline_id': f"pipeline_{self.timestamp}",
            'input_file': str(input_file),
            'steps': [],
            'outputs': {},
            'timing': {'start': datetime.now().isoformat()}
        }
        
        if not input_file.exists():
            results['error'] = f"Input file not found: {input_file}"
            return results
        
        print(f"🚀 Starting Master Content Pipeline")
        print(f"   Input: {input_file}")
        print(f"   Pipeline ID: {results['pipeline_id']}")
        print(f"   Timestamp: {self.timestamp}")
        print()
        
        # Step 1: Content Processing (transformation)
        if persona or namespace or style:
            print("📝 Step 1: Content Transformation")
            try:
                cmd = [
                    'python', str(self.scripts_dir / 'content_processor.py'),
                    'process',
                    '--file', str(input_file)
                ]
                
                if persona:
                    cmd.extend(['--persona', persona])
                if namespace:
                    cmd.extend(['--namespace', namespace])
                if style:
                    cmd.extend(['--style', style])
                
                proc_result = subprocess.run(cmd, capture_output=True, text=True)
                
                if proc_result.returncode == 0:
                    results['steps'].append('✅ Content transformation successful')
                    results['outputs']['transformation'] = 'Generated transformed content'
                    print("   ✅ Content transformation complete")
                else:
                    results['steps'].append(f'❌ Content transformation failed: {proc_result.stderr}')
                    print(f"   ❌ Transformation failed: {proc_result.stderr}")
                    
            except Exception as e:
                results['steps'].append(f'❌ Content transformation error: {str(e)}')
                print(f"   ❌ Error: {str(e)}")
        else:
            print("⏭️  Step 1: Skipping transformation (no parameters provided)")
            results['steps'].append('⏭️ Content transformation skipped')
        
        print()
        
        # Step 2: Format Generation
        if export_formats:
            print("🔄 Step 2: Format Generation")
            try:
                cmd = [
                    'python', str(self.scripts_dir / 'format_generator.py'),
                    'convert',
                    '--file', str(input_file),
                    '--format', ','.join(export_formats)
                ]
                
                format_result = subprocess.run(cmd, capture_output=True, text=True)
                
                if format_result.returncode == 0:
                    results['steps'].append(f'✅ Format generation successful: {", ".join(export_formats)}')
                    results['outputs']['formats'] = export_formats
                    print(f"   ✅ Generated formats: {', '.join(export_formats)}")
                else:
                    results['steps'].append(f'❌ Format generation failed: {format_result.stderr}')
                    print(f"   ❌ Format generation failed: {format_result.stderr}")
                    
            except Exception as e:
                results['steps'].append(f'❌ Format generation error: {str(e)}')
                print(f"   ❌ Error: {str(e)}")
        else:
            print("⏭️  Step 2: Skipping format generation (no formats specified)")
            results['steps'].append('⏭️ Format generation skipped')
        
        print()
        
        # Step 3: Publishing Pipeline (if requested)
        if publish:
            print("📚 Step 3: Publishing Pipeline")
            try:
                # First, move to exports/books/drafts if not already there
                books_dir = self.exports_dir / "books" / "drafts"
                books_dir.mkdir(parents=True, exist_ok=True)
                
                draft_file = books_dir / input_file.name
                if not draft_file.exists():
                    import shutil
                    shutil.copy2(input_file, draft_file)
                    print(f"   📄 Copied to drafts: {draft_file}")
                
                # Use export_book.sh to promote through pipeline
                cmd = [
                    'bash', str(self.scripts_dir / 'export_book.sh'),
                    'promote', f"drafts/{input_file.name}"
                ]
                
                book_result = subprocess.run(cmd, capture_output=True, text=True)
                
                if book_result.returncode == 0:
                    results['steps'].append('✅ Publishing pipeline successful')
                    results['outputs']['published'] = True
                    print("   ✅ Publishing pipeline complete")
                    print(f"   {book_result.stdout}")
                else:
                    results['steps'].append(f'❌ Publishing pipeline failed: {book_result.stderr}')
                    print(f"   ❌ Publishing failed: {book_result.stderr}")
                    
            except Exception as e:
                results['steps'].append(f'❌ Publishing pipeline error: {str(e)}')
                print(f"   ❌ Error: {str(e)}")
        else:
            print("⏭️  Step 3: Skipping publishing pipeline")
            results['steps'].append('⏭️ Publishing pipeline skipped')
        
        print()
        
        # Step 4: Organization and Cleanup
        print("🗂️  Step 4: Organization")
        try:
            cmd = ['bash', str(self.scripts_dir / 'organize_exports.sh')]
            org_result = subprocess.run(cmd, capture_output=True, text=True)
            
            if org_result.returncode == 0:
                results['steps'].append('✅ Export organization successful')
                print("   ✅ Export organization complete")
            else:
                results['steps'].append(f'❌ Export organization failed: {org_result.stderr}')
                print(f"   ❌ Organization failed: {org_result.stderr}")
                
        except Exception as e:
            results['steps'].append(f'❌ Export organization error: {str(e)}')
            print(f"   ❌ Error: {str(e)}")
        
        print()
        
        # Finalize results
        results['timing']['end'] = datetime.now().isoformat()
        
        # Save pipeline results
        results_file = self.exports_dir / "archive" / f"master_pipeline_{self.timestamp}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📊 Pipeline Complete!")
        print(f"   Results saved: {results_file}")
        print(f"   Steps completed: {len([s for s in results['steps'] if s.startswith('✅')])}")
        print(f"   Steps failed: {len([s for s in results['steps'] if s.startswith('❌')])}")
        
        return results
    
    def batch_pipeline(self, input_dir: Path, 
                      persona: str = None,
                      namespace: str = None,
                      style: str = None,
                      export_formats: List[str] = None) -> Dict[str, Any]:
        """Run pipeline on all files in a directory"""
        
        if not input_dir.exists():
            return {'error': f'Input directory not found: {input_dir}'}
        
        # Find processable files
        file_patterns = ['*.md', '*.txt']
        files_to_process = []
        
        for pattern in file_patterns:
            files_to_process.extend(input_dir.glob(pattern))
        
        if not files_to_process:
            return {'error': 'No processable files found'}
        
        print(f"🔄 Batch Pipeline Processing")
        print(f"   Directory: {input_dir}")
        print(f"   Files found: {len(files_to_process)}")
        print()
        
        batch_results = {
            'batch_id': f"batch_{self.timestamp}",
            'input_dir': str(input_dir),
            'total_files': len(files_to_process),
            'processed': [],
            'failed': [],
            'timing': {'start': datetime.now().isoformat()}
        }
        
        for i, file_path in enumerate(files_to_process, 1):
            print(f"📄 Processing {i}/{len(files_to_process)}: {file_path.name}")
            
            result = self.full_content_pipeline(
                file_path,
                persona=persona,
                namespace=namespace,
                style=style,
                export_formats=export_formats,
                publish=False  # Don't publish in batch mode
            )
            
            if 'error' in result:
                batch_results['failed'].append({
                    'file': str(file_path),
                    'error': result['error']
                })
                print(f"   ❌ Failed: {file_path.name}")
            else:
                batch_results['processed'].append({
                    'file': str(file_path),
                    'pipeline_id': result['pipeline_id'],
                    'steps_completed': len([s for s in result['steps'] if s.startswith('✅')])
                })
                print(f"   ✅ Success: {file_path.name}")
            
            print()
        
        batch_results['timing']['end'] = datetime.now().isoformat()
        
        # Save batch results
        results_file = self.exports_dir / "archive" / f"batch_pipeline_{self.timestamp}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(batch_results, f, indent=2)
        
        print(f"📊 Batch Pipeline Complete!")
        print(f"   Processed: {len(batch_results['processed'])}/{batch_results['total_files']} files")
        print(f"   Failed: {len(batch_results['failed'])} files")
        print(f"   Results saved: {results_file}")
        
        return batch_results


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Master Integration Pipeline for Humanizer Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline for single file
  python master_pipeline.py single --file essay.md --persona philosopher --formats html,pdf --publish
  
  # Batch process directory
  python master_pipeline.py batch --dir drafts/essays/ --persona scientist --formats html,pdf
  
  # Check system status
  python master_pipeline.py status
  
  # Transform and format only
  python master_pipeline.py single --file content.md --persona artist --formats html
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Pipeline commands')
    
    # Single file pipeline
    single_parser = subparsers.add_parser('single', help='Process single file')
    single_parser.add_argument('--file', type=Path, required=True, help='Input file')
    single_parser.add_argument('--persona', help='Persona for transformation')
    single_parser.add_argument('--namespace', help='Namespace for transformation')
    single_parser.add_argument('--style', help='Style for transformation')
    single_parser.add_argument('--formats', help='Export formats (comma-separated)')
    single_parser.add_argument('--publish', action='store_true', help='Run through publishing pipeline')
    
    # Batch pipeline
    batch_parser = subparsers.add_parser('batch', help='Process directory')
    batch_parser.add_argument('--dir', type=Path, required=True, help='Input directory')
    batch_parser.add_argument('--persona', help='Persona for transformation')
    batch_parser.add_argument('--namespace', help='Namespace for transformation')
    batch_parser.add_argument('--style', help='Style for transformation')
    batch_parser.add_argument('--formats', help='Export formats (comma-separated)')
    
    # Status check
    status_parser = subparsers.add_parser('status', help='Check pipeline status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    pipeline = MasterPipeline()
    
    if args.command == 'status':
        print("🔍 Checking Humanizer Pipeline Status")
        print("=" * 50)
        
        status = pipeline.check_dependencies()
        
        for component, available in status.items():
            status_icon = "✅" if available else "❌"
            print(f"{status_icon} {component}")
        
        all_ready = all(status.values())
        print()
        print(f"Overall Status: {'✅ Ready' if all_ready else '❌ Some components unavailable'}")
        
        if not all_ready:
            print("\n💡 To fix missing components:")
            if not status.get('lighthouse-api', False):
                print("   - Start API: cd humanizer_api/lighthouse && python api_enhanced.py")
            if not status.get('humanizer-archive', False):  
                print("   - Install CLI: pip install -e humanizer_api/lighthouse/")
    
    elif args.command == 'single':
        formats = args.formats.split(',') if args.formats else None
        
        result = pipeline.full_content_pipeline(
            args.file,
            persona=args.persona,
            namespace=args.namespace,
            style=args.style,
            export_formats=formats,
            publish=args.publish
        )
        
        if 'error' in result:
            print(f"❌ Pipeline failed: {result['error']}")
            sys.exit(1)
    
    elif args.command == 'batch':
        formats = args.formats.split(',') if args.formats else None
        
        result = pipeline.batch_pipeline(
            args.dir,
            persona=args.persona,
            namespace=args.namespace,
            style=args.style,
            export_formats=formats
        )
        
        if 'error' in result:
            print(f"❌ Batch pipeline failed: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()