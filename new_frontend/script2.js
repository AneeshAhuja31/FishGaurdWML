document.getElementById('scrollButton')?.addEventListener('click', function() {
    let target = document.getElementById('workflow1start');
    if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
    }
});

async function getUserId(){
    return 'user_123456789';
}

async function updateClassification(url, classification) {
    try {
      const userId = await getUserId();
      
      const response = await fetch("http://localhost:8000/update-classification", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          classification: classification,
          user_id: userId
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error updating classification: ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log('URL classification updated successfully:', result);
      
      showNotification(`URL classified as ${classification} successfully!`, 'success');
      return result;
    } catch (error) {
      console.error('Error in updateClassification function:', error);
      showNotification('Failed to update classification: ' + error.message, 'error');
      throw error;
    }
}

function showNotification(message, type = 'info') {
  let notificationContainer = document.getElementById('notification-container');
  if (!notificationContainer) {
    notificationContainer = document.createElement('div');
    notificationContainer.id = 'notification-container';
    notificationContainer.style.position = 'fixed';
    notificationContainer.style.bottom = '20px';
    notificationContainer.style.right = '20px';
    notificationContainer.style.zIndex = '1000';
    document.body.appendChild(notificationContainer);
  }
  
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.innerHTML = message;
  
  // Style the notification
  notification.style.padding = '12px 20px';
  notification.style.marginBottom = '10px';
  notification.style.borderRadius = '4px';
  notification.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
  notification.style.fontFamily = 'Inter, Arial, sans-serif';
  notification.style.opacity = '1';
  notification.style.transition = 'opacity 0.5s ease';
  
  if (type === 'success') {
    notification.style.backgroundColor = '#4CAF50';
    notification.style.color = 'white';
  } else if (type === 'error') {
    notification.style.backgroundColor = '#F44336';
    notification.style.color = 'white';
  } else if (type === 'warning') {
    notification.style.backgroundColor = '#FFC107';
    notification.style.color = 'black';
  } else {
    notification.style.backgroundColor = '#2196F3';
    notification.style.color = 'white';
  }
  
  notificationContainer.appendChild(notification);
  
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      if (notificationContainer.contains(notification)) {
        notificationContainer.removeChild(notification);
      }
    }, 500);
  }, 3000);
}

// Use this function to set up event listeners after DOM is fully loaded
function setupButtonListeners() {
  console.log('Setting up button event listeners');
  
  const urlInput = document.getElementById('url-input');
  const legitButton = document.getElementById('legitimate-button');
  const fraudButton = document.getElementById('fraudulent-button');
  const unrelatedButton = document.getElementById('unrelated-button');
  
  if (!urlInput) {
    console.error('URL input element not found');
    return;
  }
  
  if (legitButton) {
    console.log('Attaching event listener to legitimate button');
    legitButton.addEventListener('click', async function(e) {
      e.preventDefault();
      console.log('Legitimate button clicked');
      
      const url = urlInput.value.trim();
      if (!url) {
        showNotification('Please enter a valid URL', 'error');
        return;
      }
      
      try {
        await updateClassification(url, "Legitimate");
        urlInput.value = '';
      } catch (error) {
        // Error handled in updateClassification function
      }
    });
  } else {
    console.error('Legitimate button not found');
  }
  
  if (fraudButton) {
    console.log('Attaching event listener to fraudulent button');
    fraudButton.addEventListener('click', async function(e) {
      e.preventDefault();
      console.log('Fraudulent button clicked');
      
      const url = urlInput.value.trim();
      if (!url) {
        showNotification('Please enter a valid URL', 'error');
        return;
      }
      
      try {
        await updateClassification(url, "Fraudulent");
        urlInput.value = '';
      } catch (error) {
        // Error handled in updateClassification function
      }
    });
  } else {
    console.error('Fraudulent button not found');
  }
  
  if (unrelatedButton) {
    console.log('Attaching event listener to unrelated button');
    unrelatedButton.addEventListener('click', async function(e) {
      e.preventDefault();
      console.log('Unrelated button clicked');
      
      const url = urlInput.value.trim();
      if (!url) {
        showNotification('Please enter a valid URL', 'error');
        return;
      }
      
      try {
        await updateClassification(url, "Unrelated");
        urlInput.value = '';
      } catch (error) {
        // Error handled in updateClassification function
      }
    });
  } else {
    console.error('Unrelated button not found');
  }
}

// Call the setup function when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM content loaded');
  
  // Try immediately
  setupButtonListeners();
  
  // Also try with a slight delay to ensure everything is rendered
  setTimeout(setupButtonListeners, 300);
  
  // Log user ID for debugging
  getUserId().then(userId => {
    console.log('[FishGuard] Using user ID:', userId);
  });
});

// Add a window load event as a backup
window.addEventListener('load', function() {
  console.log('Window fully loaded, setting up buttons again');
  setupButtonListeners();
});