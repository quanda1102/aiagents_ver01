/**
 * Chat Widget Initialization Script
 * Include this script to automatically add the chat widget to any page
 */

(function() {
  'use strict';
  
  // Function to load CSS dynamically
  function loadCSS(href) {
    return new Promise((resolve, reject) => {
      // Check if CSS is already loaded
      if (document.querySelector(`link[href*="${href}"]`)) {
        resolve();
        return;
      }
      
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      link.onload = resolve;
      link.onerror = reject;
      document.head.appendChild(link);
    });
  }
  
  // Function to load JavaScript dynamically
  function loadJS(src) {
    return new Promise((resolve, reject) => {
      // Check if script is already loaded
      if (document.querySelector(`script[src*="${src}"]`)) {
        resolve();
        return;
      }
      
      const script = document.createElement('script');
      script.src = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }
  
  // Get the current script path to determine relative paths
  function getCurrentScriptPath() {
    const scripts = document.getElementsByTagName('script');
    const currentScript = scripts[scripts.length - 1];
    const scriptPath = currentScript.src;
    return scriptPath.substring(0, scriptPath.lastIndexOf('/'));
  }
  
  // Initialize chat widget
  async function initChatWidget() {
    try {
      const basePath = getCurrentScriptPath();
      
      // Load CSS and JS files
      await Promise.all([
        loadCSS(`assets/css/chat-widget.css`),
        loadJS(`assets/js/chat-widget.js`)
      ]);
      
      console.log('✅ Chat widget loaded successfully');
    } catch (error) {
      console.error('❌ Failed to load chat widget:', error);
    }
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatWidget);
  } else {
    initChatWidget();
  }
})(); 