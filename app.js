// --- Reusable function to handle fetch requests ---
async function handleAuthRequest(endpoint, formData, messageElement) {
  try {
    const response = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
      method: 'POST',
      body: formData,
    });

    const result = await response.json(); // Get JSON result

    if (response.ok) {
      
      // Check if this was an authentication attempt AND if it failed
      if (endpoint === 'authenticate' && result.authenticated === false) {
        messageElement.textContent = 'Access Denied. Gait does not match.';
        messageElement.style.color = 'red';
      
      } else {
        // This block now handles SUCCESSFUL authentication or registration
        const successMessage = endpoint === 'register' ? `User ${result.user_id} registered!` : `Success! Welcome, ${result.user_id}.`;
        messageElement.textContent = successMessage;
        messageElement.style.color = 'green';
      }

    } else {
      const errorMsg = result.details || result.error || 'An unknown error occurred.';
      messageElement.textContent = `Error: ${errorMsg}`;
      messageElement.style.color = 'red';
    }
  } catch (error) {
    console.error(`Error during /${endpoint} fetch:`, error);
    messageElement.textContent = 'Server error. Could not connect.';
    messageElement.style.color = 'red';
  }
}

// --- Add all event listeners after the DOM content is loaded ---
document.addEventListener('DOMContentLoaded', () => {
    
  // --- START OF FIX ---
  // This line makes the content on index.html visible
  if (document.body.classList.contains('fade')) {
      document.body.classList.remove('fade');
  }
  // --- END OF FIX ---

  // --- Navigation from index.html ---
  const getStartedButton = document.getElementById('get-started');
  if (getStartedButton) {
    getStartedButton.addEventListener('click', () => {
      // This will navigate from index.html to your new auth.html page
      window.location.href = 'auth.html';
    });
  }

  // --- Animation buttons (for auth.html) ---
  const container = document.getElementById('container');
  const registerBtn = document.getElementById('register');
  const loginBtn = document.getElementById('login');

  if (container && registerBtn && loginBtn) {
    registerBtn.addEventListener('click', () => container.classList.add('active'));
    loginBtn.addEventListener('click', () => container.classList.remove('active'));
  }

  // --- Sign In Form (for auth.html) ---
  const signInForm = document.getElementById('signin-form');
  const signInVideoInput = document.getElementById('signin-video-input');
  const signInMessage = document.getElementById('signin-message');

  if (signInForm) {
    signInForm.addEventListener('submit', async (event) => {
      event.preventDefault(); 
      const file = signInVideoInput.files[0];
      if (!file) {
        signInMessage.textContent = 'Please select a video file.';
        signInMessage.style.color = 'red';
        return;
      }
      signInMessage.textContent = 'Authenticating...';
      signInMessage.style.color = '#333';
      const formData = new FormData();
      formData.append('gait_video', file);
      await handleAuthRequest('authenticate', formData, signInMessage);
      signInVideoInput.value = ''; // Reset input
    });
  }

  // --- Sign Up Form (for auth.html) ---
  const signUpForm = document.getElementById('signup-form');
  const signUpVideoInput = document.getElementById('signup-video-input');
  const signUpMessage = document.getElementById('signup-message');
  const signUpNameInput = document.getElementById('signup-name');

  if (signUpForm) {
    signUpForm.addEventListener('submit', async (event) => {
      event.preventDefault(); 
      const file = signUpVideoInput.files[0];
      const name = signUpNameInput.value;
      if (!file || !name) {
        signUpMessage.textContent = 'Please provide a name and a video file.';
        signUpMessage.style.color = 'red';
        return;
      }
      signUpMessage.textContent = 'Registering...';
      signUpMessage.style.color = '#333';
      const formData = new FormData();
      formData.append('gait_video', file);
      formData.append('user_id', name);
      await handleAuthRequest('register', formData, signUpMessage);
      signUpVideoInput.value = ''; // Reset input
      signUpNameInput.value = ''; // Reset name
    });
  }

});