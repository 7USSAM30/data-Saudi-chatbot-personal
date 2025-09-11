# 🚀 Prompt Management System

This document explains how to use the new JSON-based prompt management system for the Data Saudi Chatbot.

## 📁 File Structure

```
back_end/agents/
├── prompts.json          # Main prompts configuration file
├── prompt_manager.py     # Python class to manage prompts
└── answer_agent.py       # Updated to use prompt manager
```

## 🎯 Benefits of Using `prompts.json`

### ✅ **Maintainability**
- **No Code Changes**: Update prompts without touching Python code
- **Version Control**: Track prompt changes separately from code
- **Easy Editing**: Non-developers can modify prompts

### ✅ **Flexibility**
- **Multi-language Support**: Store prompts in Arabic and English
- **Environment-specific**: Different prompts for dev/staging/prod
- **A/B Testing**: Test different prompt versions

### ✅ **Configuration Management**
- **Centralized Settings**: All prompts and configs in one place
- **Hot Reloading**: Update prompts without restarting the service
- **Validation**: Built-in validation for required prompts

## 📋 Prompt Structure

### **System Prompts**
```json
{
  "prompts": {
    "system": {
      "en": {
        "role": "You are an expert AI assistant...",
        "rules": [
          "Rule 1: Answer directly with numbers...",
          "Rule 2: Provide closest relevant figures..."
        ]
      },
      "ar": {
        "role": "أنت مساعد ذكي متخصص...",
        "rules": [
          "القاعدة 1: أجب مباشرة بالأرقام...",
          "القاعدة 2: قدم أقرب الأرقام ذات الصلة..."
        ]
      }
    }
  }
}
```

### **Translation Prompts**
```json
{
  "prompts": {
    "translation": {
      "en": "Translate the following to {target_language}. Return only the translation.",
      "ar": "ترجم التالي إلى {target_language}. أعد الترجمة فقط."
    }
  }
}
```

### **Error Messages**
```json
{
  "prompts": {
    "error_messages": {
      "translation_failed": {
        "en": "I'm sorry, I encountered an issue...",
        "ar": "عذراً، واجهت مشكلة..."
      }
    }
  }
}
```

### **Configuration**
```json
{
  "config": {
    "search_top_k": 7,
    "max_tokens_answer": 1500,
    "max_tokens_translate": 150,
    "temperature_answer": 1.0,
    "temperature_translate": 1.0,
    "chunk_size": 400
  }
}
```

### **Model Configuration**
```json
{
  "models": {
    "llm": "gpt-5-chat-latest",
    "embedding": "text-embedding-3-large"
  }
}
```

## 🛠️ Usage Examples

### **Basic Usage**
```python
from prompt_manager import PromptManager

# Initialize with default prompts.json location
pm = PromptManager()

# Get system prompt in English
en_prompt = pm.get_system_prompt('en')

# Get system prompt in Arabic
ar_prompt = pm.get_system_prompt('ar')

# Get configuration values
top_k = pm.get_config('search_top_k')
max_tokens = pm.get_config('max_tokens_answer')
```

### **Advanced Usage**
```python
# Custom prompts file location
pm = PromptManager('/path/to/custom_prompts.json')

# Get error message in specific language
error_msg = pm.get_error_message('translation_failed', 'ar')

# Get all configurations
all_configs = pm.get_all_configs()

# Validate prompts
is_valid = pm.validate_prompts()

# Hot reload prompts
pm.reload_prompts()
```

## 🔄 Hot Reloading

The prompt manager supports hot reloading, allowing you to update prompts without restarting the service:

```python
# Update prompts.json file
# Then call:
pm.reload_prompts()
```

## ✅ Validation

The system automatically validates that all required prompts are present:

```python
if pm.validate_prompts():
    print("All prompts are valid!")
else:
    print("Some prompts are missing!")
```

## 🧪 Testing

Run the test script to verify everything works:

```bash
python test_prompt_manager.py
```

## 📝 Adding New Prompts

### **1. Add to `prompts.json`**
```json
{
  "prompts": {
    "new_category": {
      "en": "English text",
      "ar": "Arabic text"
    }
  }
}
```

### **2. Add to `PromptManager` class**
```python
def get_new_prompt(self, language: str = 'en') -> str:
    try:
        return self.prompts_data['prompts']['new_category'][language]
    except KeyError:
        return "Default fallback text"
```

### **3. Use in your code**
```python
new_prompt = pm.get_new_prompt('en')
```

## 🚨 Best Practices

### **✅ Do's**
- **Version Control**: Always version your prompts
- **Validation**: Use `validate_prompts()` before deployment
- **Fallbacks**: Provide default values for missing prompts
- **Documentation**: Document any new prompt categories

### **❌ Don'ts**
- **Hardcode**: Don't hardcode prompts in Python files
- **Skip Validation**: Always validate prompts before use
- **Ignore Errors**: Handle missing prompts gracefully
- **Forget Testing**: Test new prompts thoroughly

## 🔧 Troubleshooting

### **Common Issues**

1. **File Not Found**
   ```
   Error: Prompts file not found
   Solution: Check file path and permissions
   ```

2. **JSON Parse Error**
   ```
   Error: Error parsing prompts file
   Solution: Validate JSON syntax
   ```

3. **Missing Prompts**
   ```
   Error: Missing required prompt
   Solution: Run validate_prompts() to identify issues
   ```

### **Debug Commands**
```python
# Check prompt version
print(pm.get_version())

# List all configurations
print(pm.get_all_configs())

# Validate prompts
print(pm.validate_prompts())
```

## 🚀 Future Enhancements

- **Database Storage**: Store prompts in database for multi-tenant support
- **API Endpoints**: REST API for prompt management
- **Versioning**: Support for multiple prompt versions
- **Analytics**: Track prompt performance and usage
- **Templates**: Support for prompt templates and variables

---

**Happy Prompting! 🎉**
