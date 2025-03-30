document.getElementById('scrollButton').addEventListener('click', function() {
    let target = document.getElementById('workflow1start');
    if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
    }
});
 



//  // Function to get the user ID from Chrome storage (or create one if doesn't exist)
// async function getUserId() {
//   // First try to get from localStorage (for web app)
//   let userId = localStorage.getItem('fishguard_user_id');
  
//   // If not found, try to get from Chrome storage (extension)
//   if (!userId && chrome && chrome.storage) {
//       try {
//           // Try to access chrome.storage (only works in extension context)
//           return new Promise((resolve) => {
//               chrome.storage.local.get(['fishguard_user_id'], (result) => {
//                   if (result && result.fishguard_user_id) {
//                       // Store in localStorage for future use
//                       localStorage.setItem('fishguard_user_id', result.fishguard_user_id);
//                       resolve(result.fishguard_user_id);
//                   } else {
//                       // Create new ID if not found anywhere
//                       const newUserId = 'user_' + Math.random().toString(36).substring(2, 15);
//                       localStorage.setItem('fishguard_user_id', newUserId);
                      
//                       // Store in Chrome storage if possible
//                       if (chrome && chrome.storage) {
//                           chrome.storage.local.set({ 'fishguard_user_id': newUserId });
//                       }
                      
//                       resolve(newUserId);
//                   }
//               });
//           });
//       } catch (e) {
//           console.log('Not in extension context, using localStorage only');
//       }
//   }
  
//   // If still no userId, create a new one
//   if (!userId) {
//       userId = 'user_' + Math.random().toString(36).substring(2, 15);
//       localStorage.setItem('fishguard_user_id', userId);
//   }
  
//   return userId;
// }

// // Function to tag a URL as phishing
// async function tagUrl(url, isPhishing = 1) {
//   try {
//       const userId = await getUserId();
      
//       const response = await fetch("http://localhost:8000/tag-url", {
//           method: 'POST',
//           headers: {
//               'Content-Type': 'application/json',
//           },
//           body: JSON.stringify({
//               url: url,
//               is_phishing: isPhishing,
//               user_id: userId,
//               source: "landing_page"
//           })
//       });
      
//       if (!response.ok) {
//           throw new Error(`Error tagging URL: ${response.statusText}`);
//       }
      
//       const result = await response.json();
//       console.log('URL tagged successfully:', result);
      
//       // Show success message to user
//       showNotification('URL tagged as phishing successfully!', 'success');
      
//       return result;
//   } catch (error) {
//       console.error('Error in tagUrl function:', error);
//       showNotification('Failed to tag URL: ' + error.message, 'error');
//       throw error;
//   }
// }

// // Function to untag a URL
// async function untagUrl(url) {
//   try {
//       const userId = await getUserId();
      
//       const response = await fetch("http://localhost:8000/untag-url", {
//           method: 'POST',
//           headers: {
//               'Content-Type': 'application/json',
//           },
//           body: JSON.stringify({
//               url: url,
//               user_id: userId
//           })
//       });
      
//       if (!response.ok) {
//           throw new Error(`Error untagging URL: ${response.statusText}`);
//       }
      
//       const result = await response.json();
//       console.log('URL untagged successfully:', result);
      
//       // Show success message to user
//       showNotification('URL untagged successfully!', 'success');
      
//       return result;
//   } catch (error) {
//       console.error('Error in untagUrl function:', error);
//       showNotification('Failed to untag URL: ' + error.message, 'error');
//       throw error;
//   }
// }

// // Helper function to display notifications to the user
// function showNotification(message, type = 'info') {
//   // Check if a notification container exists, create one if not
//   let notificationContainer = document.getElementById('notification-container');
//   if (!notificationContainer) {
//       notificationContainer = document.createElement('div');
//       notificationContainer.id = 'notification-container';
//       notificationContainer.style.position = 'fixed';
//       notificationContainer.style.top = '20px';
//       notificationContainer.style.right = '20px';
//       notificationContainer.style.zIndex = '1000';
//       document.body.appendChild(notificationContainer);
//   }
  
//   // Create notification element
//   const notification = document.createElement('div');
//   notification.className = `notification ${type}`;
//   notification.innerHTML = message;
  
//   // Style the notification based on type
//   notification.style.padding = '12px 20px';
//   notification.style.marginBottom = '10px';
//   notification.style.borderRadius = '4px';
//   notification.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
//   notification.style.fontFamily = 'Arial, sans-serif';
  
//   if (type === 'success') {
//       notification.style.backgroundColor = '#4CAF50';
//       notification.style.color = 'white';
//   } else if (type === 'error') {
//       notification.style.backgroundColor = '#F44336';
//       notification.style.color = 'white';
//   } else {
//       notification.style.backgroundColor = '#2196F3';
//       notification.style.color = 'white';
//   }
  
//   // Add to container
//   notificationContainer.appendChild(notification);
  
//   // Remove after 3 seconds
//   setTimeout(() => {
//       notification.style.opacity = '0';
//       notification.style.transition = 'opacity 0.5s ease';
//       setTimeout(() => {
//           notificationContainer.removeChild(notification);
//       }, 500);
//   }, 3000);
// }

// // Add event listeners when the document is loaded
// document.addEventListener('DOMContentLoaded', function() {
//   // Get form elements
//   const urlForm = document.getElementById('url-form');
//   const urlInput = document.getElementById('url-input');
//   const tagButton = document.getElementById('tag-button');
//   const untagButton = document.getElementById('untag-button');
  
//   // Add event listener for the tag button
//   if (tagButton) {
//       tagButton.addEventListener('click', async function(e) {
//           e.preventDefault();
          
//           const url = urlInput.value.trim();
//           if (!url) {
//               showNotification('Please enter a valid URL', 'error');
//               return;
//           }
          
//           try {
//               await tagUrl(url);
//               // Optional: Clear the input after successful tagging
//               urlInput.value = '';
//           } catch (error) {
//               // Error already handled in tagUrl function
//           }
//       });
//   }
  
//   // Add event listener for the untag button
//   if (untagButton) {
//       untagButton.addEventListener('click', async function(e) {
//           e.preventDefault();
          
//           const url = urlInput.value.trim();
//           if (!url) {
//               showNotification('Please enter a valid URL', 'error');
//               return;
//           }
          
//           try {
//               await untagUrl(url);
//               // Optional: Clear the input after successful untagging
//               urlInput.value = '';
//           } catch (error) {
//               // Error already handled in untagUrl function
//           }
//       });
//   }
  
//   // If using a form submit event instead of button clicks
//   if (urlForm) {
//       urlForm.addEventListener('submit', function(e) {
//           e.preventDefault();
//           // Default action can be to tag the URL
//           tagUrl(urlInput.value.trim());
//       });
//   }
  
//   // Display user ID (optional, for debugging)
//   getUserId().then(userId => {
//       console.log('[FishGuard] Using user ID:', userId);
//   });
// });














// async function getUserId() {
//     // First try to get from localStorage
//     let userId = localStorage.getItem('fishguard_user_id');
    
//     // If not found, try Chrome storage (for extension)
//     if (!userId && typeof chrome !== 'undefined' && chrome.storage) {
//       try {
//         return new Promise((resolve) => {
//           chrome.storage.local.get(['fishguard_user_id'], (result) => {
//             if (result && result.fishguard_user_id) {
//               localStorage.setItem('fishguard_user_id', result.fishguard_user_id);
//               resolve(result.fishguard_user_id);
//             } else {
//               // Create new ID
//               const newUserId = 'user_' + Math.random().toString(36).substring(2, 15);
//               localStorage.setItem('fishguard_user_id', newUserId);
              
//               // Store in Chrome storage
//               chrome.storage.local.set({ 'fishguard_user_id': newUserId });
//               resolve(newUserId);
//             }
//           });
//         });
//       } catch (e) {
//         console.log('Not in extension context, using localStorage only');
//       }
//     }
    
//     // Create new ID if still none
//     if (!userId) {
//       userId = 'user_' + Math.random().toString(36).substring(2, 15);
//       localStorage.setItem('fishguard_user_id', userId);
//     }
    
//     return userId;
//   }
  async function getUserId(){
    return 'user_123456789';
  }
  
  // // Function to tag a URL as phishing
  // async function tagUrl(url, isPhishing = 1) {
  //   try {
  //     const userId = await getUserId();
      
  //     const response = await fetch("http://localhost:8000/tag-url", {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify({
  //         url: url,
  //         is_phishing: isPhishing,
  //         user_id: userId,
  //         source: "landing_page"
  //       })
  //     });
      
  //     if (!response.ok) {
  //       throw new Error(`Error tagging URL: ${response.statusText}`);
  //     }
      
  //     const result = await response.json();
  //     console.log('URL tagged successfully:', result);
      
  //     showNotification('URL tagged as phishing successfully!', 'success');
  //     return result;
  //   } catch (error) {
  //     console.error('Error in tagUrl function:', error);
  //     showNotification('Failed to tag URL: ' + error.message, 'error');
  //     throw error;
  //   }
  // }

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
  
  
  // // Function to untag a URL
  // async function untagUrl(url) {
  //   try {
  //     const userId = await getUserId();
      
  //     const response = await fetch("http://localhost:8000/untag-url", {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json',
  //       },
  //       body: JSON.stringify({
  //         url: url,
  //         user_id: userId
  //       })
  //     });
      
  //     if (!response.ok) {
  //       throw new Error(`Error untagging URL: ${response.statusText}`);
  //     }
      
  //     const result = await response.json();
  //     console.log('URL untagged successfully:', result);
      
  //     showNotification('URL untagged successfully!', 'success');
  //     return result;
  //   } catch (error) {
  //     console.error('Error in untagUrl function:', error);
  //     showNotification('Failed to untag URL: ' + error.message, 'error');
  //     throw error;
  //   }
  // }
  
  // // Function to display notifications
  // function showNotification(message, type = 'info') {
  //   let notificationContainer = document.getElementById('notification-container');
  //   if (!notificationContainer) {
  //     notificationContainer = document.createElement('div');
  //     notificationContainer.id = 'notification-container';
  //     document.body.appendChild(notificationContainer);
  //   }
    
  //   const notification = document.createElement('div');
  //   notification.className = `notification ${type}`;
  //   notification.innerHTML = message;
    
  //   notificationContainer.appendChild(notification);
    
  //   setTimeout(() => {
  //     notification.style.opacity = '0';
  //     setTimeout(() => {
  //       notificationContainer.removeChild(notification);
  //     }, 500);
  //   }, 3000);
  // }
  
// Function to display notifications
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


  // // Initialize event listeners when DOM is loaded
  // document.addEventListener('DOMContentLoaded', function() {
  //   console.log('DOM content loaded, setting up event listeners');
    
  //   const urlInput = document.getElementById('url-input');
  //   const tagButton = document.getElementById('tag-button');
  //   const untagButton = document.getElementById('untag-button');
    
  //   // Debug logging to check if elements exist
  //   console.log('URL Input element:', urlInput);
  //   console.log('Tag Button element:', tagButton);
  //   console.log('Untag Button element:', untagButton);
    
  //   // Event listener for tag button
  //   if (tagButton) {
  //     tagButton.addEventListener('click', async function(e) {
  //       e.preventDefault();
  //       console.log('Tag button clicked');
        
  //       const url = urlInput.value.trim();
  //       if (!url) {
  //         showNotification('Please enter a valid URL', 'error');
  //         return;
  //       }
        
  //       try {
  //         await tagUrl(url);
  //         urlInput.value = '';
  //       } catch (error) {
  //         // Error handled in tagUrl function
  //       }
  //     });
  //   } else {
  //     console.error('Tag button not found in the DOM');
  //   }
    
  //   // Event listener for untag button
  //   if (untagButton) {
  //     untagButton.addEventListener('click', async function(e) {
  //       e.preventDefault();
  //       console.log('Untag button clicked');
        
  //       const url = urlInput.value.trim();
  //       if (!url) {
  //         showNotification('Please enter a valid URL', 'error');
  //         return;
  //       }
        
  //       try {
  //         await untagUrl(url);
  //         urlInput.value = '';
  //       } catch (error) {
  //         // Error handled in untagUrl function
  //       }
  //     });
  //   } else {
  //     console.error('Untag button not found in the DOM');
  //   }
    
  //   // Log user ID for debugging
  //   getUserId().then(userId => {
  //     console.log('[FishGuard] Using user ID:', userId);
  //   });
  // });
  
  // // Add this as a fallback in case DOMContentLoaded already fired
  // if (document.readyState === 'loading') {
  //   console.log('Document still loading, will use DOMContentLoaded');
  // } else {
  //   console.log('Document already loaded, setting up event listeners immediately');
  //   // Run the same setup immediately
  //   const urlInput = document.getElementById('url-input');
  //   const tagButton = document.getElementById('tag-button');
  //   const untagButton = document.getElementById('untag-button');
    
  //   if (tagButton) {
  //     tagButton.addEventListener('click', async function(e) {
  //       e.preventDefault();
  //       const url = urlInput.value.trim();
  //       if (!url) {
  //         showNotification('Please enter a valid URL', 'error');
  //         return;
  //       }
  //       try {
  //         await tagUrl(url);
  //         urlInput.value = '';
  //       } catch (error) {
  //         // Error handled in tagUrl function
  //       }
  //     });
  //   }
    
  //   if (untagButton) {
  //     untagButton.addEventListener('click', async function(e) {
  //       e.preventDefault();
  //       const url = urlInput.value.trim();
  //       if (!url) {
  //         showNotification('Please enter a valid URL', 'error');
  //         return;
  //       }
  //       try {
  //         await untagUrl(url);
  //         urlInput.value = '';
  //       } catch (error) {
  //         // Error handled in untagUrl function
  //       }
  //     });
  //   }
  // }

  // Initialize event listeners when DOM is loaded
// document.addEventListener('DOMContentLoaded', function() {
//   console.log('DOM content loaded, setting up event listeners for URL classification');
  
//   const urlInput = document.getElementById('url-input');
//   const tagButton = document.getElementById('tag-button');
//   const checkButton = document.querySelector('.check-btn');
//   const crossButton = document.querySelector('.cross-btn');
  
//   // Update ID selectors in your HTML to match these IDs
//   const legitButton = tagButton; // Green button for Legitimate
//   const fraudButton = crossButton; // Red button for Fraudulent
//   const unrelatedButton = checkButton; // Yellow button for Unrelated
  
//   // Debug logging
//   console.log('URL Input element:', urlInput);
//   console.log('Legitimate Button element:', legitButton);
//   console.log('Fraudulent Button element:', fraudButton);
//   console.log('Unrelated Button element:', unrelatedButton);
  
//   // Event listener for Legitimate button (green)
//   if (legitButton) {
//     legitButton.addEventListener('click', async function(e) {
//       e.preventDefault();
//       console.log('Legitimate button clicked');
      
//       const url = urlInput.value.trim();
//       if (!url) {
//         showNotification('Please enter a valid URL', 'error');
//         return;
//       }
      
//       try {
//         await updateClassification(url, "Legitimate");
//         urlInput.value = '';
//       } catch (error) {
//         // Error handled in updateClassification function
//       }
//     });
//   } else {
//     console.error('Legitimate button not found in the DOM');
//   }
  
//   // Event listener for Fraudulent button (red)
//   if (fraudButton) {
//     fraudButton.addEventListener('click', async function(e) {
//       e.preventDefault();
//       console.log('Fraudulent button clicked');
      
//       const url = urlInput.value.trim();
//       if (!url) {
//         showNotification('Please enter a valid URL', 'error');
//         return;
//       }
      
//       try {
//         await updateClassification(url, "Fraudulent");
//         urlInput.value = '';
//       } catch (error) {
//         // Error handled in updateClassification function
//       }
//     });
//   } else {
//     console.error('Fraudulent button not found in the DOM');
//   }
  
//   // Event listener for Unrelated button (yellow)
//   if (unrelatedButton) {
//     unrelatedButton.addEventListener('click', async function(e) {
//       e.preventDefault();
//       console.log('Unrelated button clicked');
      
//       const url = urlInput.value.trim();
//       if (!url) {
//         showNotification('Please enter a valid URL', 'error');
//         return;
//       }
      
//       try {
//         await updateClassification(url, "Unrelated");
//         urlInput.value = '';
//       } catch (error) {
//         // Error handled in updateClassification function
//       }
//     });
//   } else {
//     console.error('Unrelated button not found in the DOM');
//   }
  
//   // Log user ID for debugging
//   getUserId().then(userId => {
//     console.log('[FishGuard] Using user ID:', userId);
//   });
// });

// // Add this as a fallback in case DOMContentLoaded already fired
// if (document.readyState === 'loading') {
//   console.log('Document still loading, will use DOMContentLoaded');
// } else {
//   console.log('Document already loaded, setting up event listeners immediately');
  
//   const urlInput = document.getElementById('url-input');
//   const tagButton = document.getElementById('tag-button');
//   const checkButton = document.querySelector('.check-btn');
//   const crossButton = document.querySelector('.cross-btn');
  
//   const legitButton = tagButton; // Green button for Legitimate
//   const fraudButton = crossButton; // Red button for Fraudulent
//   const unrelatedButton = checkButton; // Yellow button for Unrelated
  
//   if (legitButton) {
//     legitButton.addEventListener('click', async function(e) {
//       e.preventDefault();
//       const url = urlInput.value.trim();
//       if (!url) {
//         showNotification('Please enter a valid URL', 'error');
//         return;
//       }
//       try {
//         await updateClassification(url, "Legitimate");
//         urlInput.value = '';
//       } catch (error) {
//         // Error handled in updateClassification function
//       }
//     });
//   }
  
//   if (fraudButton) {
//     fraudButton.addEventListener('click', async function(e) {
//       e.preventDefault();
//       const url = urlInput.value.trim();
//       if (!url) {
//         showNotification('Please enter a valid URL', 'error');
//         return;
//       }
//       try {
//         await updateClassification(url, "Fraudulent");
//         urlInput.value = '';
//       } catch (error) {
//         // Error handled in updateClassification function
//       }
//     });
//   }
  
//   if (unrelatedButton) {
//     unrelatedButton.addEventListener('click', async function(e) {
//       e.preventDefault();
//       const url = urlInput.value.trim();
//       if (!url) {
//         showNotification('Please enter a valid URL', 'error');
//         return;
//       }
//       try {
//         await updateClassification(url, "Unrelated");
//         urlInput.value = '';
//       } catch (error) {
//         // Error handled in updateClassification function
//       }
//     });
//   }
// }

// // Clear out the old event listeners and rewrite the URL validation section
// document.addEventListener('DOMContentLoaded', function() {
//   console.log('DOM content loaded, setting up event listeners for URL classification');
  
//   const urlInput = document.getElementById('url-input');
//   const legitButton = document.getElementById('legitimate-button');
//   const fraudButton = document.getElementById('fraudulent-button');
//   const unrelatedButton = document.getElementById('unrelated-button');
  
//   // Debug logging
//   console.log('URL Input element:', urlInput);
//   console.log('Legitimate Button element:', legitButton);
//   console.log('Fraudulent Button element:', fraudButton);
//   console.log('Unrelated Button element:', unrelatedButton);
  
//   // Event listener for Legitimate button (green)
//   if (legitButton) {
//     legitButton.addEventListener('click', async function(e) {
//       e.preventDefault();
//       console.log('Legitimate button clicked');
      
//       const url = urlInput.value.trim();
//       if (!url) {
//         showNotification('Please enter a valid URL', 'error');
//         return;
//       }
      
//       try {
//         await updateClassification(url, "Legitimate");
//         urlInput.value = '';
//       } catch (error) {
//         // Error handled in updateClassification function
//       }
//     });
//   } else {
//     console.error('Legitimate button not found in the DOM');
//   }
  
//   // Event listener for Fraudulent button (red)
//   if (fraudButton) {
//     fraudButton.addEventListener('click', async function(e) {
//       e.preventDefault();
//       console.log('Fraudulent button clicked');
      
//       const url = urlInput.value.trim();
//       if (!url) {
//         showNotification('Please enter a valid URL', 'error');
//         return;
//       }
      
//       try {
//         await updateClassification(url, "Fraudulent");
//         urlInput.value = '';
//       } catch (error) {
//         // Error handled in updateClassification function
//       }
//     });
//   } else {
//     console.error('Fraudulent button not found in the DOM');
//   }
  
//   // Event listener for Unrelated button (yellow)
//   if (unrelatedButton) {
//     unrelatedButton.addEventListener('click', async function(e) {
//       e.preventDefault();
//       console.log('Unrelated button clicked');
      
//       const url = urlInput.value.trim();
//       if (!url) {
//         showNotification('Please enter a valid URL', 'error');
//         return;
//       }
      
//       try {
//         await updateClassification(url, "Unrelated");
//         urlInput.value = '';
//       } catch (error) {
//         // Error handled in updateClassification function
//       }
//     });
//   } else {
//     console.error('Unrelated button not found in the DOM');
//   }
  
//   // Log user ID for debugging
//   getUserId().then(userId => {
//     console.log('[FishGuard] Using user ID:', userId);
//   });
// });

// // Remove the duplicate code outside of DOMContentLoaded

document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM content loaded, setting up event listeners for URL classification');
  
  // Wait for a short time to ensure all elements are fully loaded
  setTimeout(function() {
    const urlInput = document.getElementById('url-input');
    const legitButton = document.getElementById('legitimate-button');
    const fraudButton = document.getElementById('fraudulent-button');
    const unrelatedButton = document.getElementById('unrelated-button');
    
    console.log('URL Input element:', urlInput);
    console.log('Legitimate Button element:', legitButton);
    console.log('Fraudulent Button element:', fraudButton);
    console.log('Unrelated Button element:', unrelatedButton);
    
    // Only add event listeners if the elements exist
    if (legitButton) {
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
      console.error('Legitimate button not found in the DOM');
    }
    
    if (fraudButton) {
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
      console.error('Fraudulent button not found in the DOM');
    }
    
    if (unrelatedButton) {
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
      console.error('Unrelated button not found in the DOM');
    }
  }, 100); // Small timeout to ensure DOM is fully loaded
  
  // Log user ID for debugging
  getUserId().then(userId => {
    console.log('[FishGuard] Using user ID:', userId);
  });
});