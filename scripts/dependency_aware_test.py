#!/usr/bin/env python3
"""
Dependency-Aware Testing Script
Tests what works with current environment and reports dependency status
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class DependencyAwareTest:
    """Test framework that adapts to available dependencies"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.test_runs_dir = self.project_root / "test_runs" 
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create test output directory
        self.test_output_dir = self.test_runs_dir / f"dependency_test_{self.timestamp}"
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            'test_run_id': f"dependency_test_{self.timestamp}",
            'start_time': datetime.now().isoformat(),
            'environment': self.check_environment(),
            'tests': {},
            'summary': {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
        }
    
    def check_environment(self) -> Dict[str, Any]:
        """Check what's available in the current environment"""
        env_status = {}
        
        # Check Python version
        env_status['python_version'] = sys.version
        
        # Check for Python packages
        packages_to_check = [
            'markdown', 'jinja2', 'sentence_transformers', 'sklearn', 
            'matplotlib', 'seaborn', 'numpy', 'sqlite3', 'yaml'
        ]
        
        env_status['packages'] = {}
        for package in packages_to_check:
            try:
                __import__(package)
                env_status['packages'][package] = 'available'
            except ImportError:
                env_status['packages'][package] = 'missing'
        
        # Check for external tools
        external_tools = ['pandoc', 'git']
        env_status['external_tools'] = {}
        
        for tool in external_tools:
            try:
                result = subprocess.run([tool, '--version'], capture_output=True, timeout=5)
                env_status['external_tools'][tool] = 'available' if result.returncode == 0 else 'missing'
            except:
                env_status['external_tools'][tool] = 'missing'
        
        return env_status
    
    def create_test_content(self):
        """Create simple test content"""
        test_file = self.test_output_dir / "test_content.md"
        content = """# Test Content

This is test content for the dependency-aware testing framework.

## Simple Content

Lorem ipsum dolor sit amet, consectetur adipiscing elit.

## Conclusion

This should work for basic testing.
"""
        with open(test_file, 'w') as f:
            f.write(content)
        
        return test_file
    
    def run_test(self, name: str, test_func) -> Dict[str, Any]:
        """Run a single test with error handling"""
        print(f"\n🧪 Testing: {name}")
        
        result = {
            'name': name,
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        try:
            test_result = test_func()
            
            if test_result.get('success', False):
                result['status'] = 'passed'
                result['message'] = test_result.get('message', 'Test passed')
                self.results['summary']['passed'] += 1
                print(f"   ✅ PASSED: {result['message']}")
                
            elif test_result.get('skipped', False):
                result['status'] = 'skipped'
                result['message'] = test_result.get('message', 'Test skipped')
                self.results['summary']['skipped'] += 1
                print(f"   ⏭️  SKIPPED: {result['message']}")
                
            else:
                result['status'] = 'failed'
                result['message'] = test_result.get('message', 'Test failed')
                self.results['summary']['failed'] += 1
                print(f"   ❌ FAILED: {result['message']}")
                
        except Exception as e:
            result['status'] = 'failed'
            result['message'] = f'Exception: {str(e)}'
            self.results['summary']['failed'] += 1
            print(f"   ❌ FAILED: {str(e)}")
        
        finally:
            result['end_time'] = datetime.now().isoformat()
            self.results['tests'][name] = result
            self.results['summary']['total'] += 1
        
        return result
    
    def test_script_existence(self) -> Dict[str, Any]:
        """Test that all Phase 3 scripts exist and are executable"""
        scripts = [
            'content_processor.py',
            'format_generator.py', 
            'embedding_navigator.py',
            'rho_visualizer.py',
            'master_pipeline.py',
            'test_framework.py',
            'export_book.sh',
            'organize_exports.sh'
        ]
        
        missing = []
        non_executable = []
        
        for script in scripts:
            script_path = self.scripts_dir / script
            if not script_path.exists():
                missing.append(script)
            elif not os.access(script_path, os.X_OK):
                non_executable.append(script)
        
        if missing:
            return {'success': False, 'message': f'Missing scripts: {", ".join(missing)}'}
        elif non_executable:
            return {'success': False, 'message': f'Non-executable scripts: {", ".join(non_executable)}'}
        else:
            return {'success': True, 'message': f'All {len(scripts)} scripts exist and are executable'}
    
    def test_directory_structure(self) -> Dict[str, Any]:
        """Test directory structure"""
        required_dirs = [
            'scripts', 'exports', 'data', 'test_runs', 'config'
        ]
        
        missing = []
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                missing.append(dir_name)
        
        if missing:
            return {'success': False, 'message': f'Missing directories: {", ".join(missing)}'}
        else:
            return {'success': True, 'message': f'All {len(required_dirs)} required directories exist'}
    
    def test_content_processor_help(self) -> Dict[str, Any]:
        """Test content processor help command"""
        script_path = self.scripts_dir / "content_processor.py"
        
        try:
            result = subprocess.run(['python3', str(script_path), '--help'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'usage:' in result.stdout.lower():
                return {'success': True, 'message': 'Content processor help works'}
            else:
                return {'success': False, 'message': f'Help command failed: {result.stderr}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Help command timed out'}
        except Exception as e:
            return {'success': False, 'message': f'Error testing help: {str(e)}'}
    
    def test_format_generator_with_dependencies(self) -> Dict[str, Any]:
        """Test format generator - skip if dependencies missing"""
        if self.results['environment']['packages']['markdown'] == 'missing':
            return {'skipped': True, 'message': 'Skipped - markdown package not available'}
        
        script_path = self.scripts_dir / "format_generator.py"
        test_file = self.create_test_content()
        
        try:
            result = subprocess.run([
                'python3', str(script_path), 'convert', 
                '--file', str(test_file), '--format', 'html'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Format generator HTML conversion works'}
            else:
                return {'success': False, 'message': f'Format generator failed: {result.stderr}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Format generator timed out'}
        except Exception as e:
            return {'success': False, 'message': f'Error testing format generator: {str(e)}'}
    
    def test_embedding_navigator_stats(self) -> Dict[str, Any]:
        """Test embedding navigator stats (should work without ML dependencies)"""
        script_path = self.scripts_dir / "embedding_navigator.py"
        
        try:
            result = subprocess.run(['python3', str(script_path), 'stats'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Embedding navigator stats command works'}
            elif 'Missing dependencies' in result.stdout:
                return {'success': True, 'message': 'Embedding navigator handles missing dependencies gracefully'}
            else:
                return {'success': False, 'message': f'Stats command failed: {result.stderr}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Stats command timed out'}
        except Exception as e:
            return {'success': False, 'message': f'Error testing stats: {str(e)}'}
    
    def test_rho_visualizer_stats(self) -> Dict[str, Any]:
        """Test rho visualizer stats command"""
        script_path = self.scripts_dir / "rho_visualizer.py"
        
        try:
            result = subprocess.run(['python3', str(script_path), 'stats'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Rho visualizer stats command works'}
            else:
                return {'success': False, 'message': f'Stats command failed: {result.stderr}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Stats command timed out'}
        except Exception as e:
            return {'success': False, 'message': f'Error testing rho stats: {str(e)}'}
    
    def test_master_pipeline_status(self) -> Dict[str, Any]:
        """Test master pipeline status command"""
        script_path = self.scripts_dir / "master_pipeline.py"
        
        try:
            result = subprocess.run(['python3', str(script_path), 'status'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Master pipeline status check works'}
            else:
                return {'success': False, 'message': f'Status command failed: {result.stderr}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Status command timed out'}
        except Exception as e:
            return {'success': False, 'message': f'Error testing pipeline status: {str(e)}'}
    
    def test_export_scripts_executable(self) -> Dict[str, Any]:
        """Test that export scripts are executable"""
        scripts = ['export_book.sh', 'organize_exports.sh']
        results = []
        
        for script in scripts:
            script_path = self.scripts_dir / script
            if script_path.exists() and os.access(script_path, os.X_OK):
                results.append(f'✅ {script}')
            else:
                results.append(f'❌ {script}')
        
        success_count = len([r for r in results if '✅' in r])
        
        if success_count == len(scripts):
            return {'success': True, 'message': f'All {len(scripts)} export scripts are executable'}
        else:
            return {'success': False, 'message': f'Only {success_count}/{len(scripts)} scripts are executable'}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all dependency-aware tests"""
        print("🚀 Dependency-Aware Test Suite")
        print(f"   Run ID: {self.results['test_run_id']}")
        print("=" * 60)
        
        # Print environment status
        print("\n📋 Environment Status:")
        print(f"   Python: {self.results['environment']['python_version'].split()[0]}")
        
        available_packages = [k for k, v in self.results['environment']['packages'].items() if v == 'available']
        missing_packages = [k for k, v in self.results['environment']['packages'].items() if v == 'missing']
        
        print(f"   Available packages: {', '.join(available_packages) if available_packages else 'None'}")
        print(f"   Missing packages: {', '.join(missing_packages) if missing_packages else 'None'}")
        
        available_tools = [k for k, v in self.results['environment']['external_tools'].items() if v == 'available']
        print(f"   External tools: {', '.join(available_tools) if available_tools else 'None'}")
        
        # Run tests
        tests = [
            ('Script Existence', self.test_script_existence),
            ('Directory Structure', self.test_directory_structure), 
            ('Content Processor Help', self.test_content_processor_help),
            ('Format Generator', self.test_format_generator_with_dependencies),
            ('Embedding Navigator Stats', self.test_embedding_navigator_stats),
            ('Rho Visualizer Stats', self.test_rho_visualizer_stats),
            ('Master Pipeline Status', self.test_master_pipeline_status),
            ('Export Scripts', self.test_export_scripts_executable)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Finalize results
        self.results['end_time'] = datetime.now().isoformat()
        
        # Save results
        results_file = self.test_runs_dir / f"dependency_aware_test_{self.timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Create detailed log
        log_file = self.test_runs_dir / f"dependency_aware_test_{self.timestamp}.log"
        with open(log_file, 'w') as f:
            f.write(f"Dependency-Aware Test Log - {self.results['test_run_id']}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("Environment Status:\n")
            f.write(f"Python: {self.results['environment']['python_version']}\n")
            f.write(f"Available packages: {available_packages}\n")
            f.write(f"Missing packages: {missing_packages}\n")
            f.write(f"External tools: {available_tools}\n\n")
            
            f.write("Test Results:\n")
            for test_name, test_result in self.results['tests'].items():
                f.write(f"{test_result['status'].upper()}: {test_name} - {test_result['message']}\n")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.results['summary']['total']}")
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        print(f"Skipped: {self.results['summary']['skipped']}")
        
        success_rate = (self.results['summary']['passed'] / 
                       self.results['summary']['total'] * 100) if self.results['summary']['total'] > 0 else 0
        
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"\n📄 Results saved:")
        print(f"   JSON: {results_file}")
        print(f"   Log:  {log_file}")
        
        return self.results


if __name__ == "__main__":
    tester = DependencyAwareTest()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['summary']['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)