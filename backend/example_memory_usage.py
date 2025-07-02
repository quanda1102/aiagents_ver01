"""
Example demonstrating how to use the AI Memory Service with your agents
"""

from services.ai_memory import AIMemoryService
import json

def example_conversation_flow():
    """Example of a complete conversation flow with memory"""
    
    # Initialize the memory service
    memory = AIMemoryService()
    
    # Simulate a user session
    user_data = {
        "user_id": "user_123",
        "user_name": "John Doe",
        "user_email": "john@example.com",
        "session_id": "session_456",
        "user_message": "Hello, I need help with my project management"
    }
    
    print("🚀 Starting conversation simulation...")
    
    # 1. Store the initial user request
    if memory.store_user_request(user_data):
        print(f"✅ Stored user message: '{user_data['user_message']}'")
    
    # 2. Simulate AI agent processing and store response
    ai_response = "Hello! I'd be happy to help you with project management. What specific aspect would you like assistance with?"
    if memory.store_assistant_response(user_data["user_id"], user_data["session_id"], ai_response):
        print(f"✅ Stored AI response: '{ai_response[:50]}...'")
    
    # 3. Continue the conversation
    follow_up_message = "I need to create a task tracking system"
    memory.store_message(user_data["user_id"], user_data["session_id"], "user", follow_up_message)
    print(f"✅ Stored follow-up: '{follow_up_message}'")
    
    ai_response_2 = "Great! I can help you create a task tracking system. Let me break this down into steps..."
    memory.store_assistant_response(user_data["user_id"], user_data["session_id"], ai_response_2)
    print(f"✅ Stored AI response 2: '{ai_response_2[:50]}...'")
    
    # 4. Retrieve and display conversation history
    print("\n📚 Retrieving conversation history:")
    history = memory.get_conversation_history(user_data["user_id"], user_data["session_id"])
    
    if history:
        for i, msg in enumerate(history, 1):
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            print(f"{i}. {role_emoji} [{msg['role']}] {msg['timestamp'][:19]}: {msg['content']}")
    
    # 5. Get formatted history for AI model
    print(f"\n🎯 Formatted history for AI model:")
    formatted = memory.get_formatted_chat_history(user_data["user_id"], user_data["session_id"])
    for msg in formatted:
        print(f"  {msg['role']}: {msg['content'][:60]}...")
    
    return memory, user_data

def example_agent_integration():
    """Example of how to integrate memory with your AI agents"""
    
    memory = AIMemoryService()
    
    # Example user request for task management
    user_request = {
        "user_id": "user_789",
        "session_id": "session_abc",
        "user_message": "Create a new task for website deployment",
        "task_priority": "high",
        "task_category": "development"
    }
    
    print("\n🔧 Agent Integration Example:")
    
    # Store the user request
    memory.store_user_request(user_request)
    
    # Get conversation history to provide context to the agent
    chat_history = memory.get_formatted_chat_history(
        user_request["user_id"], 
        user_request["session_id"]
    )
    
    # Simulate agent processing with memory context
    print(f"📝 Agent received context: {len(chat_history)} previous messages")
    
    # Agent processes and responds
    agent_response = {
        "task_created": True,
        "task_id": "TASK_001",
        "message": "I've created a high-priority task for website deployment. Task ID: TASK_001"
    }
    
    # Store agent response with metadata
    memory.store_assistant_response(
        user_request["user_id"],
        user_request["session_id"],
        agent_response["message"],
        metadata={"task_id": agent_response["task_id"], "task_created": True}
    )
    
    print(f"✅ Agent response stored with task metadata")
    
    return memory

def example_memory_management():
    """Example of memory management operations"""
    
    memory = AIMemoryService()
    
    print("\n🗂️ Memory Management Examples:")
    
    # Test connection
    if memory.client:
        try:
            memory.client.ping()
            print("✅ Redis connection is working")
        except:
            print("❌ Redis connection failed - make sure Redis is running")
            return
    
    # Create multiple conversations for testing
    users = ["user_1", "user_2", "user_3"]
    sessions = ["session_a", "session_b"]
    
    for user in users:
        for session in sessions:
            test_message = f"Test message from {user} in {session}"
            memory.store_message(user, session, "user", test_message)
    
    print(f"✅ Created test conversations for {len(users)} users across {len(sessions)} sessions")
    
    # Retrieve specific conversation
    conversation = memory.get_conversation_history("user_1", "session_a")
    print(f"📖 Retrieved conversation: {len(conversation)} messages")
    
    # Clean up test data
    for user in users:
        for session in sessions:
            memory.clear_conversation(user, session)
    
    print("🧹 Cleaned up test conversations")

if __name__ == "__main__":
    print("=== AI Memory Service Examples ===\n")
    
    # Run examples
    example_conversation_flow()
    example_agent_integration()
    example_memory_management()
    
    print("\n✨ All examples completed!")
    print("\n💡 Tips for using the AI Memory Service:")
    print("1. Always check if Redis is running before using the service")
    print("2. Use meaningful user_id and session_id combinations")
    print("3. Store metadata with messages for better context")
    print("4. Use get_formatted_chat_history() when feeding data to AI models")
    print("5. Set appropriate max_history limits to manage memory usage") 