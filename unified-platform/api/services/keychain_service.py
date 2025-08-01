"""
Keychain Service for Unified Platform
Secure API key management using macOS Keychain with migration from existing system
"""
import subprocess
import logging
import os
from typing import Optional, Dict, List
from dataclasses import dataclass

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from config import config, LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class APIKeyInfo:
    """Information about a stored API key."""
    provider: str
    service_name: str
    account: str
    has_key: bool
    is_valid: Optional[bool] = None
    last_modified: Optional[str] = None


class KeychainService:
    """Enhanced keychain service for unified platform"""
    
    def __init__(self, app_name: str = "unified-humanizer"):
        self.app_name = app_name
        self.service_prefix = f"com.humanizer.{app_name}"
        self.legacy_service_prefix = "com.humanizer.humanizer-lighthouse"
        
    def _get_service_name(self, provider: str) -> str:
        """Generate consistent service name for keychain."""
        return f"{self.service_prefix}.{provider}"
    
    def _get_legacy_service_name(self, provider: str) -> str:
        """Generate legacy service name for migration."""
        return f"{self.legacy_service_prefix}.{provider}"
    
    def _run_security_command(self, command: List[str]) -> tuple[bool, str]:
        """Run macOS security command safely."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.error("Keychain operation timed out")
            return False, "Operation timed out"
        except Exception as e:
            logger.error(f"Keychain operation failed: {e}")
            return False, str(e)
    
    def store_api_key(self, provider: str, api_key: str, account: str = "default") -> bool:
        """Store API key securely in macOS Keychain."""
        service_name = self._get_service_name(provider)
        
        command = [
            "security", "add-generic-password",
            "-s", service_name,
            "-a", account,
            "-w", api_key,
            "-U"  # Update if exists
        ]
        
        success, output = self._run_security_command(command)
        
        if success:
            logger.info(f"Successfully stored API key for {provider}")
            # Also set as environment variable for immediate use
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
            return True
        else:
            logger.error(f"Failed to store API key for {provider}: {output}")
            return False
    
    def retrieve_api_key(self, provider: str, account: str = "default") -> Optional[str]:
        """Retrieve API key from macOS Keychain."""
        service_name = self._get_service_name(provider)
        
        command = [
            "security", "find-generic-password",
            "-s", service_name,
            "-a", account,
            "-w"  # Return password only
        ]
        
        success, output = self._run_security_command(command)
        
        if success:
            api_key = output.strip()
            # Set as environment variable
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
            return api_key
        else:
            # Try legacy service name
            legacy_service_name = self._get_legacy_service_name(provider)
            command[command.index(service_name)] = legacy_service_name
            
            success, output = self._run_security_command(command)
            if success:
                api_key = output.strip()
                # Migrate to new service name
                self.store_api_key(provider, api_key, account)
                logger.info(f"Migrated API key for {provider} from legacy storage")
                return api_key
            
            logger.debug(f"No API key found for {provider}: {output}")
            return None
    
    def migrate_from_legacy(self) -> Dict[str, bool]:
        """Migrate API keys from legacy keychain entries."""
        logger.info("Starting keychain migration from legacy system")
        
        migration_results = {}
        
        # Common LLM providers to migrate
        providers_to_migrate = [
            "openai", "anthropic", "google", "groq", "cohere", 
            "mistral", "deepseek", "ollama", "together"
        ]
        
        for provider in providers_to_migrate:
            try:
                legacy_service_name = self._get_legacy_service_name(provider)
                
                # Try to retrieve from legacy location
                command = [
                    "security", "find-generic-password",
                    "-s", legacy_service_name,
                    "-a", "default",
                    "-w"
                ]
                
                success, output = self._run_security_command(command)
                
                if success:
                    api_key = output.strip()
                    # Store in new location
                    if self.store_api_key(provider, api_key):
                        migration_results[provider] = True
                        logger.info(f"Successfully migrated {provider} API key")
                    else:
                        migration_results[provider] = False
                        logger.error(f"Failed to migrate {provider} API key")
                else:
                    # No legacy key found - not an error
                    logger.debug(f"No legacy API key found for {provider}")
                    
            except Exception as e:
                logger.error(f"Error migrating {provider} key: {e}")
                migration_results[provider] = False
        
        logger.info(f"Migration completed: {sum(migration_results.values())} keys migrated")
        return migration_results
    
    def load_all_keys_to_env(self) -> Dict[str, bool]:
        """Load all stored API keys into environment variables."""
        results = {}
        
        for provider in LLMProvider:
            api_key = self.retrieve_api_key(provider.value)
            if api_key:
                env_var = f"{provider.value.upper()}_API_KEY"
                os.environ[env_var] = api_key
                results[provider.value] = True
                logger.debug(f"Loaded {provider.value} API key to environment")
            else:
                results[provider.value] = False
        
        return results
    
    def test_api_key(self, provider: str, api_key: Optional[str] = None) -> tuple[bool, str]:
        """Test if an API key is valid by making a simple API call."""
        if api_key is None:
            api_key = self.retrieve_api_key(provider)
            if not api_key:
                return False, "No API key found in keychain"
        
        try:
            import httpx
            
            # Test different providers with simple API calls
            if provider == "openai":
                return self._test_openai_key(api_key)
            elif provider == "anthropic":
                return self._test_anthropic_key(api_key)
            elif provider == "deepseek":
                return self._test_deepseek_key(api_key)
            elif provider == "groq":
                return self._test_groq_key(api_key)
            elif provider == "google":
                return self._test_google_key(api_key)
            elif provider == "ollama":
                return self._test_ollama_connection()
            else:
                return True, f"Testing not implemented for {provider}"
                
        except Exception as e:
            return False, f"Test failed: {str(e)}"
    
    def _test_openai_key(self, api_key: str) -> tuple[bool, str]:
        """Test OpenAI API key."""
        try:
            import httpx
            headers = {"Authorization": f"Bearer {api_key}"}
            
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    "https://api.openai.com/v1/models",
                    headers=headers
                )
                if response.status_code == 200:
                    return True, "OpenAI API key is valid"
                else:
                    return False, f"OpenAI API returned status {response.status_code}"
                    
        except ImportError:
            return True, "Cannot test - httpx library not available"
        except Exception as e:
            return False, f"OpenAI test failed: {str(e)}"
    
    def _test_anthropic_key(self, api_key: str) -> tuple[bool, str]:
        """Test Anthropic API key."""
        try:
            import httpx
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
            
            # Use a minimal completion request
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}]
            }
            
            with httpx.Client(timeout=10) as client:
                response = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data
                )
                if response.status_code in [200, 201]:
                    return True, "Anthropic API key is valid"
                else:
                    return False, f"Anthropic API returned status {response.status_code}"
                    
        except ImportError:
            return True, "Cannot test - httpx library not available"
        except Exception as e:
            return False, f"Anthropic test failed: {str(e)}"
    
    def _test_deepseek_key(self, api_key: str) -> tuple[bool, str]:
        """Test DeepSeek API key."""
        try:
            import httpx
            headers = {"Authorization": f"Bearer {api_key}"}
            
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    "https://api.deepseek.com/v1/models",
                    headers=headers
                )
                if response.status_code == 200:
                    return True, "DeepSeek API key is valid"
                else:
                    return False, f"DeepSeek API returned status {response.status_code}"
                    
        except ImportError:
            return True, "Cannot test - httpx library not available"
        except Exception as e:
            return False, f"DeepSeek test failed: {str(e)}"
    
    def _test_groq_key(self, api_key: str) -> tuple[bool, str]:
        """Test Groq API key."""
        try:
            import httpx
            headers = {"Authorization": f"Bearer {api_key}"}
            
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    "https://api.groq.com/openai/v1/models",
                    headers=headers
                )
                if response.status_code == 200:
                    return True, "Groq API key is valid"
                else:
                    return False, f"Groq API returned status {response.status_code}"
                    
        except ImportError:
            return True, "Cannot test - httpx library not available"
        except Exception as e:
            return False, f"Groq test failed: {str(e)}"
    
    def _test_google_key(self, api_key: str) -> tuple[bool, str]:
        """Test Google Gemini API key."""
        try:
            import httpx
            
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
                )
                if response.status_code == 200:
                    return True, "Google API key is valid"
                else:
                    return False, f"Google API returned status {response.status_code}"
                    
        except ImportError:
            return True, "Cannot test - httpx library not available"
        except Exception as e:
            return False, f"Google test failed: {str(e)}"
    
    def _test_ollama_connection(self) -> tuple[bool, str]:
        """Test Ollama local connection."""
        try:
            import httpx
            ollama_host = config.llm.get_llm_provider_config(LLMProvider.OLLAMA).get("base_url", "http://localhost:11434")
            
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{ollama_host}/api/tags")
                if response.status_code == 200:
                    return True, "Ollama is running and accessible"
                else:
                    return False, f"Ollama returned status {response.status_code}"
                    
        except ImportError:
            return True, "Cannot test - httpx library not available"
        except Exception as e:
            return False, f"Ollama test failed: {str(e)}"
    
    def get_provider_status(self) -> Dict[str, Dict]:
        """Get comprehensive status for all configured providers."""
        status = {}
        
        for provider in LLMProvider:
            provider_name = provider.value
            api_key = self.retrieve_api_key(provider_name)
            has_key = api_key is not None
            
            if has_key or provider_name == "ollama":  # Ollama doesn't need API key
                test_success, test_message = self.test_api_key(provider_name, api_key)
                status[provider_name] = {
                    "has_key": has_key,
                    "key_valid": test_success,
                    "status_message": test_message,
                    "available": test_success,
                    "provider_config": config.llm.get_llm_provider_config(provider)
                }
            else:
                status[provider_name] = {
                    "has_key": False,
                    "key_valid": False,
                    "status_message": "No API key stored",
                    "available": False,
                    "provider_config": config.llm.get_llm_provider_config(provider)
                }
        
        return status
    
    def list_stored_keys(self) -> List[APIKeyInfo]:
        """List all stored API keys for this application."""
        command = [
            "security", "dump-keychain"
        ]
        
        success, output = self._run_security_command(command)
        
        if not success:
            logger.error(f"Failed to list keychain items: {output}")
            return []
        
        stored_keys = []
        lines = output.split('\n')
        
        for line in lines:
            if self.service_prefix in line and 'svce' in line:
                try:
                    # Parse service name to extract provider
                    if '"' in line:
                        service_name = line.split('"')[1]
                        if service_name.startswith(self.service_prefix):
                            provider = service_name.replace(f"{self.service_prefix}.", "")
                            
                            # Test the key validity
                            is_valid = None
                            try:
                                test_success, _ = self.test_api_key(provider)
                                is_valid = test_success
                            except:
                                pass
                            
                            stored_keys.append(APIKeyInfo(
                                provider=provider,
                                service_name=service_name,
                                account="default",
                                has_key=True,
                                is_valid=is_valid
                            ))
                except Exception as e:
                    logger.debug(f"Failed to parse keychain line: {e}")
                    continue
        
        return stored_keys


# Global keychain service instance
keychain_service = KeychainService()