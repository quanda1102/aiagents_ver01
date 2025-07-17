/**
 * Chat Widget JavaScript
 * A floating chat widget for customer support
 */

class ChatWidget {
  constructor(options = {}) {
    this.options = {
      apiUrl: options.apiUrl || '/api/v1/chat',
      position: options.position || 'bottom-right',
      theme: options.theme || 'blue',
      placeholder: options.placeholder || 'Nhập tin nhắn...',
      title: options.title || 'Hỗ trợ trực tuyến',
      subtitle: options.subtitle || 'Chúng tôi luôn sẵn sàng hỗ trợ bạn',
      sessionExpireHours: options.sessionExpireHours || 24,
      debugMode: options.debugMode || false
    };
    
    this.sessionId = null;
    this.isOpen = false;
    this.isTyping = false;
    this.widget = null;
    this.button = null;
    this.window = null;
    this.messagesContainer = null;
    this.inputField = null;
    this.sendButton = null;
    this.badge = null;
    
    // Load existing session
    this.loadSession();
  }

  /**
   * Load session from sessionStorage (primary) or localStorage (fallback)
   * Session format: { sessionId: string, timestamp: number }
   */
  loadSession() {
    try {
      let sessionData = sessionStorage.getItem('chat_widget_session_data');
      
      // Migrate from localStorage if needed
      if (!sessionData) {
        const localSessionData = localStorage.getItem('chat_widget_session_data');
        const oldLocalSessionId = localStorage.getItem('chat_widget_session_id');
        
        if (localSessionData) {
          sessionStorage.setItem('chat_widget_session_data', localSessionData);
          localStorage.removeItem('chat_widget_session_data'); // Clean up localStorage
          sessionData = localSessionData;
        } else if (oldLocalSessionId) {
          // Create new format with current timestamp (assume it's fresh)
          const migratedData = {
            sessionId: oldLocalSessionId,
            timestamp: new Date().getTime()
          };
          sessionStorage.setItem('chat_widget_session_data', JSON.stringify(migratedData));
          localStorage.removeItem('chat_widget_session_id'); // Clean up old format
          sessionData = JSON.stringify(migratedData);
        }
      }
      
      if (sessionData) {
        const { sessionId, timestamp } = JSON.parse(sessionData);
        const now = new Date().getTime();
        const expireTime = this.options.sessionExpireHours * 60 * 60 * 1000; // Convert hours to milliseconds
        
        // Check if session has expired
        if (now - timestamp < expireTime) {
          this.sessionId = sessionId;
        } else {
          this.clearSession();
        }
      }
      
      // If no valid session, sessionId will be null and server will create new one
      if (!this.sessionId) {
        this.sessionId = null;
      }
    } catch (error) {
      console.error('❌ Chat Widget - Error loading session:', error);
      this.sessionId = null;
    }
  }

  /**
   * Save session ID to both sessionStorage (primary) and localStorage (fallback)
   */
  saveSessionId(sessionId) {
    if (!sessionId) return;
    
    const sessionData = {
      sessionId: sessionId,
      timestamp: new Date().getTime()
    };
    
    try {
      sessionStorage.setItem('chat_widget_session_data', JSON.stringify(sessionData));
      this.sessionId = sessionId;
    } catch (error) {
      console.error('❌ Chat Widget - Error saving session to sessionStorage:', error);
      // Fallback: try localStorage if sessionStorage fails
      try {
        localStorage.setItem('chat_widget_session_data', JSON.stringify(sessionData));
        this.sessionId = sessionId;
      } catch (fallbackError) {
        console.error('❌ Chat Widget - Both sessionStorage and localStorage failed:', fallbackError);
      }
    }
  }

  /**
   * Clear session data from both sessionStorage and localStorage
   */
  clearSession() {
    try {
      sessionStorage.removeItem('chat_widget_session_data');
      localStorage.removeItem('chat_widget_session_data');
      // Keep old key for backward compatibility cleanup
      localStorage.removeItem('chat_widget_session_id');
      this.sessionId = null;
    } catch (error) {
      console.error('❌ Chat Widget - Error clearing session:', error);
    }
  }

  init() {
    // Test storage capabilities on init
    setTimeout(() => {
      this.checkStorageCapabilities();
    }, 500);
    
    this.createWidget();
    this.bindEvents();
    
    // Check visibility after DOM insertion
    setTimeout(() => {
      this.checkVisibility();
    }, 1000);
  }

  createWidget() {
    // Create chat widget container
    this.widget = document.createElement('div');
    this.widget.className = 'chat-widget';
    this.widget.innerHTML = this.getWidgetHTML();
    
    document.body.appendChild(this.widget);
    
    // Get references to elements
    this.button = this.widget.querySelector('.chat-widget-button');
    this.window = this.widget.querySelector('.chat-widget-window');
    this.messagesContainer = this.widget.querySelector('.chat-widget-messages');
    this.inputField = this.widget.querySelector('.chat-input-field');
    this.sendButton = this.widget.querySelector('.chat-send-button');
    this.badge = this.widget.querySelector('.chat-widget-badge');
  }

  getWidgetHTML() {
    return `
      <button class="chat-widget-button" type="button">
        <i class="ti ti-message-circle"></i>
        <i class="ti ti-x"></i>
        <span class="chat-widget-badge">1</span>
      </button>
      
      <div class="chat-widget-window">
        <div class="chat-widget-header">
          <div class="chat-widget-avatar">
            <i class="ti ti-headset"></i>
          </div>
          <div class="chat-widget-title">
            <h4>${this.options.title}</h4>
            <p>${this.options.subtitle}</p>
          </div>
          <button class="chat-widget-close" type="button">
            <i class="ti ti-x"></i>
          </button>
        </div>
        
        <div class="chat-widget-messages"></div>
        
        <div class="chat-widget-typing" style="display: none;">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <p>Đang soạn tin nhắn...</p>
        </div>
        
        <div class="chat-widget-input">
          <input type="text" class="chat-input-field" placeholder="${this.options.placeholder}" maxlength="500">
          <button class="chat-send-button" type="button">
            <i class="ti ti-send"></i>
          </button>
        </div>
      </div>
    `;
  }

  bindEvents() {
    // Toggle chat window
    this.button.addEventListener('click', () => {
      this.toggle();
    });

    // Close button
    const closeButton = this.widget.querySelector('.chat-widget-close');
    closeButton.addEventListener('click', () => {
      this.close();
    });

    // Send message on button click
    this.sendButton.addEventListener('click', () => {
      this.sendMessage();
    });

    // Send message on Enter key
    this.inputField.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Clear badge on focus
    this.inputField.addEventListener('focus', () => {
      this.clearBadge();
    });

    // Auto-resize input (basic)
    this.inputField.addEventListener('input', () => {
      // Basic input validation
      const message = this.inputField.value.trim();
      this.sendButton.disabled = message.length === 0;
    });
  }

  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  open() {
    this.isOpen = true;
    this.widget.classList.add('chat-widget-open');
    this.inputField.focus();
    this.clearBadge();
  }

  close() {
    this.isOpen = false;
    this.widget.classList.remove('chat-widget-open');
  }

  async sendMessage() {
    const message = this.inputField.value.trim();
    if (!message) return;

    // Add user message to chat
    this.addMessage({
      type: 'user',
      text: message,
      time: new Date()
    });

      // Clear input
      this.inputField.value = '';
      this.sendButton.disabled = true;

      // Show typing indicator
      this.showTyping();

    try {
      const response = await this.sendToAPI(message);
      this.hideTyping();
      
      // Add bot response
      this.addMessage({
        type: 'bot',
        text: response,
        time: new Date()
      });
    } catch (error) {
      console.error('❌ Chat Widget - Error sending message:', error);
      this.hideTyping();
      
      let errorMessage = 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.';
      
      // Handle specific error types
      if (error.message.includes('401') || error.message.includes('403')) {
        errorMessage = 'Phiên làm việc đã hết hạn. Tin nhắn tiếp theo sẽ tạo phiên mới.';
      } else if (error.message.includes('network') || error.name === 'TypeError') {
        errorMessage = 'Lỗi kết nối mạng. Vui lòng kiểm tra internet và thử lại.';
      }
      
      this.addMessage({
        type: 'bot',
        text: errorMessage,
        time: new Date()
      });
    }
  }

  async sendToAPI(message) {
    // Get auth token if available (check both storages)
    const token = sessionStorage.getItem('access_token') || localStorage.getItem('access_token');

    // Get current user metadata from auth.js functions
    let userData = {
      user_id: 0,
      user_name: 'Guest',
      user_role: 'GUEST'
    };
    
    if (typeof getCurrentUser === 'function') {
      try {
        const currentUser = await getCurrentUser();
        if (currentUser) {
          userData = {
            user_id: currentUser.id || 0,
            user_name: currentUser.full_name || currentUser.email || 'User',
            user_role: currentUser.role || 'USER'
          };
        }
      } catch (error) {
        // User not authenticated or getCurrentUser failed, keep guest defaults
      }
    }

    const requestPayload = {
      message: message,
      session_id: this.sessionId,
      user_metadata: userData
    };

    const headers = {
      'Content-Type': 'application/json'
    };

    // Add Authorization header if token exists
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(this.options.apiUrl, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(requestPayload)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Extract session_id from response and save it
    const extractedSessionId = data.session_id || data.sessionId || 
                              (data.metadata && data.metadata.session_id);
    
    if (extractedSessionId && extractedSessionId !== this.sessionId) {
      this.saveSessionId(extractedSessionId);
    }

    return this.extractMessageFromResponse(data);
  }

  extractMessageFromResponse(data) {
    // Handle various response formats
    
    // Simple string response
    if (typeof data === 'string') {
      return data;
    }
    
    // Response with direct text/message field
    if (data.response) {
      return data.response;
    }
    
    if (data.text) {
      return data.text;
    }
    
    if (data.message) {
      return data.message;
    }
    
    // Array response (check first item)
    if (Array.isArray(data) && data.length > 0) {
      const firstItem = data[0];
      
      if (typeof firstItem === 'string') {
        return firstItem;
      }
      
      if (firstItem.output) {
        return firstItem.output;
      }
      
      if (firstItem.out) {
        return firstItem.out;
      }
      
      if (firstItem.message) {
        return firstItem.message;
      }
      
      if (typeof firstItem === 'string') {
        return firstItem;
      }
    }
    
    // Fallback: try to convert to string
    return data.toString ? data.toString() : 'Phản hồi không hợp lệ từ server.';
  }

  addMessage(messageData) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message chat-message-${messageData.type}`;
    
    const time = messageData.time.toLocaleTimeString('vi-VN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
      <div class="chat-message-content">
        <p>${this.escapeHtml(messageData.text)}</p>
        <span class="chat-message-time">${time}</span>
      </div>
    `;
    
    this.messagesContainer.appendChild(messageDiv);
    this.scrollToBottom();
    
    // Show badge if window is closed and it's a bot message
    if (!this.isOpen && messageData.type === 'bot') {
      this.showBadge();
    }
  }

  showTyping() {
    this.isTyping = true;
    const typingDiv = this.widget.querySelector('.chat-widget-typing');
    typingDiv.style.display = 'flex';
    this.scrollToBottom();
  }

  hideTyping() {
    this.isTyping = false;
    const typingDiv = this.widget.querySelector('.chat-widget-typing');
    typingDiv.style.display = 'none';
  }

  scrollToBottom() {
    setTimeout(() => {
      this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }, 100);
  }

  showBadge(count = '1') {
    this.badge.textContent = count;
    this.badge.style.display = 'block';
  }

  clearBadge() {
    this.badge.style.display = 'none';
  }

  // Public methods for external control
  getCurrentSessionId() {
    return this.sessionId;
  }

  getSessionInfo() {
    try {
      const sessionData = sessionStorage.getItem('chat_widget_session_data') || 
                         localStorage.getItem('chat_widget_session_data');
      return sessionData ? JSON.parse(sessionData) : null;
    } catch (error) {
      console.error('❌ Chat Widget - Error getting session info:', error);
      return null;
    }
  }

  resetSession() {
    this.clearSession();
  }

  // Debug methods
  makeSuperVisible() {
    if (this.widget) {
      this.widget.style.backgroundColor = 'red';
      this.widget.style.border = '5px solid yellow';
      this.widget.style.zIndex = '999999';
      this.button.style.animation = 'pulse 1s infinite';
    }
  }

  makeNormal() {
    if (this.widget) {
      this.widget.style.backgroundColor = '';
      this.widget.style.border = '';
      this.widget.style.zIndex = '';
      this.button.style.animation = '';
    }
  }

  checkStorageCapabilities() {
    const result = {
      sessionStorage: false,
      localStorage: false,
      quota: null
    };

    // Test sessionStorage
    try {
      sessionStorage.setItem('test', 'test');
      sessionStorage.removeItem('test');
      result.sessionStorage = true;
    } catch (e) {
      result.sessionStorage = false;
    }

    // Test localStorage  
    try {
      localStorage.setItem('test', 'test');
      localStorage.removeItem('test');
      result.localStorage = true;
    } catch (e) {
      result.localStorage = false;
    }

    // Try to estimate quota
    if (navigator.storage && navigator.storage.estimate) {
      navigator.storage.estimate().then(estimate => {
        result.quota = estimate;
      });
    }

    return result;
  }
}

// Debug tools (only available in development)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  window.addEventListener('load', function() {
    setTimeout(() => {
      if (window.chatWidget) {
      }
    }, 2000);
  });
} 