"""
Secure API Key Management using macOS Keychain
Provides secure storage and retrieval of LLM provider API keys.
"""
import subprocess
import json
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class APIKeyInfo:
    """Information about a stored API key."""
    provider: str
    service_name: str
    account: str
    has_key: bool
    last_modified: Optional[str] = None

class KeychainManager:
    """Manages API keys in macOS Keychain with security-first approach."""
    
    def __init__(self, app_name: str = "humanizer-lighthouse"):
        self.app_name = app_name
        self.service_prefix = f"com.humanizer.{app_name}"
        
    def _get_service_name(self, provider: str) -> str:
        """Generate consistent service name for keychain."""
        return f"{self.service_prefix}.{provider}"
    
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
        """
        Store API key securely in macOS Keychain.
        
        Args:
            provider: LLM provider name (e.g., 'openai', 'anthropic')
            api_key: The API key to store
            account: Account identifier (default: 'default')
            
        Returns:
            bool: True if successful, False otherwise
        """
        service_name = self._get_service_name(provider)
        
        # First try to update existing key
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
            return True
        else:
            logger.error(f"Failed to store API key for {provider}: {output}")
            return False
    
    def retrieve_api_key(self, provider: str, account: str = "default") -> Optional[str]:
        """
        Retrieve API key from macOS Keychain.
        
        Args:
            provider: LLM provider name
            account: Account identifier
            
        Returns:
            str: API key if found, None otherwise
        """
        service_name = self._get_service_name(provider)
        
        command = [
            "security", "find-generic-password",
            "-s", service_name,
            "-a", account,
            "-w"  # Return password only
        ]
        
        success, output = self._run_security_command(command)
        
        if success:
            return output.strip()
        else:
            logger.debug(f"No API key found for {provider}: {output}")
            return None
    
    def delete_api_key(self, provider: str, account: str = "default") -> bool:
        """
        Delete API key from macOS Keychain.
        
        Args:
            provider: LLM provider name
            account: Account identifier
            
        Returns:
            bool: True if successful or not found, False on error
        """
        service_name = self._get_service_name(provider)
        
        command = [
            "security", "delete-generic-password",
            "-s", service_name,
            "-a", account
        ]
        
        success, output = self._run_security_command(command)
        
        if success:
            logger.info(f"Successfully deleted API key for {provider}")
            return True
        elif "could not be found" in output.lower():
            logger.debug(f"API key for {provider} was already deleted")
            return True
        else:
            logger.error(f"Failed to delete API key for {provider}: {output}")
            return False
    
    def list_stored_keys(self) -> List[APIKeyInfo]:
        """
        List all stored API keys for this application.
        
        Returns:
            List[APIKeyInfo]: Information about stored keys
        """
        command = [
            "security", "dump-keychain",
            "-d"  # Include creation/modification dates
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
                            stored_keys.append(APIKeyInfo(
                                provider=provider,
                                service_name=service_name,
                                account="default",  # We use default for now
                                has_key=True
                            ))
                except Exception as e:
                    logger.debug(f"Failed to parse keychain line: {e}")
                    continue
        
        return stored_keys
    
    def test_api_key(self, provider: str, api_key: Optional[str] = None) -> tuple[bool, str]:
        """
        Test if an API key is valid by making a simple API call.
        
        Args:
            provider: LLM provider name
            api_key: API key to test (if None, retrieves from keychain)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if api_key is None:
            api_key = self.retrieve_api_key(provider)
            if not api_key:
                return False, "No API key found in keychain"
        
        try:
            # Test different providers with simple API calls
            if provider == "openai":
                return self._test_openai_key(api_key)
            elif provider == "anthropic":
                return self._test_anthropic_key(api_key)
            elif provider == "google":
                return self._test_google_key(api_key)
            elif provider == "groq":
                return self._test_groq_key(api_key)
            elif provider == "cohere":
                return self._test_cohere_key(api_key)
            elif provider == "mistral":
                return self._test_mistral_key(api_key)
            else:
                return True, f"Testing not implemented for {provider}"
                
        except Exception as e:
            return False, f"Test failed: {str(e)}"
    
    def _test_openai_key(self, api_key: str) -> tuple[bool, str]:
        """Test OpenAI API key."""
        try:
            import requests
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return True, "OpenAI API key is valid"
            else:
                return False, f"OpenAI API returned status {response.status_code}"
        except ImportError:
            return True, "Cannot test - requests library not available"
        except Exception as e:
            return False, f"OpenAI test failed: {str(e)}"
    
    def _test_anthropic_key(self, api_key: str) -> tuple[bool, str]:
        """Test Anthropic API key."""
        try:
            import requests
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
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=10
            )
            if response.status_code in [200, 201]:
                return True, "Anthropic API key is valid"
            else:
                return False, f"Anthropic API returned status {response.status_code}"
        except ImportError:
            return True, "Cannot test - requests library not available"
        except Exception as e:
            return False, f"Anthropic test failed: {str(e)}"
    
    def _test_google_key(self, api_key: str) -> tuple[bool, str]:
        """Test Google Gemini API key."""
        try:
            import requests
            response = requests.get(
                f"https://generativelanguage.googleapis.com/v1/models?key={api_key}",
                timeout=10
            )
            if response.status_code == 200:
                return True, "Google API key is valid"
            else:
                return False, f"Google API returned status {response.status_code}"
        except ImportError:
            return True, "Cannot test - requests library not available"
        except Exception as e:
            return False, f"Google test failed: {str(e)}"
    
    def _test_groq_key(self, api_key: str) -> tuple[bool, str]:
        """Test Groq API key."""
        try:
            import requests
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return True, "Groq API key is valid"
            else:
                return False, f"Groq API returned status {response.status_code}"
        except ImportError:
            return True, "Cannot test - requests library not available"
        except Exception as e:
            return False, f"Groq test failed: {str(e)}"
    
    def _test_cohere_key(self, api_key: str) -> tuple[bool, str]:
        """Test Cohere API key."""
        try:
            import requests
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://api.cohere.ai/v1/models",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return True, "Cohere API key is valid"
            else:
                return False, f"Cohere API returned status {response.status_code}"
        except ImportError:
            return True, "Cannot test - requests library not available"
        except Exception as e:
            return False, f"Cohere test failed: {str(e)}"
    
    def _test_mistral_key(self, api_key: str) -> tuple[bool, str]:
        """Test Mistral API key."""
        try:
            import requests
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                "https://api.mistral.ai/v1/models",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return True, "Mistral API key is valid"
            else:
                return False, f"Mistral API returned status {response.status_code}"
        except ImportError:
            return True, "Cannot test - requests library not available"
        except Exception as e:
            return False, f"Mistral test failed: {str(e)}"
    
    def get_provider_status(self, providers: List[str]) -> Dict[str, Dict]:
        """
        Get comprehensive status for multiple providers.
        
        Args:
            providers: List of provider names to check
            
        Returns:
            Dict: Status information for each provider
        """
        status = {}
        
        for provider in providers:
            api_key = self.retrieve_api_key(provider)
            has_key = api_key is not None
            
            if has_key:
                test_success, test_message = self.test_api_key(provider, api_key)
                status[provider] = {
                    "has_key": True,
                    "key_valid": test_success,
                    "status_message": test_message,
                    "available": test_success
                }
            else:
                status[provider] = {
                    "has_key": False,
                    "key_valid": False,
                    "status_message": "No API key stored",
                    "available": False
                }
        
        return status

# Global keychain manager instance
keychain_manager = KeychainManager()