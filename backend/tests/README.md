# AI Agents Backend Testing Suite

This directory contains comprehensive unit tests for the AI Agents backend services.

## 📋 Test Coverage

### AI Memory Service Tests (`test_ai_memory.py`)
- ✅ **Initialization Tests**: Redis connection, error handling
- ✅ **Message Storage**: User messages, assistant responses, metadata handling
- ✅ **Conversation Retrieval**: History fetching, formatting for AI models
- ✅ **Memory Management**: Clearing conversations, handling multiple sessions
- ✅ **Error Handling**: Network failures, invalid data, edge cases
- ✅ **Edge Cases**: Empty data, Unicode content, special characters
- ✅ **Integration Tests**: Complete conversation flows

### Agent Tests (`unit_testing.py`)
- ✅ **FAQ Lookup**: Identity queries, greetings, fallback responses
- ✅ **Task Management**: CRUD operations for tasks

## 🚀 Running Tests

### Quick Start
```bash
# Navigate to backend directory
cd aiagents_ver01/backend

# Install dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py
```

### Test Runner Options
```bash
# Run only AI Memory tests
python run_tests.py --memory

# Run only Agent tests  
python run_tests.py --agents

# Run with verbose output
python run_tests.py --verbose

# Run specific test file directly
python -m unittest tests.test_ai_memory -v
```

## 🧪 Test Categories

### 1. Unit Tests
- **Purpose**: Test individual methods in isolation
- **Mocking**: Redis connections and dependencies are mocked
- **Coverage**: All public methods of AIMemoryService class

### 2. Integration Tests
- **Purpose**: Test complete workflows
- **Scope**: End-to-end conversation storage and retrieval
- **Validation**: Data integrity across multiple operations

### 3. Edge Case Tests
- **Empty/null values**: Handling of empty strings and None values
- **Large data**: Testing with large messages and conversations
- **Special characters**: Unicode content and special characters in IDs
- **Error conditions**: Network failures, invalid JSON, missing dependencies

## 📊 Test Structure

### TestAIMemoryService Class
```python
class TestAIMemoryService(unittest.TestCase):
    # Core functionality tests
    test_init_successful_connection()
    test_store_message_success()
    test_get_conversation_history_success()
    test_store_user_request_success()
    test_store_assistant_response_success()
    test_clear_conversation_success()
    test_get_formatted_chat_history_with_data()
    
    # Error handling tests
    test_init_failed_connection()
    test_store_message_no_client()
    test_get_conversation_history_no_client()
    
    # Integration tests
    test_integration_full_conversation_flow()
```

### TestAIMemoryServiceEdgeCases Class
```python
class TestAIMemoryServiceEdgeCases(unittest.TestCase):
    test_empty_string_parameters()
    test_very_long_message()
    test_special_characters_in_ids()
    test_unicode_content()
    test_invalid_json_in_redis()
```

## 🛠️ Dependencies

### Required for Testing
- `unittest` (Python standard library)
- `unittest.mock` (Python 3.3+)
- `redis` (Redis Python client)
- `pytest` (Optional, for advanced testing features)
- `fakeredis` (For Redis mocking without real Redis instance)

### Installing Test Dependencies
```bash
pip install redis pytest fakeredis unittest-mock
```

## 🔧 Test Configuration

### Mocking Strategy
- **Redis Client**: Mocked to avoid requiring real Redis instance
- **External Dependencies**: Isolated using unittest.mock
- **Logging**: Captured and verified for proper error reporting

### Test Data
```python
sample_user_data = {
    "user_id": "test_user_123",
    "user_name": "Test User",
    "user_email": "test@example.com", 
    "session_id": "test_session_456",
    "user_message": "Hello, I need help with testing"
}
```

## 📈 Expected Results

### Successful Test Run
```
🧠 Running AI Memory Service Tests...
..................................................
----------------------------------------------------------------------
Ran 25 tests in 0.123s

OK

🤖 Running Agent Tests...
......
----------------------------------------------------------------------
Ran 6 tests in 0.045s

OK

📊 TEST SUMMARY
============================================================
✅ AI Memory Service:
   Tests: 25, Failures: 0, Errors: 0
   Success Rate: 100.0%
✅ Agents:
   Tests: 6, Failures: 0, Errors: 0
   Success Rate: 100.0%
------------------------------------------------------------
📈 OVERALL: ✅ PASSED
   Total Tests: 31
   Total Failures: 0
   Total Errors: 0
   Overall Success Rate: 100.0%
============================================================
```

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Problem: ModuleNotFoundError: No module named 'services'
# Solution: Run tests from backend directory
cd aiagents_ver01/backend
python run_tests.py
```

#### Redis Connection Errors
```bash
# Problem: redis.ConnectionError in production tests
# Solution: Tests use mocked Redis, no real Redis needed
# If you see this error, check your test imports
```

#### Missing Dependencies
```bash
# Problem: ImportError: No module named 'redis'
# Solution: Install requirements
pip install -r requirements.txt
```

## 📝 Writing New Tests

### For AI Memory Service
```python
def test_new_feature(self):
    """Test description"""
    service = AIMemoryService()
    service.client = self.mock_redis_client
    
    # Test your feature
    result = service.new_method("param1", "param2")
    
    # Assertions
    self.assertTrue(result)
    self.mock_redis_client.some_method.assert_called_once()
```

### For New Services
1. Create new test file: `tests/test_new_service.py`
2. Follow existing test patterns
3. Add to test runner in `run_tests.py`
4. Update this README

## 📚 Best Practices

### Test Naming
- Use descriptive test method names
- Follow pattern: `test_method_condition_expectedresult`
- Example: `test_store_message_no_client_returns_false`

### Mocking
- Mock external dependencies (Redis, APIs, file system)
- Use `patch` decorator for class-level mocking
- Verify mock calls with `assert_called_with()`

### Assertions
- Use specific assertions (`assertEqual`, `assertTrue`, `assertIsNone`)
- Test both positive and negative cases
- Verify error conditions and logging

### Documentation
- Include docstrings for all test methods
- Explain what is being tested and why
- Document any special setup or teardown requirements

## 🔄 Continuous Integration

The tests are designed to run in CI/CD environments:
- No external dependencies required (Redis is mocked)
- Fast execution (typically under 1 second)
- Clear pass/fail indicators
- Detailed error reporting

Add to your CI pipeline:
```yaml
# Example GitHub Actions
- name: Run Backend Tests
  run: |
    cd aiagents_ver01/backend
    pip install -r requirements.txt
    python run_tests.py --verbose
``` 