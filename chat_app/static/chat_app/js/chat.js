document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    
    // Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Helper function to format time
    function formatTime(date) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    
    // Add a new message to the chat
    function addMessage(content, type, source = null) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${type}-message`);
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.textContent = content;
        
        const messageTime = document.createElement('div');
        messageTime.classList.add('message-time');
        messageTime.textContent = formatTime(new Date());
        
        messageDiv.appendChild(messageContent);
        
        if (source) {
            const messageSource = document.createElement('div');
            messageSource.classList.add('message-source');
            messageSource.textContent = `Source: ${source}`;
            messageDiv.appendChild(messageSource);
        }
        
        messageDiv.appendChild(messageTime);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Add loading indicator
    function addLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('message', 'bot-message', 'loading-message');
        
        const loadingContent = document.createElement('div');
        loadingContent.classList.add('message-content');
        loadingContent.innerHTML = 'Thinking<span class="loading-dots"></span>';
        
        loadingDiv.appendChild(loadingContent);
        chatMessages.appendChild(loadingDiv);
        
        // Scroll to the bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return loadingDiv;
    }
    
    // Remove loading indicator
    function removeLoadingIndicator(element) {
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }
    
    // Send message to the server
    async function sendMessage(message) {
        const csrftoken = getCookie('csrftoken');
        
        try {
            const response = await fetch('/chat/api/message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error:', error);
            return {
                response: 'Sorry, there was an error processing your request.',
                source: null
            };
        }
    }
    
    // Handle form submission
    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        userInput.value = '';
        
        // Show loading indicator
        const loadingIndicator = addLoadingIndicator();
        
        // Get bot response
        const responseData = await sendMessage(message);
        
        // Remove loading indicator
        removeLoadingIndicator(loadingIndicator);
        
        // Add bot response to chat
        addMessage(responseData.response, 'bot', responseData.source);
    });
    
    // Initial focus on input
    userInput.focus();

    // Index current page (optional)
    async function indexCurrentPage() {
        const csrftoken = getCookie('csrftoken');
        
        try {
            const response = await fetch('/chat/api/index/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ url: window.location.href })
            });
            
            if (!response.ok) {
                console.warn('Failed to index current page');
            }
        } catch (error) {
            console.error('Error indexing page:', error);
        }
    }
    
    // Uncomment this to automatically index the current page
    // indexCurrentPage();

    // Helper function to index specific pages
    window.indexPage = async function(url) {
        const csrftoken = getCookie('csrftoken');
        
        try {
            const response = await fetch('/chat/api/index/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ url: url })
            });
            
            if (!response.ok) {
                return false;
            }
            
            return true;
        } catch (error) {
            console.error('Error indexing page:', error);
            return false;
        }
    };
});