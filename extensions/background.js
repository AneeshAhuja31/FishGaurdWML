// Extension installation event
console.log('[FishGuard] Service worker starting...');

// Keep a persistent connection to avoid being shut down
let keepAlivePort = null;

// Handle installation
chrome.runtime.onInstalled.addListener(async () => {
  console.log('[FishGuard] Extension installed');
  
  // Initialize storage
  await chrome.storage.local.set({ 
    cachedUrls: {}, 
    cachedJobs: {},
    sessionId: generateSessionId(),
    lastActivity: Date.now(), // Add last activity timestamp
    statistics: { 
      phishingDetected: 0, 
      suspiciousJobs: 0, 
      maliciousJobs: 0 
    } 
  });
  console.log('[FishGuard] Storage initialized');
  
  // Set up the keep-alive alarm
  chrome.alarms.create("keepAlive", { periodInMinutes: 1 });
  
  // Set up session check alarm (check every 5 minutes)
  chrome.alarms.create("sessionCheck", { periodInMinutes: 5 });
});

// Generate a unique session ID
function generateSessionId() {
  return Date.now().toString(36) + Math.random().toString(36).substring(2);
}

// Keep-alive mechanism
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "keepAlive") {
    console.log("[FishGuard] Keeping service worker alive...");
    
    // Send a ping to keep the service worker alive
    fetch("https://www.google.com", { mode: "no-cors" })
      .then(() => console.log("[FishGuard] Keep-alive request sent"))
      .catch(err => console.warn("[FishGuard] Keep-alive ping failed", err));
    
    // Check if we need to reconnect the port
    if (!keepAlivePort || keepAlivePort.disconnect) {
      try {
        keepAlivePort = chrome.runtime.connect({ name: "keepAlive" });
        console.log("[FishGuard] Reconnected keep-alive port");
      } catch (error) {
        console.warn("[FishGuard] Failed to reconnect keep-alive port", error);
      }
    }
  } else if (alarm.name === "sessionCheck") {
    // Check for session timeout
    checkSessionTimeout();
  }
});

// Check if session has timed out (30 minutes of inactivity)
function checkSessionTimeout() {
  chrome.storage.local.get(['lastActivity'], (result) => {
    const now = Date.now();
    const lastActivity = result.lastActivity || now;
    
    console.log("[FishGuard] Checking session timeout. Last activity:", new Date(lastActivity).toLocaleString());
    
    // If session is older than 30 minutes
    if (now - lastActivity > 30 * 60 * 1000) {
      console.log("[FishGuard] Session timeout detected, creating new session");
      createNewSession();
    }
  });
}

// Handle port connections
chrome.runtime.onConnect.addListener((port) => {
  console.log("[FishGuard] Port connected:", port.name);
  
  if (port.name === "keepAlive") {
    keepAlivePort = port;
  }
  
  port.onDisconnect.addListener(() => {
    console.log("[FishGuard] Port disconnected:", port.name);
    if (port.name === "keepAlive") {
      keepAlivePort = null;
    }
  });
});

// Create a new session
async function createNewSession() {
  const sessionId = generateSessionId();
  const lastActivity = Date.now();
  const statistics = { 
    phishingDetected: 0, 
    suspiciousJobs: 0, 
    maliciousJobs: 0 
  };
  
  await chrome.storage.local.set({ sessionId, statistics, lastActivity });
  console.log('[FishGuard] New session created:', sessionId);
  return { sessionId, statistics };
}

// Handle messages from popup.js or content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log(`[FishGuard] Message received in background.js:`, message);
  
  // Update last activity time for any message received
  chrome.storage.local.set({ lastActivity: Date.now() });
  
  if (message.type === 'updateStats') {
    chrome.storage.local.get(['statistics', 'sessionId'], (result) => {
      const stats = result.statistics || { 
        phishingDetected: 0, 
        suspiciousJobs: 0, 
        maliciousJobs: 0 
      };
      
      let updated = false;
      
      // For single phishing detection
      if (message.data.phishingDetected) {
        stats.phishingDetected++;
        console.log(`[FishGuard] Phishing detected! New count: ${stats.phishingDetected}`);
        updated = true;
      }
      
      // Handle batch updates of phishing links
      if (message.data.phishingDetectedCount && message.data.phishingDetectedCount > 0) {
        stats.phishingDetected += message.data.phishingDetectedCount;
        console.log(`[FishGuard] ${message.data.phishingDetectedCount} phishing links detected! New count: ${stats.phishingDetected}`);
        updated = true;
      }
      
      if (message.data.jobStatus === 'suspicious') {
        stats.suspiciousJobs++;
        console.log(`[FishGuard] Suspicious job detected! New count: ${stats.suspiciousJobs}`);
        updated = true;
      }
      
      if (message.data.jobStatus === 'malicious') {
        stats.maliciousJobs++;
        console.log(`[FishGuard] Malicious job detected! New count: ${stats.maliciousJobs}`);
        updated = true;
      }
      
      if (updated) {
        chrome.storage.local.set({ statistics: stats }, () => {
          console.log('[FishGuard] Statistics updated in background:', stats);
          sendResponse({ status: "success", stats: stats });
        });
      } else {
        sendResponse({ status: "no update needed" });
      }
    });
    
    // This is important! Return true to indicate you'll call sendResponse asynchronously
    return true;
  }
  
  if (message.type === 'startNewSession') {
    createNewSession().then(({ sessionId, statistics }) => {
      sendResponse({ status: "success", sessionId, statistics });
    }).catch(error => {
      console.error('[FishGuard] Error creating new session:', error);
      sendResponse({ status: "error", message: error.message });
    });
    
    return true;
  }
  
  if (message.type === 'getSessionStats') {
    chrome.storage.local.get(['statistics', 'sessionId', 'lastActivity'], (result) => {
      // Check for session timeout here as well
      const now = Date.now();
      const lastActivity = result.lastActivity || now;
      
      // If session is older than 30 minutes, create a new one before responding
      if (now - lastActivity > 30 * 60 * 1000) {
        console.log("[FishGuard] Session timeout detected during stats request, creating new session");
        createNewSession().then(({ sessionId, statistics }) => {
          sendResponse({ 
            status: "success", 
            stats: statistics,
            sessionId: sessionId,
            note: "New session created due to timeout"
          });
        });
      } else {
        // Return current stats
        sendResponse({ 
          status: "success", 
          stats: result.statistics || { phishingDetected: 0, suspiciousJobs: 0, maliciousJobs: 0 },
          sessionId: result.sessionId
        });
      }
    });
    
    return true;
  }
});

// Handle errors
chrome.runtime.lastError && console.error('[FishGuard] Runtime error:', chrome.runtime.lastError);

// // Extension installation event
// console.log('[FishGuard] Service worker starting...');

// // Keep a persistent connection to avoid being shut down
// let keepAlivePort = null;

// // Handle installation
// chrome.runtime.onInstalled.addListener(async () => {
//   console.log('[FishGuard] Extension installed');
  
//   // Initialize storage
//   await chrome.storage.local.set({ 
//     cachedUrls: {}, 
//     cachedJobs: {},
//     sessionId: generateSessionId(),
//     statistics: { 
//       phishingDetected: 0, 
//       suspiciousJobs: 0, 
//       maliciousJobs: 0 
//     } 
//   });
//   console.log('[FishGuard] Storage initialized');
  
//   // Set up the keep-alive alarm
//   chrome.alarms.create("keepAlive", { periodInMinutes: 1 });
  
// });

// // Generate a unique session ID
// function generateSessionId() {
//   return Date.now().toString(36) + Math.random().toString(36).substring(2);
// }

// // Keep-alive mechanism
// chrome.alarms.onAlarm.addListener((alarm) => {
//   if (alarm.name === "keepAlive") {
//     console.log("[FishGuard] Keeping service worker alive...");
    
//     // Send a ping to keep the service worker alive
//     fetch("https://www.google.com", { mode: "no-cors" })
//       .then(() => console.log("[FishGuard] Keep-alive request sent"))
//       .catch(err => console.warn("[FishGuard] Keep-alive ping failed", err));
    
//     // Check if we need to reconnect the port
//     if (!keepAlivePort || keepAlivePort.disconnect) {
//       try {
//         keepAlivePort = chrome.runtime.connect({ name: "keepAlive" });
//         console.log("[FishGuard] Reconnected keep-alive port");
//       } catch (error) {
//         console.warn("[FishGuard] Failed to reconnect keep-alive port", error);
//       }
//     }
//   }
// });

// // Handle port connections
// chrome.runtime.onConnect.addListener((port) => {
//   console.log("[FishGuard] Port connected:", port.name);
  
//   if (port.name === "keepAlive") {
//     keepAlivePort = port;
//   }
  
//   port.onDisconnect.addListener(() => {
//     console.log("[FishGuard] Port disconnected:", port.name);
//     if (port.name === "keepAlive") {
//       keepAlivePort = null;
//     }
//   });
// });

// // Create a new session
// async function createNewSession() {
//   const sessionId = generateSessionId();
//   const statistics = { 
//     phishingDetected: 0, 
//     suspiciousJobs: 0, 
//     maliciousJobs: 0 
//   };
  
//   await chrome.storage.local.set({ sessionId, statistics });
//   console.log('[FishGuard] New session created:', sessionId);
//   return { sessionId, statistics };
// }

// //USED TO UPDATE THE STATISTIC DATA
// // Handle messages from popup.js or content scripts
// chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
//   console.log(`[FishGuard] Message received in background.js:`, message);
  
//   if (message.type === 'updateStats') {
//     chrome.storage.local.get(['statistics', 'sessionId'], (result) => {
//       const stats = result.statistics || { // either previous stats or new initialized stats
//         phishingDetected: 0, 
//         suspiciousJobs: 0, 
//         maliciousJobs: 0 
//       };
      
//       let updated = false;
      
//       //for single phishing detection
//       if (message.data.phishingDetected) {
//         stats.phishingDetected++;
//         console.log(`[FishGuard] Phishing detected! New count: ${stats.phishingDetected}`);
//         updated = true;
//       }
      
//       // Handle batch updates of phishing links
//       if (message.data.phishingDetectedCount && message.data.phishingDetectedCount > 0) {
//         stats.phishingDetected += message.data.phishingDetectedCount;
//         console.log(`[FishGuard] ${message.data.phishingDetectedCount} phishing links detected! New count: ${stats.phishingDetected}`);
//         updated = true;
//       }
      
//       if (message.data.jobStatus === 'suspicious') {
//         stats.suspiciousJobs++;
//         console.log(`[FishGuard] Suspicious job detected! New count: ${stats.suspiciousJobs}`);
//         updated = true;
//       }
      
//       if (message.data.jobStatus === 'malicious') {
//         stats.maliciousJobs++;
//         console.log(`[FishGuard] Malicious job detected! New count: ${stats.maliciousJobs}`);
//         updated = true;
//       }
      
//       if (updated) {
//         chrome.storage.local.set({ statistics: stats }, () => {
//           console.log('[FishGuard] Statistics updated in background:', stats);
//           sendResponse({ status: "success", stats: stats });
//         });
//       } else {
//         sendResponse({ status: "no update needed" });
//       }
//     });
    
//     // This is important! Return true to indicate you'll call sendResponse asynchronously
//     return true;
//   }
  
//   if (message.type === 'startNewSession') {
//     createNewSession().then(({ sessionId, statistics }) => {
//       sendResponse({ status: "success", sessionId, statistics });
//     }).catch(error => {
//       console.error('[FishGuard] Error creating new session:', error);
//       sendResponse({ status: "error", message: error.message });
//     });
    
//     return true;
//   }
  
//   if (message.type === 'getSessionStats') {
//     chrome.storage.local.get(['statistics', 'sessionId'], (result) => {
//       sendResponse({ 
//         status: "success", 
//         stats: result.statistics || { phishingDetected: 0, suspiciousJobs: 0, maliciousJobs: 0 },
//         sessionId: result.sessionId
//       });
//     });
    
//     return true;
//   }
// });

// // Handle errors
// chrome.runtime.lastError && console.error('[FishGuard] Runtime error:', chrome.runtime.lastError);