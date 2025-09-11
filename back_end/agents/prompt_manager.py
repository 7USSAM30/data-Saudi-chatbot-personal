import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages system prompts and configurations loaded from JSON files."""
    
    def __init__(self, prompts_file: str = None):
        """Initialize the prompt manager.
        
        Args:
            prompts_file: Path to the prompts JSON file. If None, uses default location.
        """
        if prompts_file is None:
            prompts_file = os.path.join(os.path.dirname(__file__), 'prompts.json')
        
        self.prompts_file = prompts_file
        self.prompts_data = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from the JSON file."""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded prompts from {self.prompts_file}")
                return data
        except FileNotFoundError:
            logger.error(f"Prompts file not found: {self.prompts_file}")
            return self._get_default_prompts()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing prompts file: {e}")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, Any]:
        """Return default prompts if file loading fails."""
        return {
            "version": "1.0.0",
            "prompts": {
                "system": {
                    "en": {
                        "role": "You are an expert AI assistant for Data Saudi.",
                        "rules": ["Provide helpful answers based on provided information."]
                    }
                }
            },
            "config": {
                "search_top_k": 7,
                "max_tokens_answer": 1500,
                "max_tokens_translate": 150,
                "temperature_answer": 1.0,
                "temperature_translate": 1.0
            }
        }
    
    def reload_prompts(self) -> None:
        """Reload prompts from the file (useful for hot-reloading)."""
        self.prompts_data = self._load_prompts()
    
    def get_system_prompt(self, language: str = 'en') -> str:
        """Get the system prompt for a specific language.
        
        Args:
            language: Language code ('en' or 'ar')
            
        Returns:
            Formatted system prompt string
        """
        try:
            system_data = self.prompts_data['prompts']['system'][language]
            role = system_data['role']
            rules = system_data['rules']
            
            # Format the prompt
            prompt = f"{role}\n\n**Here's how to respond (CRITICAL RULES):**\n"
            for i, rule in enumerate(rules, 1):
                prompt += f"\n{i}. {rule}"
            
            return prompt
        except KeyError:
            logger.warning(f"System prompt not found for language: {language}")
            return self._get_default_prompts()['prompts']['system']['en']['role']
    
    def get_translation_prompt(self, language: str = 'en') -> str:
        """Get the translation prompt for a specific language.
        
        Args:
            language: Language code ('en' or 'ar')
            
        Returns:
            Translation prompt string
        """
        try:
            return self.prompts_data['prompts']['translation'][language]
        except KeyError:
            logger.warning(f"Translation prompt not found for language: {language}")
            return "Translate the following to {target_language}. Return only the translation."
    
    def get_error_message(self, error_type: str, language: str = 'en') -> str:
        """Get an error message for a specific type and language.
        
        Args:
            error_type: Type of error ('translation_failed', 'api_failed', 'no_data')
            language: Language code ('en' or 'ar')
            
        Returns:
            Error message string
        """
        try:
            return self.prompts_data['prompts']['error_messages'][error_type][language]
        except KeyError:
            logger.warning(f"Error message not found for type: {error_type}, language: {language}")
            return "An error occurred. Please try again."
    
    def get_config(self, key: str) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value
        """
        return self.prompts_data.get('config', {}).get(key)
    
    def get_model_config(self, key: str) -> str:
        """Get a model configuration value.
        
        Args:
            key: Model configuration key ('llm' or 'embedding')
            
        Returns:
            Model name string
        """
        return self.prompts_data.get('models', {}).get(key, '')
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configuration values.
        
        Returns:
            Dictionary of all configurations
        """
        return self.prompts_data.get('config', {})
    
    def get_version(self) -> str:
        """Get the prompts version.
        
        Returns:
            Version string
        """
        return self.prompts_data.get('version', 'unknown')
    
    def validate_prompts(self) -> bool:
        """Validate that all required prompts are present.
        
        Returns:
            True if valid, False otherwise
        """
        required_keys = [
            'prompts.system.en.role',
            'prompts.system.en.rules',
            'prompts.system.ar.role', 
            'prompts.system.ar.rules',
            'prompts.translation.en',
            'prompts.translation.ar',
            'prompts.error_messages.translation_failed.en',
            'prompts.error_messages.translation_failed.ar'
        ]
        
        for key_path in required_keys:
            keys = key_path.split('.')
            value = self.prompts_data
            try:
                for key in keys:
                    value = value[key]
            except (KeyError, TypeError):
                logger.error(f"Missing required prompt: {key_path}")
                return False
        
        logger.info("All required prompts are present and valid")
        return True
