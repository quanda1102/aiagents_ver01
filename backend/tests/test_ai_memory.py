"""
Comprehensive unit tests for the AI Memory Service
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import redis
from datetime import datetime

# Import the service we're testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.ai_memory import AIMemoryService


class TestAIMemoryService(unittest.TestCase):
    """Test cases for AIMemoryService class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_redis_client = Mock()
        self.sample_user_data = {
            "user_id": "test_user_123",
            "user_name": "Test User",
            "user_email": "test@example.com",
            "session_id": "test_session_456",
            "user_message": "Hello, I need help with testing"
        }

    @patch('services.ai_memory.redis.Redis')
    def test_init_successful_connection(self, mock_redis):
        """Test successful Redis connection during initialization"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        service = AIMemoryService()
        
        self.assertIsNotNone(service.client)
        mock_client.ping.assert_called_once()

    @patch('services.ai_memory.redis.Redis')
    def test_init_failed_connection(self, mock_redis):
        """Test failed Redis connection during initialization"""
        mock_redis.side_effect = redis.ConnectionError("Connection failed")
        
        service = AIMemoryService()
        
        self.assertIsNone(service.client)

    @patch('services.ai_memory.logger')
    @patch('services.ai_memory.redis.Redis')
    def test_init_logs_connection_status(self, mock_redis, mock_logger):
        """Test that initialization logs connection status"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        AIMemoryService()
        
        mock_logger.info.assert_called_with("Successfully connected to Redis")

    def test_store_message_success(self):
        """Test successful message storage"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        
        # Mock existing conversation retrieval
        service.get_conversation_history = Mock(return_value=[])
        
        result = service.store_message("user123", "session456", "user", "Test message")
        
        self.assertTrue(result)
        self.mock_redis_client.set.assert_called_once()

    def test_store_message_no_client(self):
        """Test message storage when Redis client is not available"""
        service = AIMemoryService()
        service.client = None
        
        result = service.store_message("user123", "session456", "user", "Test message")
        
        self.assertFalse(result)

    @patch('services.ai_memory.logger')
    def test_store_message_logs_error_on_exception(self, mock_logger):
        """Test that store_message logs errors when exceptions occur"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        service.get_conversation_history = Mock(side_effect=Exception("Test error"))
        
        result = service.store_message("user123", "session456", "user", "Test message")
        
        self.assertFalse(result)
        mock_logger.error.assert_called()

    def test_get_conversation_history_success(self):
        """Test successful conversation history retrieval"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        
        mock_conversation = [
            {"role": "user", "content": "Hello", "timestamp": "2024-01-01T10:00:00"},
            {"role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01T10:00:01"}
        ]
        self.mock_redis_client.get.return_value = json.dumps(mock_conversation)
        
        result = service.get_conversation_history("user123", "session456")
        
        self.assertEqual(result, mock_conversation)
        self.mock_redis_client.get.assert_called_with("chat:user123:session456")

    def test_get_conversation_history_no_data(self):
        """Test conversation history retrieval when no data exists"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        self.mock_redis_client.get.return_value = None
        
        result = service.get_conversation_history("user123", "session456")
        
        self.assertEqual(result, [])

    def test_get_conversation_history_max_limit(self):
        """Test conversation history retrieval with max_history limit"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        
        # Create a conversation with 10 messages
        mock_conversation = [
            {"role": "user", "content": f"Message {i}", "timestamp": f"2024-01-01T10:00:{i:02d}"}
            for i in range(10)
        ]
        self.mock_redis_client.get.return_value = json.dumps(mock_conversation)
        
        result = service.get_conversation_history("user123", "session456", max_history=5)
        
        self.assertEqual(len(result), 5)
        self.assertEqual(result, mock_conversation[-5:])  # Should get the last 5 messages

    def test_get_conversation_history_no_client(self):
        """Test conversation history retrieval when Redis client is not available"""
        service = AIMemoryService()
        service.client = None
        
        result = service.get_conversation_history("user123", "session456")
        
        self.assertIsNone(result)

    def test_store_user_request_success(self):
        """Test successful user request storage"""
        service = AIMemoryService()
        service.store_message = Mock(return_value=True)
        
        result = service.store_user_request(self.sample_user_data)
        
        self.assertTrue(result)
        service.store_message.assert_called_once_with(
            "test_user_123", 
            "test_session_456", 
            "user", 
            "Hello, I need help with testing",
            {'user_name': 'Test User', 'user_email': 'test@example.com'}
        )

    def test_store_user_request_missing_fields(self):
        """Test user request storage with missing required fields"""
        service = AIMemoryService()
        
        incomplete_data = {"user_id": "123"}  # Missing session_id and user_message
        
        result = service.store_user_request(incomplete_data)
        
        self.assertFalse(result)

    @patch('services.ai_memory.logger')
    def test_store_user_request_logs_missing_fields(self, mock_logger):
        """Test that store_user_request logs error for missing fields"""
        service = AIMemoryService()
        
        incomplete_data = {"user_id": "123"}
        service.store_user_request(incomplete_data)
        
        mock_logger.error.assert_called_with("Missing required fields: user_id, session_id, or user_message")

    def test_store_assistant_response_success(self):
        """Test successful assistant response storage"""
        service = AIMemoryService()
        service.store_message = Mock(return_value=True)
        
        result = service.store_assistant_response("user123", "session456", "Test response", {"key": "value"})
        
        self.assertTrue(result)
        service.store_message.assert_called_once_with("user123", "session456", "assistant", "Test response", {"key": "value"})

    def test_clear_conversation_success(self):
        """Test successful conversation clearing"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        
        result = service.clear_conversation("user123", "session456")
        
        self.assertTrue(result)
        self.mock_redis_client.delete.assert_called_once_with("chat:user123:session456")

    def test_clear_conversation_no_client(self):
        """Test conversation clearing when Redis client is not available"""
        service = AIMemoryService()
        service.client = None
        
        result = service.clear_conversation("user123", "session456")
        
        self.assertFalse(result)

    @patch('services.ai_memory.logger')
    def test_clear_conversation_logs_error_on_exception(self, mock_logger):
        """Test that clear_conversation logs errors when exceptions occur"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        self.mock_redis_client.delete.side_effect = Exception("Test error")
        
        result = service.clear_conversation("user123", "session456")
        
        self.assertFalse(result)
        mock_logger.error.assert_called()

    def test_get_formatted_chat_history_with_data(self):
        """Test formatted chat history with existing conversation"""
        service = AIMemoryService()
        
        mock_conversation = [
            {"role": "user", "content": "Hello", "timestamp": "2024-01-01T10:00:00", "metadata": {}},
            {"role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01T10:00:01", "metadata": {}}
        ]
        service.get_conversation_history = Mock(return_value=mock_conversation)
        
        result = service.get_formatted_chat_history("user123", "session456")
        
        expected = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        self.assertEqual(result, expected)

    def test_get_formatted_chat_history_no_data(self):
        """Test formatted chat history with no existing conversation"""
        service = AIMemoryService()
        service.get_conversation_history = Mock(return_value=None)
        
        result = service.get_formatted_chat_history("user123", "session456")
        
        expected = [{"role": "system", "content": "You are a helpful assistant."}]
        self.assertEqual(result, expected)

    def test_get_formatted_chat_history_empty_conversation(self):
        """Test formatted chat history with empty conversation"""
        service = AIMemoryService()
        service.get_conversation_history = Mock(return_value=[])
        
        result = service.get_formatted_chat_history("user123", "session456")
        
        expected = [{"role": "system", "content": "You are a helpful assistant."}]
        self.assertEqual(result, expected)

    def test_get_formatted_chat_history_respects_max_history(self):
        """Test that formatted chat history respects max_history parameter"""
        service = AIMemoryService()
        
        mock_conversation = [
            {"role": "user", "content": f"Message {i}", "timestamp": f"2024-01-01T10:00:{i:02d}", "metadata": {}}
            for i in range(5)
        ]
        service.get_conversation_history = Mock(return_value=mock_conversation)
        
        result = service.get_formatted_chat_history("user123", "session456", max_history=3)
        
        # Should call get_conversation_history with max_history=3
        service.get_conversation_history.assert_called_with("user123", "session456", 3)

    @patch('services.ai_memory.datetime')
    def test_store_message_includes_timestamp(self, mock_datetime):
        """Test that store_message includes correct timestamp"""
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        service = AIMemoryService()
        service.client = self.mock_redis_client
        service.get_conversation_history = Mock(return_value=[])
        
        service.store_message("user123", "session456", "user", "Test message")
        
        # Verify that the stored data includes the timestamp
        call_args = self.mock_redis_client.set.call_args
        stored_data = json.loads(call_args[0][1])
        self.assertEqual(stored_data[0]["timestamp"], "2024-01-01T12:00:00")

    def test_store_message_preserves_metadata(self):
        """Test that store_message preserves metadata correctly"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        service.get_conversation_history = Mock(return_value=[])
        
        metadata = {"task_id": "TASK_001", "priority": "high"}
        service.store_message("user123", "session456", "user", "Test message", metadata)
        
        # Verify that the stored data includes the metadata
        call_args = self.mock_redis_client.set.call_args
        stored_data = json.loads(call_args[0][1])
        self.assertEqual(stored_data[0]["metadata"], metadata)

    def test_store_message_handles_none_metadata(self):
        """Test that store_message handles None metadata correctly"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        service.get_conversation_history = Mock(return_value=[])
        
        service.store_message("user123", "session456", "user", "Test message", None)
        
        # Verify that metadata defaults to empty dict
        call_args = self.mock_redis_client.set.call_args
        stored_data = json.loads(call_args[0][1])
        self.assertEqual(stored_data[0]["metadata"], {})

    def test_redis_key_format(self):
        """Test that Redis keys are formatted correctly"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        service.get_conversation_history = Mock(return_value=[])
        
        service.store_message("user_123", "session_456", "user", "Test message")
        
        # Verify the Redis key format
        call_args = self.mock_redis_client.set.call_args
        redis_key = call_args[0][0]
        self.assertEqual(redis_key, "chat:user_123:session_456")

    @patch('services.ai_memory.logger')
    def test_get_conversation_history_logs_info_for_no_data(self, mock_logger):
        """Test that get_conversation_history logs info when no data is found"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        self.mock_redis_client.get.return_value = None
        
        service.get_conversation_history("user123", "session456")
        
        mock_logger.info.assert_called_with("No conversation history found for user user123, session session456")

    def test_integration_full_conversation_flow(self):
        """Integration test for a complete conversation flow"""
        service = AIMemoryService()
        service.client = self.mock_redis_client
        
        # Mock Redis to return progressively building conversation
        stored_conversations = []
        
        def mock_get(key):
            if stored_conversations:
                return json.dumps(stored_conversations[-1])
            return None
        
        def mock_set(key, value):
            stored_conversations.append(json.loads(value))
        
        self.mock_redis_client.get.side_effect = mock_get
        self.mock_redis_client.set.side_effect = mock_set
        
        # Simulate a conversation
        user_request = {
            "user_id": "integration_user",
            "session_id": "integration_session",
            "user_message": "Hello, I need help"
        }
        
        # Store user request
        result1 = service.store_user_request(user_request)
        self.assertTrue(result1)
        
        # Store assistant response
        result2 = service.store_assistant_response("integration_user", "integration_session", "How can I help you?")
        self.assertTrue(result2)
        
        # Verify conversation history
        history = service.get_conversation_history("integration_user", "integration_session")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["role"], "assistant")
        
        # Test formatted history
        formatted = service.get_formatted_chat_history("integration_user", "integration_session")
        self.assertEqual(len(formatted), 3)  # system + user + assistant
        self.assertEqual(formatted[0]["role"], "system")


class TestAIMemoryServiceEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for AIMemoryService"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.service = AIMemoryService()
        self.service.client = Mock()

    def test_empty_string_parameters(self):
        """Test behavior with empty string parameters"""
        result = self.service.store_message("", "", "user", "")
        # Should still work with empty strings
        self.assertTrue(result)

    def test_very_long_message(self):
        """Test behavior with very long messages"""
        long_message = "x" * 10000  # 10KB message
        self.service.get_conversation_history = Mock(return_value=[])
        
        result = self.service.store_message("user123", "session456", "user", long_message)
        self.assertTrue(result)

    def test_special_characters_in_ids(self):
        """Test behavior with special characters in user/session IDs"""
        special_user_id = "user@#$%^&*()"
        special_session_id = "session!@#$%"
        self.service.get_conversation_history = Mock(return_value=[])
        
        result = self.service.store_message(special_user_id, special_session_id, "user", "Test message")
        self.assertTrue(result)

    def test_unicode_content(self):
        """Test behavior with Unicode content"""
        unicode_message = "Hello 🌍 世界 🚀 مرحبا"
        self.service.get_conversation_history = Mock(return_value=[])
        
        result = self.service.store_message("user123", "session456", "user", unicode_message)
        self.assertTrue(result)

    def test_invalid_json_in_redis(self):
        """Test behavior when Redis contains invalid JSON"""
        self.service.client.get.return_value = "invalid json data"
        
        with patch('services.ai_memory.logger') as mock_logger:
            result = self.service.get_conversation_history("user123", "session456")
            self.assertIsNone(result)
            mock_logger.error.assert_called()


if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test cases
    test_suite.addTest(unittest.makeSuite(TestAIMemoryService))
    test_suite.addTest(unittest.makeSuite(TestAIMemoryServiceEdgeCases))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}") 