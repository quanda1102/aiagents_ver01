/**
 * Chat Widget JavaScript
 * A floating chat widget for customer support
 */

class ChatWidget {
  constructor(options = {}) {
    this.options = {
      title: 'Trợ lý Quân',
      subtitle: 'Xin chào tớ có thể giúp gì được cậu không',
      placeholder: 'Nhập tin nhắn...',
      apiUrl: options.apiUrl || 'https://aimarketingvn.com/webhook/chat',
      initialMessages: [
        {
          type: 'bot',
          text: 'Xin chào! Tôi có thể giúp gì cho bạn hôm nay?',
          time: new Date()
        }
      ],
      ...options
    };
    
    this.isOpen = false;
    this.messages = [...this.options.initialMessages];
    this.isTyping = false;
    
    // Try to load existing session ID from localStorage (persist 1 day or less)
    this.sessionId = localStorage.getItem('chat_widget_session_id') || null;

    this.init();
  }

  init() {
    console.log('🚀 Chat Widget - Initializing...');
    this.createWidget();
    this.bindEvents();
    this.showNotificationBadge();
    
    // Debug visibility
    setTimeout(() => {
      const widgetRect = this.widget.getBoundingClientRect();
      const buttonRect = this.button.getBoundingClientRect();
      const computedStyle = window.getComputedStyle(this.widget);
      const buttonStyle = window.getComputedStyle(this.button);
      
      const isVisible = this.widget.offsetWidth > 0 && this.widget.offsetHeight > 0;
      const isInViewport = widgetRect.right > 0 && widgetRect.bottom > 0 && 
                          widgetRect.left < window.innerWidth && widgetRect.top < window.innerHeight;
      
      console.log('🔍 Chat Widget - Visibility Analysis:', {
        visible: isVisible,
        inViewport: isInViewport,
        widgetRect: widgetRect,
        buttonRect: buttonRect,
        zIndex: computedStyle.zIndex,
        buttonColor: buttonStyle.backgroundColor,
        pageBackground: window.getComputedStyle(document.body).backgroundColor
      });
      
      // Add debug class if query param exists
      if (window.location.search.includes('debug-chat')) {
        this.widget.classList.add('debug-mode');
        console.log('🚨 Chat Widget - DEBUG MODE ENABLED (red pulsing widget)');
      }
      
      if (!isVisible || !isInViewport) {
        console.warn('⚠️ Chat Widget - Widget may not be visible!');
        console.log('💡 Add ?debug-chat to URL to make widget super visible');
      }
    }, 1000);
  }

  createWidget() {
    console.log('🔧 Chat Widget - Creating widget DOM...');
    
    // Create chat widget container
    this.widget = document.createElement('div');
    this.widget.className = 'chat-widget';
    this.widget.innerHTML = this.getWidgetHTML();
    
    console.log('🔧 Chat Widget - Appending to body...');
    document.body.appendChild(this.widget);
    
    // Get references to elements
    this.button = this.widget.querySelector('.chat-widget-button');
    this.window = this.widget.querySelector('.chat-widget-window');
    this.messagesContainer = this.widget.querySelector('.chat-widget-messages');
    this.inputField = this.widget.querySelector('.chat-input-field');
    this.sendButton = this.widget.querySelector('.chat-send-button');
    this.badge = this.widget.querySelector('.chat-widget-badge');
    
    console.log('🔧 Chat Widget - Widget elements:', {
      button: this.button,
      window: this.window,
      widget: this.widget
    });
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
          <div class="chat-widget-info">
            <h6>${this.options.title}</h6>
            <p>${this.options.subtitle}</p>
          </div>
        </div>
        
        <div class="chat-widget-messages">
          ${this.renderMessages()}
        </div>
        
        <div class="chat-widget-input">
          <div class="chat-input-container">
            <input 
              type="text" 
              class="chat-input-field" 
              placeholder="${this.options.placeholder}"
              maxlength="500"
            >
            <button class="chat-send-button" type="button">
              <i class="ti ti-send"></i>
            </button>
          </div>
        </div>
      </div>
    `;
  }

  renderMessages() {
    return this.messages.map(message => this.renderMessage(message)).join('');
  }

  renderMessage(message) {
    const time = this.formatTime(message.time);
    const isUser = message.type === 'user';
    
    return `
      <div class="chat-message ${isUser ? 'user' : ''}">
        <div class="chat-message-avatar">
          <i class="ti ${isUser ? 'ti-user' : 'ti-robot'}"></i>
        </div>
        <div class="chat-message-content">
          <p class="chat-message-text">${this.escapeHtml(message.text)}</p>
          <div class="chat-message-time">${time}</div>
        </div>
      </div>
    `;
  }

  bindEvents() {
    // Toggle chat window
    this.button.addEventListener('click', () => {
      this.toggle();
    });

    // Send message on Enter key
    this.inputField.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Send message on button click
    this.sendButton.addEventListener('click', () => {
      this.sendMessage();
    });

    // Close widget on outside click
    document.addEventListener('click', (e) => {
      if (this.isOpen && !this.widget.contains(e.target)) {
        this.close();
      }
    });

    // Auto-resize input
    this.inputField.addEventListener('input', () => {
      this.updateSendButton();
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
    this.button.classList.add('active');
    this.window.classList.add('show');
    this.hideNotificationBadge();
    this.focusInput();
    this.scrollToBottom();
  }

  close() {
    this.isOpen = false;
    this.button.classList.remove('active');
    this.window.classList.remove('show');
  }

  async sendMessage() {
    const text = this.inputField.value.trim();
    if (!text) return;

    // Add user message
    this.addMessage({
      type: 'user',
      text: text,
      time: new Date()
    });

    // Clear input
    this.inputField.value = '';
    this.updateSendButton();

    // Show typing indicator
    this.showTyping();

    try {
      // Send to API (replace with your actual API)
      const response = await this.sendToAPI(text);
      
      // Hide typing indicator
      this.hideTyping();
      
      // Add bot response
      this.addMessage({
        type: 'bot',
        text: response,
        time: new Date()
      });
    } catch (error) {
      console.error('Chat API Error:', error);
      this.hideTyping();
      this.addMessage({
        type: 'bot',
        text: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.',
        time: new Date()
      });
    }
  }

  async sendToAPI(message) {
    // Get auth token if available
    const token = localStorage.getItem('access_token');

    // Get current user metadata from auth.js functions
    let userData = {
      user_id: 0,
      user_name: 'Guest',
      user_email: 'guest@example.com',
      user_phone: '',
      user_address: '',
      user_city: '',
      user_state: '',
      user_zip: '',
      user_country: '',
      user_role: 'GUEST'
    };

    // Try to get actual user data if authenticated
    if (token && typeof getCurrentUser === 'function') {
      try {
        const currentUser = await getCurrentUser();
        if (currentUser) {
          userData = {
            user_id: currentUser.id || 0,
            user_name: currentUser.name || currentUser.username || 'User',
            user_email: currentUser.email || '',
            user_phone: currentUser.phone || '',
            user_address: currentUser.address || '',
            user_city: currentUser.city || '',
            user_state: currentUser.state || '',
            user_zip: currentUser.zip || '',
            user_country: currentUser.country || '',
            user_role: currentUser.role || 'USER'
          };
        }
      } catch (error) {
        console.warn('Failed to get user metadata:', error);
        // Continue with guest data if user fetch fails
      }
    }

    // Build ChatRequest payload with real user metadata
    const chatRequest = {
      ...userData,
      session_id: this.sessionId,
      message: message,
      timestamp: new Date().toISOString(),
      page_url: window.location.href,
      page_title: document.title
    };

    const response = await fetch(this.options.apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: JSON.stringify(chatRequest)
    });

    if (!response.ok) {
      throw new Error('API request failed');
    }

    const data = await response.json();

    // Persist returned session_id (from ChatResponse) for future requests
    if (data.session_id) {
      this.sessionId = data.session_id;
      localStorage.setItem('chat_widget_session_id', data.session_id);
    }

    // Handle array response format: [{"output": "message"}]
    if (Array.isArray(data) && data.length > 0 && data[0].output) {
      return data[0].output;
    }

    // Handle direct response formats for backward compatibility
    return data.response || data.message || 'Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất có thể.';
  }

  addMessage(message) {
    this.messages.push(message);
    const messageElement = this.renderMessage(message);
    this.messagesContainer.insertAdjacentHTML('beforeend', messageElement);
    this.scrollToBottom();
  }

  showTyping() {
    if (this.isTyping) return;
    
    this.isTyping = true;
    const typingHTML = `
      <div class="chat-message typing-indicator">
        <div class="chat-message-avatar">
          <i class="ti ti-robot"></i>
        </div>
        <div class="chat-message-content">
          <div class="chat-typing">
            <div class="chat-typing-dot"></div>
            <div class="chat-typing-dot"></div>
            <div class="chat-typing-dot"></div>
          </div>
        </div>
      </div>
    `;
    this.messagesContainer.insertAdjacentHTML('beforeend', typingHTML);
    this.scrollToBottom();
  }

  hideTyping() {
    if (!this.isTyping) return;
    
    this.isTyping = false;
    const typingElement = this.messagesContainer.querySelector('.typing-indicator');
    if (typingElement) {
      typingElement.remove();
    }
  }

  showNotificationBadge() {
    setTimeout(() => {
      this.badge.classList.add('show');
    }, 2000);
  }

  hideNotificationBadge() {
    this.badge.classList.remove('show');
  }

  updateSendButton() {
    const hasText = this.inputField.value.trim().length > 0;
    this.sendButton.disabled = !hasText;
  }

  focusInput() {
    setTimeout(() => {
      this.inputField.focus();
    }, 300);
  }

  scrollToBottom() {
    setTimeout(() => {
      this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }, 100);
  }

  formatTime(date) {
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Public methods
  addCustomMessage(text, type = 'bot') {
    this.addMessage({
      type: type,
      text: text,
      time: new Date()
    });
  }

  showBadge(count = '') {
    this.badge.textContent = count;
    this.badge.classList.add('show');
  }

  hideBadge() {
    this.badge.classList.remove('show');
  }
  
  // Debug helper methods
  makeSuperVisible() {
    this.widget.classList.add('debug-mode');
    console.log('🚨 Chat widget is now RED and PULSING for visibility testing');
  }
  
  makeNormal() {
    this.widget.classList.remove('debug-mode');
    console.log('✅ Chat widget back to normal appearance');
  }
  
  checkVisibility() {
    const rect = this.widget.getBoundingClientRect();
    const style = window.getComputedStyle(this.widget);
    const bodyStyle = window.getComputedStyle(document.body);
    
    console.table({
      'Widget Position': `${rect.right}px from left, ${rect.bottom}px from top`,
      'Widget Size': `${rect.width}x${rect.height}`,
      'Z-Index': style.zIndex,
      'Is Visible': rect.width > 0 && rect.height > 0,
      'In Viewport': rect.right > 0 && rect.left < window.innerWidth,
      'Page Background': bodyStyle.backgroundColor
    });
    
    return rect;
  }
}

// Auto-initialize when DOM is ready
function autoInitChatWidget() {
  // Only initialize if not on login/register pages
  const currentPath = window.location.pathname;
  const isAuthPage = currentPath.includes('login') ||
                     currentPath.includes('register') ||
                     currentPath.includes('forgot-password') ||
                     currentPath.includes('reset-password') ||
                     currentPath.includes('code-verification') ||
                     currentPath.includes('landing.html') ||
                     currentPath.includes('error-') ||
                     currentPath.includes('coming-soon') ||
                     currentPath.includes('under-construction');

  console.log('🔍 Chat Widget - Current path:', currentPath);
  console.log('🔍 Chat Widget - Is auth page:', isAuthPage);

  if (!isAuthPage) {
    console.log('✅ Chat Widget - Initializing...');
    window.chatWidget = new ChatWidget({
      apiUrl: 'https://aimarketingvn.com/webhook/chat'
    });
    console.log('✅ Chat Widget - Widget created:', window.chatWidget);
  } else {
    console.log('❌ Chat Widget - Skipped (auth page)');
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', autoInitChatWidget);
} else {
  // DOM already loaded, initialize immediately
  autoInitChatWidget();
}

// Global debugging helpers
window.debugChatWidget = function() {
  if (window.chatWidget) {
    console.log('🔧 Chat Widget Debug Tools:');
    console.log('- chatWidget.makeSuperVisible() - Make widget red and pulsing');
    console.log('- chatWidget.makeNormal() - Return to normal appearance');
    console.log('- chatWidget.checkVisibility() - Show position/visibility info');
    console.log('- chatWidget.open() - Force open chat window');
    return window.chatWidget.checkVisibility();
  } else {
    console.error('❌ Chat widget not found! Check if it initialized properly.');
  }
}; 