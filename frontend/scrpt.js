// Get references to DOM elements
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
let loadingMessageElement = null; // To keep track of loading/sending messages

// Function to display a message in the chat messages area
function displayMessage(message, type = 'normal') {
  const messageElement = document.createElement('div');
  messageElement.textContent = message;
  if (type === 'error') {
    messageElement.style.color = 'red';
  } else if (type === 'info') {
    messageElement.style.fontStyle = 'italic';
  }
  chatMessages.appendChild(messageElement);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return messageElement; // Return the element if we need to remove it later
}

// Function to show/hide a temporary loading/info message
function showTemporaryMessage(messageText, type = 'info') {
  removeTemporaryMessage(); // Remove any existing temporary message
  loadingMessageElement = displayMessage(messageText, type);
}

function removeTemporaryMessage() {
  if (loadingMessageElement && loadingMessageElement.parentNode === chatMessages) {
    chatMessages.removeChild(loadingMessageElement);
  }
  loadingMessageElement = null;
}

// Function to send a message to the backend
async function sendMessageToBackend(message) {
  sendButton.disabled = true;
  messageInput.disabled = true;
  showTemporaryMessage('Sending...', 'info');

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: message }),
    });
    removeTemporaryMessage(); // Remove "Sending..."
    if (!response.ok) {
      // Try to get error message from backend response body
      let errorData = null;
      try {
        errorData = await response.json();
      } catch (e) {
        // Ignore if response is not JSON
      }
      const errorMsg = errorData && errorData.detail ? errorData.detail : `HTTP error! status: ${response.status}`;
      throw new Error(errorMsg);
    }
    // Backend is expected to echo the message or the frontend calls fetchMessages again.
    // For now, we are displaying the user's message directly, which is fine.
    // However, to ensure the displayed message matches what's on the server (e.g. with timestamps or user name),
    // it's often better to fetch all messages again or have the backend return the created message object.
    // For this iteration, displaying the user's message is kept for simplicity.
    displayMessage(`You: ${message}`);
    // Alternative: call fetchMessages() to refresh the chat with the new message from server.
    // await fetchMessages();
  } catch (error) {
    removeTemporaryMessage(); // Remove "Sending..." if it's still there on error
    console.error('Error sending message to backend:', error);
    displayMessage(`Error sending message: ${error.message || 'Unknown error'}. Please try again.`, 'error');
  } finally {
    sendButton.disabled = false;
    messageInput.disabled = false;
    messageInput.focus(); // Put focus back to input
  }
}

// Function to fetch messages from the backend
async function fetchMessages() {
  showTemporaryMessage('Loading messages...', 'info');
  sendButton.disabled = true; // Disable send while loading initial messages

  try {
    const response = await fetch('/messages');
    removeTemporaryMessage(); // Remove "Loading messages..."
    if (!response.ok) {
      // Try to get error message from backend response body
      let errorData = null;
      try {
        errorData = await response.json();
      } catch (e) {
        // Ignore if response is not JSON
      }
      const errorMsg = errorData && errorData.detail ? errorData.detail : `HTTP error! status: ${response.status}`;
      throw new Error(errorMsg);
    }
    const messages = await response.json();
    chatMessages.innerHTML = ''; // Clear existing messages (including any previous error/loading messages)
    messages.forEach(msg => {
      if (typeof msg === 'object' && msg.text) {
        displayMessage(`${msg.user || 'Anonymous'}: ${msg.text}`);
      } else {
        // Fallback for simple string messages, though backend sends objects
        displayMessage(String(msg));
      }
    });
  } catch (error) {
    removeTemporaryMessage(); // Remove "Loading messages..." if it's still there on error
    // If chatMessages was cleared, we might want to ensure the error is visible.
    if (chatMessages.innerHTML === '') {
        displayMessage(`Error fetching messages: ${error.message || 'Unknown error'}. Please try refreshing.`, 'error');
    } else { // If there were old messages, append error at the end
        displayMessage(`Error fetching messages: ${error.message || 'Unknown error'}. Please try refreshing.`, 'error');
    }
    console.error('Error fetching messages:', error);
  } finally {
    sendButton.disabled = false; // Re-enable send button
  }
}

// Event listener for the send button
sendButton.addEventListener('click', () => {
  if (sendButton.disabled) return; // Prevent action if button is disabled

  const message = messageInput.value.trim();
  if (message !== '') {
    sendMessageToBackend(message);
    messageInput.value = ''; // Clear the input field after initiating send
  }
});

// Call fetchMessages when the page loads
window.addEventListener('load', fetchMessages);
