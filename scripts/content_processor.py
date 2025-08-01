#!/usr/bin/env python3
"""
Automated Content Processing Workflow
Integrates with Humanizer CLI for batch processing and content transformation
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

class ContentProcessor:
    """Automated content processing and transformation system"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.exports_dir = self.project_root / "exports"
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_processing_config(self) -> Dict[str, Any]:
        """Load processing configuration from YAML"""
        config_file = self.config_dir / "templates" / "processing_config.yaml"
        
        if not config_file.exists():
            # Create default config
            default_config = {
                'personas': {
                    'default': 'philosopher',
                    'scientific': 'scientist',
                    'creative': 'artist',
                    'analytical': 'critic'
                },
                'namespaces': {
                    'default': 'classical_literature',
                    'modern': 'natural_world',
                    'futuristic': 'cyberpunk_future'
                },
                'styles': {
                    'default': 'formal',
                    'academic': 'academic',
                    'casual': 'casual',
                    'poetic': 'poetic'
                },
                'batch_settings': {
                    'max_concurrent': 3,
                    'timeout_seconds': 300,
                    'preserve_originals': True
                }
            }
            
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
                
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def process_file(self, input_file: Path, persona: str = None, 
                    namespace: str = None, style: str = None, 
                    output_dir: Path = None) -> Dict[str, Any]:
        """Process a single file through humanizer transformation"""
        
        if not input_file.exists():
            return {'error': f'Input file not found: {input_file}'}
        
        config = self.load_processing_config()
        
        # Use defaults if not specified
        persona = persona or config['personas']['default']
        namespace = namespace or config['namespaces']['default'] 
        style = style or config['styles']['default']
        
        # Determine output location
        if output_dir is None:
            output_dir = self.exports_dir / "transformations"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename
        input_stem = input_file.stem
        output_file = output_dir / f"{self.timestamp}_{input_stem}_{persona}.txt"
        
        try:
            # Build humanizer command
            cmd = [
                "humanizer-archive", "transform",
                "--file", str(input_file),
                "--persona", persona,
                "--namespace", namespace,
                "--style", style,
                "--output", str(output_file)
            ]
            
            print(f"🔄 Processing: {input_file.name}")
            print(f"   Persona: {persona}, Namespace: {namespace}, Style: {style}")
            
            # Execute transformation
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'input_file': str(input_file),
                    'output_file': str(output_file),
                    'persona': persona,
                    'namespace': namespace,
                    'style': style,
                    'timestamp': self.timestamp
                }
            else:
                return {
                    'error': f'Transformation failed: {result.stderr}',
                    'input_file': str(input_file)
                }
                
        except subprocess.TimeoutExpired:
            return {
                'error': 'Transformation timed out',
                'input_file': str(input_file)
            }
        except Exception as e:
            return {
                'error': f'Processing error: {str(e)}',
                'input_file': str(input_file)
            }
    
    def batch_process_directory(self, input_dir: Path, 
                               persona_mapping: Dict[str, str] = None,
                               output_dir: Path = None) -> Dict[str, Any]:
        """Batch process all files in a directory"""
        
        if not input_dir.exists():
            return {'error': f'Input directory not found: {input_dir}'}
        
        # Find all processable files
        file_patterns = ['*.md', '*.txt']
        files_to_process = []
        
        for pattern in file_patterns:
            files_to_process.extend(input_dir.glob(pattern))
        
        if not files_to_process:
            return {'error': 'No processable files found in directory'}
        
        print(f"📦 Batch processing {len(files_to_process)} files from {input_dir}")
        
        results = {
            'processed': [],
            'failed': [],
            'summary': {
                'total_files': len(files_to_process),
                'successful': 0,
                'failed': 0,
                'start_time': datetime.now().isoformat()
            }
        }
        
        for file_path in files_to_process:
            # Determine persona for this file (could be based on filename, directory, etc.)
            persona = None
            if persona_mapping:
                for pattern, mapped_persona in persona_mapping.items():
                    if pattern in file_path.name.lower():
                        persona = mapped_persona
                        break
            
            # Process the file
            result = self.process_file(file_path, persona=persona, output_dir=output_dir)
            
            if 'error' in result:
                results['failed'].append(result)
                results['summary']['failed'] += 1
                print(f"❌ Failed: {file_path.name} - {result['error']}")
            else:
                results['processed'].append(result)
                results['summary']['successful'] += 1
                print(f"✅ Success: {file_path.name} → {Path(result['output_file']).name}")
        
        results['summary']['end_time'] = datetime.now().isoformat()
        
        # Save batch results
        results_file = self.exports_dir / "archive" / f"batch_results_{self.timestamp}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📊 Batch complete: {results['summary']['successful']}/{results['summary']['total_files']} successful")
        print(f"📋 Results saved: {results_file}")
        
        return results
    
    def create_content_variants(self, input_file: Path, 
                               personas: List[str] = None) -> Dict[str, Any]:
        """Create multiple variants of content with different personas"""
        
        if personas is None:
            config = self.load_processing_config()
            personas = list(config['personas'].values())[:3]  # Take first 3
        
        print(f"🎭 Creating {len(personas)} variants of {input_file.name}")
        
        results = {'variants': [], 'failed': []}
        
        for persona in personas:
            result = self.process_file(input_file, persona=persona)
            
            if 'error' in result:
                results['failed'].append({'persona': persona, 'error': result['error']})
            else:
                results['variants'].append(result)
                print(f"  ✅ {persona} variant created")
        
        return results

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Automated Content Processing Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file
  python content_processor.py process --file drafts/my_essay.md --persona philosopher
  
  # Batch process directory
  python content_processor.py batch --dir drafts/essays/ --output transformations/
  
  # Create multiple variants
  python content_processor.py variants --file my_content.md --personas philosopher,scientist,artist
        """
    )
    
    parser.add_argument('command', choices=['process', 'batch', 'variants'], 
                       help='Processing command')
    parser.add_argument('--file', type=Path, help='Input file to process')
    parser.add_argument('--dir', type=Path, help='Input directory for batch processing')
    parser.add_argument('--output', type=Path, help='Output directory')
    parser.add_argument('--persona', help='Persona for transformation')
    parser.add_argument('--namespace', help='Namespace for transformation')
    parser.add_argument('--style', help='Style for transformation')
    parser.add_argument('--personas', help='Comma-separated list of personas for variants')
    
    args = parser.parse_args()
    
    processor = ContentProcessor()
    
    if args.command == 'process':
        if not args.file:
            parser.error("--file required for process command")
        
        result = processor.process_file(
            args.file, 
            persona=args.persona,
            namespace=args.namespace,
            style=args.style,
            output_dir=args.output
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        else:
            print(f"✅ Success: {result['output_file']}")
    
    elif args.command == 'batch':
        if not args.dir:
            parser.error("--dir required for batch command")
        
        result = processor.batch_process_directory(args.dir, output_dir=args.output)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
    
    elif args.command == 'variants':
        if not args.file:
            parser.error("--file required for variants command")
        
        personas = args.personas.split(',') if args.personas else None
        result = processor.create_content_variants(args.file, personas=personas)
        
        print(f"✅ Created {len(result['variants'])} variants")
        if result['failed']:
            print(f"❌ {len(result['failed'])} failed")

if __name__ == "__main__":
    main()