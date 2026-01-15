document.addEventListener('DOMContentLoaded', () => {
  
  const container = document.getElementById('container');
  const registerBtn = document.getElementById('register');
  const loginBtn = document.getElementById('login');

  if (container && registerBtn && loginBtn) {
    
    registerBtn.addEventListener('click', () => {
      container.classList.add('active');
    });

    loginBtn.addEventListener('click', () => {
      container.classList.remove('active');
    });

  } else {
    console.error("Error: Could not find one or more required elements (container, register, or login).");
  }

  document.body.classList.remove('fade');
  
});