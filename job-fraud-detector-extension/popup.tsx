

// import React, { useState, useEffect } from "react"
// import { Storage } from "@plasmohq/storage"

// function IndexPopup() {
//   const [legitimateCount, setLegitimateCount] = useState(0)
//   const [unrelatedCount, setUnrelatedCount] = useState(0)
//   const [fraudulentCount, setFraudulentCount] = useState(0)
//   const storage = new Storage()

//   // Function to fetch all counts from storage
//   const fetchCounts = async () => {
//     const legitimate = (await storage.get("legitimateJobsCount")) || 0
//     const unrelated = (await storage.get("unrelatedCount")) || 0
//     const fraudulent = (await storage.get("fraudulentJobsCount")) || 0

//     setLegitimateCount(Number(legitimate))
//     setUnrelatedCount(Number(unrelated))
//     setFraudulentCount(Number(fraudulent))

//     console.log("Popup stats updated:", {
//       legitimate: Number(legitimate),
//       unrelated: Number(unrelated),
//       fraudulent: Number(fraudulent)
//     })
//   }

//   useEffect(() => {
//     // Initial fetch
//     fetchCounts()

//     // Set up polling to check for updates every 2 seconds
//     const interval = setInterval(fetchCounts, 2000)
    
//     // Watch storage for changes
//     const watchCallbacks = {
//       "legitimateJobsCount": () => fetchCounts(),
//       "unrelatedCount": () => fetchCounts(),
//       "fraudulentJobsCount": () => fetchCounts()
//     }
    
//     storage.watch(watchCallbacks)
    
//     // Cleanup function
//     return () => {
//       clearInterval(interval)
//       // Unregister the storage watchers
//       storage.unwatch(watchCallbacks)
//     }
//   }, [])

//   return (
//     <div
//       style={{
//         width: "250px",
//         padding: "20px",
//         textAlign: "center",
//         fontFamily: "Arial, sans-serif",
//         backgroundColor: "transparent", // Fully remove background
//         display: "flex",
//         justifyContent: "center",
//         alignItems: "center"
//       }}>
//       <div
//         style={{
//           width: "100%",
//           padding: "15px",
//           borderRadius: "20px", // Rounded corners
//           backgroundColor: "#007BFF", // Blue background for the inner div
//           color: "white", // White text for contrast
//           boxShadow: "0 4px 10px rgba(0,0,0,0.2)" // Soft shadow for floating effect
//         }}>
//         <h2>Job Fraud Detector</h2>
//         <div>
//           <p>
//             <strong>Legitimate Jobs Detected:</strong>{" "}
//             <span style={{ color: "lightgreen" }}>{legitimateCount}</span>
//           </p>
//           <p>
//             <strong>Unrelated URLs:</strong>{" "}
//             <span style={{ color: "yellow" }}>{unrelatedCount}</span>
//           </p>
//           <p>
//             <strong>Fraudulent Jobs Detected:</strong>{" "}
//             <span style={{ color: "red" }}>{fraudulentCount}</span>
//           </p>
//         </div>
//       </div>
//     </div>
//   )
// }

// export default IndexPopup




import React, { useState, useEffect } from "react"
import { Storage } from "@plasmohq/storage"

function IndexPopup() {
  const [legitimateCount, setLegitimateCount] = useState(0)
  const [unrelatedCount, setUnrelatedCount] = useState(0)
  const [fraudulentCount, setFraudulentCount] = useState(0)
  const storage = new Storage()

  // Function to fetch all counts from storage
  const fetchCounts = async () => {
    const legitimate = (await storage.get("legitimateJobsCount")) || 0
    const unrelated = (await storage.get("unrelatedCount")) || 0
    const fraudulent = (await storage.get("fraudulentJobsCount")) || 0

    setLegitimateCount(Number(legitimate))
    setUnrelatedCount(Number(unrelated))
    setFraudulentCount(Number(fraudulent))

    console.log("Popup stats updated:", {
      legitimate: Number(legitimate),
      unrelated: Number(unrelated),
      fraudulent: Number(fraudulent)
    })
  }

  useEffect(() => {
    // Initial fetch
    fetchCounts()

    // Set up polling to check for updates every 2 seconds
    const interval = setInterval(fetchCounts, 2000)
    
    // Watch storage for changes
    const watchCallbacks = {
      "legitimateJobsCount": () => fetchCounts(),
      "unrelatedCount": () => fetchCounts(),
      "fraudulentJobsCount": () => fetchCounts()
    }
    
    storage.watch(watchCallbacks)
    
    // Cleanup function
    return () => {
      clearInterval(interval)
      // Unregister the storage watchers
      storage.unwatch(watchCallbacks)
    }
  }, [])

  return (
    <div style={{
      width: "250px",
      padding: "16px",
      fontFamily: "Arial, sans-serif",
      backgroundColor: "#1e2430",
      borderRadius: "12px",
      overflow: "hidden",
      color: "white"
    }}>
      {/* Header */}
      <div style={{
        display: "flex",
        alignItems: "center",
        marginBottom: "16px"
      }}>
        <div style={{
          marginRight: "8px",
          color: "#fbbf24" // yellow color
        }}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
          </svg>
        </div>
        <h2 style={{
          fontSize: "20px",
          fontWeight: "bold",
          margin: 0,
          color: "#00b4d8"
        }}>SafeHire Wizard</h2>
      </div>

      {/* Stats Cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {/* Legitimate Jobs */}
        <div style={{
          backgroundColor: "#3a4151",
          borderRadius: "8px",
          padding: "12px"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center"
          }}>
            <div style={{
              marginRight: "12px",
              color: "#10b981" // green
            }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              width: "100%"
            }}>
              <span style={{
                color: "white",
                fontSize: "14px",
                fontWeight: "500"
              }}>Legitimate Jobs:</span>
              <span style={{
                color: "#34d399", // light green
                fontWeight: "bold"
              }}>{legitimateCount}</span>
            </div>
          </div>
        </div>

        {/* Unrelated URLs */}
        <div style={{
          backgroundColor: "#3a4151",
          borderRadius: "8px",
          padding: "12px"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center"
          }}>
            <div style={{
              marginRight: "12px",
              color: "#f59e0b" // yellow/amber
            }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              width: "100%"
            }}>
              <span style={{
                color: "white",
                fontSize: "14px",
                fontWeight: "500"
              }}>Unrelated URLs:</span>
              <span style={{
                color: "#fbbf24", // yellow
                fontWeight: "bold"
              }}>{unrelatedCount}</span>
            </div>
          </div>
        </div>

        {/* Fraudulent Jobs */}
        <div style={{
          backgroundColor: "#3a4151",
          borderRadius: "8px",
          padding: "12px"
        }}>
          <div style={{
            display: "flex",
            alignItems: "center"
          }}>
            <div style={{
              marginRight: "12px",
              color: "#ef4444" // red
            }}>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </div>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              width: "100%"
            }}>
              <span style={{
                color: "white",
                fontSize: "14px",
                fontWeight: "500"
              }}>Fraudulent Jobs:</span>
              <span style={{
                color: "#f87171", // light red
                fontWeight: "bold"
              }}>{fraudulentCount}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default IndexPopup