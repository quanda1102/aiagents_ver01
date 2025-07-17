/**
 * Chat Widget JavaScript
 * A floating chat widget for customer support with built-in testing capabilities
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
      debugMode: options.debugMode || false,
      testMode: options.testMode || false
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
    
    // Test results storage
    this.testResults = [];
    this.testStartTime = null;
    
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
    console.log('🚀 Chat Widget - Starting initialization');
    this.testStartTime = new Date();
    
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
    
    // Run auto-tests if test mode is enabled
    if (this.options.testMode) {
      setTimeout(() => {
        this.runAutoTests();
      }, 2000);
    }
    
    console.log('✅ Chat Widget - Initialization complete');
    this.logTestResult('Initialization', 'SUCCESS', 'Chat widget initialized successfully');
  }

  createWidget() {
    console.log('🏗️ Chat Widget - Creating widget');
    
    // Create chat widget container
    this.widget = document.createElement('div');
    this.widget.className = 'chat-widget';
    if (this.options.testMode) {
      this.widget.classList.add('test-mode');
    }
    this.widget.innerHTML = this.getWidgetHTML();
    
    document.body.appendChild(this.widget);
    console.log('✅ Chat Widget - Widget added to DOM');
    
    // Get references to elements
    this.button = this.widget.querySelector('.chat-widget-button');
    this.window = this.widget.querySelector('.chat-widget-window');
    this.messagesContainer = this.widget.querySelector('.chat-widget-messages');
    this.inputField = this.widget.querySelector('.chat-input-field');
    this.sendButton = this.widget.querySelector('.chat-send-button');
    this.badge = this.widget.querySelector('.chat-widget-badge');
    
    // Log element creation status
    console.log('🔗 Chat Widget - Element references:');
    console.log('  - Button:', !!this.button);
    console.log('  - Window:', !!this.window);
    console.log('  - Messages Container:', !!this.messagesContainer);
    console.log('  - Input Field:', !!this.inputField);
    console.log('  - Send Button:', !!this.sendButton);
    console.log('  - Badge:', !!this.badge);
    
    // Test controls are already included in getWidgetHTML() when testMode is true
  }

  getWidgetHTML() {
    const testControls = this.options.testMode ? `
      <div class="chat-widget-test-panel" style="position: absolute; top: -300px; right: 0; width: 300px; background: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 1000;">
        <h6 style="margin: 0 0 10px 0; color: #333;">🧪 Chat Widget Test Panel</h6>
        <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px;">
          <button onclick="window.chatWidget.testOpen()" style="padding: 5px 8px; font-size: 11px; border: 1px solid #007bff; background: #007bff; color: white; border-radius: 4px; cursor: pointer;">Open</button>
          <button onclick="window.chatWidget.testClose()" style="padding: 5px 8px; font-size: 11px; border: 1px solid #6c757d; background: #6c757d; color: white; border-radius: 4px; cursor: pointer;">Close</button>
          <button onclick="window.chatWidget.testBadge()" style="padding: 5px 8px; font-size: 11px; border: 1px solid #28a745; background: #28a745; color: white; border-radius: 4px; cursor: pointer;">Badge</button>
          <button onclick="window.chatWidget.testMessage()" style="padding: 5px 8px; font-size: 11px; border: 1px solid #ffc107; background: #ffc107; color: black; border-radius: 4px; cursor: pointer;">Message</button>
          <button onclick="window.chatWidget.testApiConnection()" style="padding: 5px 8px; font-size: 11px; border: 1px solid #dc3545; background: #dc3545; color: white; border-radius: 4px; cursor: pointer;">API Test</button>
          <button onclick="window.chatWidget.debug()" style="padding: 5px 8px; font-size: 11px; border: 1px solid #17a2b8; background: #17a2b8; color: white; border-radius: 4px; cursor: pointer;">Debug</button>
          <button onclick="window.chatWidget.showTestResults()" style="padding: 5px 8px; font-size: 11px; border: 1px solid #6f42c1; background: #6f42c1; color: white; border-radius: 4px; cursor: pointer;">Results</button>
        </div>
        <div id="testOutput" style="font-size: 10px; max-height: 100px; overflow-y: auto; background: #f8f9fa; padding: 5px; border-radius: 3px; font-family: monospace;"></div>
      </div>
    ` : '';

    return `
      ${testControls}
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
    // Check if elements exist before binding events
    if (!this.button) {
      console.error('❌ Chat Widget - Button element not found');
      this.logTestResult('Button Events', 'FAILED', 'Button element not found');
      return;
    }

    // Toggle chat window
    this.button.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log('🔄 Chat Widget - Button clicked'); // Debug log
      this.toggle();
    });

    // Close button
    const closeButton = this.widget.querySelector('.chat-widget-close');
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        this.close();
      });
    }

    // Send message on button click
    if (this.sendButton) {
      this.sendButton.addEventListener('click', () => {
        this.sendMessage();
      });
    }

    // Send message on Enter key
    if (this.inputField) {
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
        if (this.sendButton) {
          this.sendButton.disabled = message.length === 0;
        }
      });
    }
    
    this.logTestResult('Event Binding', 'SUCCESS', 'All events bound successfully');
  }

  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  open() {
    console.log('🔓 Chat Widget - Opening window'); // Debug log
    this.isOpen = true;
    
    if (this.button) {
      this.button.classList.add('active');
    }
    
    if (this.window) {
      this.window.classList.add('show');
      console.log('✅ Chat Widget - Window should now be visible'); // Debug log
      this.logTestResult('Open Window', 'SUCCESS', 'Chat window opened successfully');
    } else {
      console.error('❌ Chat Widget - Window element not found');
      this.logTestResult('Open Window', 'FAILED', 'Window element not found');
    }
    
    if (this.inputField) {
      setTimeout(() => this.inputField.focus(), 100);
    }
    
    this.clearBadge();
  }

  close() {
    console.log('🔒 Chat Widget - Closing window'); // Debug log
    this.isOpen = false;
    
    if (this.button) {
      this.button.classList.remove('active');
    }
    
    if (this.window) {
      this.window.classList.remove('show');
      this.logTestResult('Close Window', 'SUCCESS', 'Chat window closed successfully');
    }
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
      
      this.logTestResult('Send Message', 'SUCCESS', 'Message sent and response received');
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
      
      this.logTestResult('Send Message', 'FAILED', 'Error: ' + error.message);
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
    if (this.badge) {
      this.badge.textContent = count;
      this.badge.classList.add('show');
      this.logTestResult('Show Badge', 'SUCCESS', `Badge shown with count: ${count}`);
    }
  }

  clearBadge() {
    if (this.badge) {
      this.badge.classList.remove('show');
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  checkVisibility() {
    if (!this.widget) {
      console.error('❌ Chat Widget - Widget not found during visibility check');
      this.logTestResult('Visibility Check', 'FAILED', 'Widget element not found');
      return;
    }

    const isVisible = this.widget.offsetParent !== null;
    const hasCorrectPosition = getComputedStyle(this.widget).position === 'fixed';
    
    console.log('👁️ Chat Widget - Visibility check:', { isVisible, hasCorrectPosition });
    
    if (isVisible && hasCorrectPosition) {
      this.logTestResult('Visibility Check', 'SUCCESS', 'Widget is visible and positioned correctly');
    } else {
      this.logTestResult('Visibility Check', 'FAILED', `Visible: ${isVisible}, Position: ${hasCorrectPosition}`);
    }
  }

  // Test Methods
  logTestResult(testName, status, details) {
    const timestamp = new Date().toLocaleTimeString();
    const result = {
      timestamp,
      testName,
      status,
      details,
      duration: this.testStartTime ? new Date() - this.testStartTime : 0
    };
    
    this.testResults.push(result);
    
    const emoji = status === 'SUCCESS' ? '✅' : status === 'FAILED' ? '❌' : '⚠️';
    console.log(`${emoji} [${timestamp}] ${testName}: ${status} - ${details}`);
    
    // Update test output if in test mode
    if (this.options.testMode) {
      this.updateTestOutput(result);
    }
  }

  updateTestOutput(result) {
    const testOutput = document.getElementById('testOutput');
    if (testOutput) {
      const emoji = result.status === 'SUCCESS' ? '✅' : result.status === 'FAILED' ? '❌' : '⚠️';
      const line = document.createElement('div');
      line.style.color = result.status === 'SUCCESS' ? '#28a745' : result.status === 'FAILED' ? '#dc3545' : '#ffc107';
      line.innerHTML = `${emoji} ${result.testName}: ${result.status}`;
      line.title = result.details;
      testOutput.appendChild(line);
      testOutput.scrollTop = testOutput.scrollHeight;
    }
  }

  runAutoTests() {
    console.log('🧪 Running automatic tests...');
    
    setTimeout(() => this.testElementsExist(), 100);
    setTimeout(() => this.testOpen(), 500);
    setTimeout(() => this.testClose(), 1000);
    setTimeout(() => this.testBadge(), 1500);
    setTimeout(() => this.testMessage(), 2000);
    setTimeout(() => this.testApiConnection(), 2500);
    
    console.log('🏁 Auto-tests completed');
  }

  testElementsExist() {
    console.log('🧪 Testing element existence...');
    
    const elements = [
      { name: 'Widget', element: this.widget },
      { name: 'Button', element: this.button },
      { name: 'Window', element: this.window },
      { name: 'Messages Container', element: this.messagesContainer },
      { name: 'Input Field', element: this.inputField },
      { name: 'Send Button', element: this.sendButton },
      { name: 'Badge', element: this.badge }
    ];
    
    elements.forEach(({ name, element }) => {
      if (element) {
        this.logTestResult(`Element ${name}`, 'SUCCESS', 'Element exists and is accessible');
      } else {
        this.logTestResult(`Element ${name}`, 'FAILED', 'Element not found');
      }
    });
  }

  testOpen() {
    console.log('🧪 Testing widget open...');
    try {
      this.open();
      const isOpen = this.isOpen && this.window && this.window.classList.contains('show');
      if (isOpen) {
        this.logTestResult('Test Open', 'SUCCESS', 'Widget opened successfully');
      } else {
        this.logTestResult('Test Open', 'FAILED', 'Widget did not open properly');
      }
    } catch (error) {
      this.logTestResult('Test Open', 'FAILED', 'Error: ' + error.message);
    }
  }

  testClose() {
    console.log('🧪 Testing widget close...');
    try {
      this.close();
      const isClosed = !this.isOpen && (!this.window || !this.window.classList.contains('show'));
      if (isClosed) {
        this.logTestResult('Test Close', 'SUCCESS', 'Widget closed successfully');
      } else {
        this.logTestResult('Test Close', 'FAILED', 'Widget did not close properly');
      }
    } catch (error) {
      this.logTestResult('Test Close', 'FAILED', 'Error: ' + error.message);
    }
  }

  testBadge() {
    console.log('🧪 Testing badge functionality...');
    try {
      this.showBadge('5');
      const isVisible = this.badge && this.badge.classList.contains('show');
      if (isVisible) {
        this.logTestResult('Test Badge', 'SUCCESS', 'Badge displayed successfully');
      } else {
        this.logTestResult('Test Badge', 'FAILED', 'Badge not visible');
      }
    } catch (error) {
      this.logTestResult('Test Badge', 'FAILED', 'Error: ' + error.message);
    }
  }

  testMessage() {
    console.log('🧪 Testing message functionality...');
    try {
      const testMsg = {
        type: 'bot',
        text: '🧪 This is a test message from the automated testing system!',
        time: new Date()
      };
      
      this.addMessage(testMsg);
      
      // Check if message was added
      const messages = this.messagesContainer.querySelectorAll('.chat-message');
      const hasTestMessage = Array.from(messages).some(msg => 
        msg.textContent.includes('🧪 This is a test message')
      );
      
      if (hasTestMessage) {
        this.logTestResult('Test Message', 'SUCCESS', 'Test message added successfully');
      } else {
        this.logTestResult('Test Message', 'FAILED', 'Test message not found in chat');
      }
    } catch (error) {
      this.logTestResult('Test Message', 'FAILED', 'Error: ' + error.message);
    }
  }

  showTestResults() {
    console.log('📊 Chat Widget Test Results:');
    console.log('============================');
    
    const summary = {
      total: this.testResults.length,
      success: this.testResults.filter(r => r.status === 'SUCCESS').length,
      failed: this.testResults.filter(r => r.status === 'FAILED').length,
      warnings: this.testResults.filter(r => r.status === 'WARNING').length
    };
    
    console.log(`Total Tests: ${summary.total}`);
    console.log(`✅ Success: ${summary.success}`);
    console.log(`❌ Failed: ${summary.failed}`);
    console.log(`⚠️ Warnings: ${summary.warnings}`);
    console.log('');
    
    this.testResults.forEach(result => {
      const emoji = result.status === 'SUCCESS' ? '✅' : result.status === 'FAILED' ? '❌' : '⚠️';
      console.log(`${emoji} [${result.timestamp}] ${result.testName}: ${result.details}`);
    });
    
    // Create visual report if in test mode
    if (this.options.testMode) {
      alert(`Test Results:\n✅ Success: ${summary.success}\n❌ Failed: ${summary.failed}\n⚠️ Warnings: ${summary.warnings}\n\nCheck console for details.`);
    }
    
    return summary;
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

    this.logTestResult('Storage Check', 'SUCCESS', 
      `SessionStorage: ${result.sessionStorage}, LocalStorage: ${result.localStorage}`);

    return result;
  }

  // Debug method to check widget state
  debug() {
    console.log('🔍 Chat Widget Debug Info:');
    console.log('- Widget element:', this.widget);
    console.log('- Button element:', this.button);
    console.log('- Window element:', this.window);
    console.log('- Is open:', this.isOpen);
    console.log('- Session ID:', this.sessionId);
    console.log('- Test mode:', this.options.testMode);
    console.log('- Test results count:', this.testResults.length);
    
    if (this.button) {
      console.log('- Button classes:', this.button.className);
      console.log('- Button in DOM:', document.body.contains(this.button));
    }
    
    if (this.window) {
      console.log('- Window classes:', this.window.className);
      console.log('- Window computed style:', getComputedStyle(this.window).visibility);
    }
    
    // Test click functionality
    if (this.button) {
      console.log('🧪 Testing button click...');
      this.button.click();
    }
    
    this.logTestResult('Debug Check', 'SUCCESS', 'Debug information displayed in console');
  }

  // Enable test mode
  enableTestMode() {
    this.options.testMode = true;
    if (this.widget) {
      this.widget.classList.add('test-mode');
      // Recreate widget with test controls
      this.widget.innerHTML = this.getWidgetHTML();
      this.bindEvents();
    }
    console.log('🧪 Test mode enabled');
  }

  // Test API connection
  async testApiConnection() {
    console.log('🧪 Testing API connection to:', this.options.apiUrl);
    
    try {
      const testPayload = {
        message: "Hello, this is a test message",
        session_id: null,
        user_metadata: {
          user_id: 0,
          user_name: "Test User",
          user_role: "GUEST"
        }
      };

      console.log('📤 Sending test request:', testPayload);

      const response = await fetch(this.options.apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testPayload)
      });

      console.log('📥 Response status:', response.status);
      console.log('📥 Response headers:', [...response.headers.entries()]);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ API Test SUCCESS:', data);
        this.logTestResult('API Connection', 'SUCCESS', `Connected to ${this.options.apiUrl}`);
        return data;
      } else {
        const errorText = await response.text();
        console.error('❌ API Test FAILED:', response.status, errorText);
        this.logTestResult('API Connection', 'FAILED', `HTTP ${response.status}: ${errorText}`);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
    } catch (error) {
      console.error('❌ API Test ERROR:', error);
      this.logTestResult('API Connection', 'FAILED', `Error: ${error.message}`);
      throw error;
    }
  }

  // Disable test mode
  disableTestMode() {
    this.options.testMode = false;
    if (this.widget) {
      this.widget.classList.remove('test-mode');
      // Recreate widget without test controls
      this.widget.innerHTML = this.getWidgetHTML();
      this.bindEvents();
    }
    console.log('🧪 Test mode disabled');
  }
}

// Global helper functions for easy testing
window.chatWidgetTest = {
  enable: () => {
    if (window.chatWidget) {
      window.chatWidget.enableTestMode();
    } else {
      console.error('Chat widget not found');
    }
  },
  
  disable: () => {
    if (window.chatWidget) {
      window.chatWidget.disableTestMode();
    }
  },
  
  results: () => {
    if (window.chatWidget) {
      return window.chatWidget.showTestResults();
    }
  },
  
  debug: () => {
    if (window.chatWidget) {
      window.chatWidget.debug();
    }
  },
  
  autoTest: () => {
    if (window.chatWidget) {
      window.chatWidget.runAutoTests();
    }
  },
  
  apiTest: () => {
    if (window.chatWidget) {
      return window.chatWidget.testApiConnection();
    }
  }
};

// Debug tools (only available in development)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  window.addEventListener('load', function() {
    setTimeout(() => {
      if (window.chatWidget) {
        console.log('🔧 Development mode detected. Additional commands available:');
        console.log('- window.chatWidgetTest.enable() - Enable test mode');
        console.log('- window.chatWidgetTest.results() - Show test results');
        console.log('- window.chatWidgetTest.debug() - Debug widget');
        console.log('- window.chatWidgetTest.autoTest() - Run auto tests');
        console.log('- window.chatWidgetTest.apiTest() - Test API connection');
      }
    }, 2000);
  });
} 