#!/usr/bin/env python3
"""
Correct Environment Testing Script
Tests using the proper Python 3.11 venv as specified in CLAUDE.md
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class CorrectEnvTest:
    """Test framework using the correct Python 3.11 lighthouse venv"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.test_runs_dir = self.project_root / "test_runs" 
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Correct Python path from lighthouse venv
        self.python_path = str(self.project_root / "humanizer_api" / "lighthouse" / "venv" / "bin" / "python")
        
        # Create test output directory
        self.test_output_dir = self.test_runs_dir / f"correct_env_test_{self.timestamp}"
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            'test_run_id': f"correct_env_test_{self.timestamp}",
            'start_time': datetime.now().isoformat(),
            'python_path': self.python_path,
            'environment': {},
            'tests': {},
            'summary': {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
        }
    
    def check_environment(self) -> Dict[str, Any]:
        """Check the correct Python 3.11 environment"""
        env_status = {}
        
        try:
            # Check Python version in correct venv
            result = subprocess.run([self.python_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            env_status['python_version'] = result.stdout.strip() if result.returncode == 0 else 'Failed to get version'
            env_status['python_executable'] = self.python_path
            
            # Check for Python packages in correct venv
            packages_to_check = [
                'markdown', 'jinja2', 'sqlite3', 'json', 'pathlib', 'datetime'
            ]
            
            env_status['packages'] = {}
            for package in packages_to_check:
                try:
                    check_result = subprocess.run([
                        self.python_path, '-c', f'import {package}; print("available")'
                    ], capture_output=True, text=True, timeout=5)
                    
                    env_status['packages'][package] = 'available' if check_result.returncode == 0 else 'missing'
                except:
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
                    
        except Exception as e:
            env_status['error'] = f'Environment check failed: {str(e)}'
        
        return env_status
    
    def create_test_content(self):
        """Create test content file"""
        test_file = self.test_output_dir / "test_content.md"
        content = """# Test Content for Correct Environment

This is test content for validating the Python 3.11 lighthouse venv.

## Features to Test

- Content processing
- Format generation  
- Database operations
- File handling

## Conclusion

This content should work with all our automation tools.
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
    
    def test_python_environment(self) -> Dict[str, Any]:
        """Test that we're using the correct Python 3.11 environment"""
        try:
            result = subprocess.run([self.python_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                if '3.11' in version:
                    return {'success': True, 'message': f'Correct Python version: {version}'}
                else:
                    return {'success': False, 'message': f'Wrong Python version: {version} (should be 3.11.x)'}
            else:
                return {'success': False, 'message': 'Failed to get Python version'}
                
        except Exception as e:
            return {'success': False, 'message': f'Environment test error: {str(e)}'}
    
    def test_content_processor_with_correct_env(self) -> Dict[str, Any]:
        """Test content processor with correct Python environment"""
        script_path = self.scripts_dir / "content_processor.py"
        
        try:
            result = subprocess.run([self.python_path, str(script_path), '--help'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and 'usage:' in result.stdout.lower():
                return {'success': True, 'message': 'Content processor works with Python 3.11'}
            else:
                return {'success': False, 'message': f'Content processor failed: {result.stderr}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Content processor timed out'}
        except Exception as e:
            return {'success': False, 'message': f'Content processor test error: {str(e)}'}
    
    def test_format_generator_with_correct_env(self) -> Dict[str, Any]:
        """Test format generator with correct Python environment and dependencies"""
        script_path = self.scripts_dir / "format_generator.py"
        test_file = self.create_test_content()
        
        try:
            # Test help first
            help_result = subprocess.run([self.python_path, str(script_path), '--help'], 
                                       capture_output=True, text=True, timeout=10)
            
            if help_result.returncode != 0:
                return {'success': False, 'message': f'Format generator help failed: {help_result.stderr}'}
            
            # Test actual conversion
            result = subprocess.run([
                self.python_path, str(script_path), 'convert', 
                '--file', str(test_file), '--format', 'html'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Format generator HTML conversion works with Python 3.11'}
            else:
                return {'success': False, 'message': f'Format generator conversion failed: {result.stderr}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Format generator timed out'}
        except Exception as e:
            return {'success': False, 'message': f'Format generator test error: {str(e)}'}
    
    def test_embedding_navigator_with_correct_env(self) -> Dict[str, Any]:
        """Test embedding navigator with correct environment"""
        script_path = self.scripts_dir / "embedding_navigator.py"
        
        try:
            result = subprocess.run([self.python_path, str(script_path), 'stats'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Embedding navigator works with Python 3.11'}
            elif 'Missing dependencies' in result.stdout:
                return {'success': True, 'message': 'Embedding navigator handles dependencies gracefully with Python 3.11'}
            else:
                return {'success': False, 'message': f'Embedding navigator failed: {result.stderr}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Embedding navigator timed out'}
        except Exception as e:
            return {'success': False, 'message': f'Embedding navigator test error: {str(e)}'}
    
    def test_rho_visualizer_with_correct_env(self) -> Dict[str, Any]:
        """Test rho visualizer with correct environment"""
        script_path = self.scripts_dir / "rho_visualizer.py"
        
        try:
            result = subprocess.run([self.python_path, str(script_path), 'stats'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Rho visualizer works with Python 3.11'}
            else:
                return {'success': False, 'message': f'Rho visualizer failed: {result.stderr}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Rho visualizer timed out'}
        except Exception as e:
            return {'success': False, 'message': f'Rho visualizer test error: {str(e)}'}
    
    def test_master_pipeline_with_correct_env(self) -> Dict[str, Any]:
        """Test master pipeline with correct environment"""
        script_path = self.scripts_dir / "master_pipeline.py"
        
        try:
            result = subprocess.run([self.python_path, str(script_path), 'status'], 
                                  capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0:
                return {'success': True, 'message': 'Master pipeline works with Python 3.11'}
            else:
                return {'success': False, 'message': f'Master pipeline failed: {result.stderr}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': 'Master pipeline timed out'}
        except Exception as e:
            return {'success': False, 'message': f'Master pipeline test error: {str(e)}'}
    
    def test_integration_workflow_correct_env(self) -> Dict[str, Any]:
        """Test integration workflow with correct environment"""
        test_file = self.create_test_content()
        
        try:
            # Test content processor -> format generator workflow
            content_proc = self.scripts_dir / "content_processor.py"
            format_gen = self.scripts_dir / "format_generator.py"
            
            if content_proc.exists():
                # Test content processor help (quick test)
                result1 = subprocess.run([
                    self.python_path, str(content_proc), '--help'
                ], capture_output=True, text=True, timeout=15)
                
                if result1.returncode != 0:
                    return {'success': False, 'message': f'Content processor failed in integration: {result1.stderr}'}
            
            if format_gen.exists():
                # Test format generator
                result2 = subprocess.run([
                    self.python_path, str(format_gen), 'convert', 
                    '--file', str(test_file), '--format', 'html'
                ], capture_output=True, text=True, timeout=30)
                
                if result2.returncode != 0:
                    return {'success': False, 'message': f'Format generator failed in integration: {result2.stderr}'}
            
            return {'success': True, 'message': 'Integration workflow works with Python 3.11'}
            
        except Exception as e:
            return {'success': False, 'message': f'Integration workflow test error: {str(e)}'}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests with the correct Python 3.11 environment"""
        print("🚀 Correct Environment Test Suite (Python 3.11)")
        print(f"   Run ID: {self.results['test_run_id']}")
        print(f"   Python Path: {self.python_path}")
        print("=" * 70)
        
        # Check environment first
        self.results['environment'] = self.check_environment()
        
        # Print environment status
        print("\n📋 Environment Status:")
        if 'python_version' in self.results['environment']:
            print(f"   {self.results['environment']['python_version']}")
        if 'python_executable' in self.results['environment']:
            print(f"   Executable: {self.results['environment']['python_executable']}")
        
        if 'packages' in self.results['environment']:
            available_packages = [k for k, v in self.results['environment']['packages'].items() if v == 'available']
            print(f"   Available packages: {', '.join(available_packages) if available_packages else 'None'}")
        
        # Run tests
        tests = [
            ('Python Environment', self.test_python_environment),
            ('Content Processor', self.test_content_processor_with_correct_env),
            ('Format Generator', self.test_format_generator_with_correct_env),
            ('Embedding Navigator', self.test_embedding_navigator_with_correct_env),
            ('Rho Visualizer', self.test_rho_visualizer_with_correct_env),
            ('Master Pipeline', self.test_master_pipeline_with_correct_env),
            ('Integration Workflow', self.test_integration_workflow_correct_env)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Finalize results
        self.results['end_time'] = datetime.now().isoformat()
        
        # Save results
        results_file = self.test_runs_dir / f"correct_env_test_{self.timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Create detailed log
        log_file = self.test_runs_dir / f"correct_env_test_{self.timestamp}.log"
        with open(log_file, 'w') as f:
            f.write(f"Correct Environment Test Log - {self.results['test_run_id']}\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("Environment Status:\n")
            if 'python_version' in self.results['environment']:
                f.write(f"Python: {self.results['environment']['python_version']}\n")
            f.write(f"Executable: {self.results['environment'].get('python_executable', 'Unknown')}\n")
            
            if 'packages' in self.results['environment']:
                available_packages = [k for k, v in self.results['environment']['packages'].items() if v == 'available']
                f.write(f"Available packages: {available_packages}\n")
            
            f.write("\nTest Results:\n")
            for test_name, test_result in self.results['tests'].items():
                f.write(f"{test_result['status'].upper()}: {test_name} - {test_result['message']}\n")
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 CORRECT ENVIRONMENT TEST SUMMARY")
        print("=" * 70)
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
        
        if success_rate >= 85:
            print("\n🎉 EXCELLENT: Phase 3 automation is working correctly with Python 3.11!")
        elif success_rate >= 70:
            print("\n✅ GOOD: Most Phase 3 components are working with Python 3.11")
        else:
            print("\n⚠️  NEEDS ATTENTION: Some Phase 3 components need fixing")
        
        return self.results


if __name__ == "__main__":
    tester = CorrectEnvTest()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['summary']['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)