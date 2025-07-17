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
  
  // Calculate correct relative path to assets based on current page location
  function getAssetsPath() {
    const currentPath = window.location.pathname;
    const depth = (currentPath.match(/\//g) || []).length - 1;
    
    // Calculate how many "../" we need to get back to root
    if (currentPath.includes('/pages/exercises/')) {
      return '../../assets/';
    } else if (currentPath.includes('/pages/')) {
      return '../assets/';
    } else if (currentPath.includes('/dashboard/')) {
      return '../assets/';
    } else {
      return 'assets/';
    }
  }

  // Initialize chat widget
  async function initChatWidget() {
    try {
      const assetsPath = getAssetsPath();
      
      // Load CSS and JS files
      await Promise.all([
        loadCSS(`${assetsPath}css/chat-widget.css`),
        loadJS(`${assetsPath}js/chat-widget.js`)
      ]);
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