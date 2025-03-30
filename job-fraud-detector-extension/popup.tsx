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

// // export default IndexPopup
// import React, { useState, useEffect } from "react"
// import { Storage } from "@plasmohq/storage"

// function IndexPopup() {
//   const [legitimateCount, setLegimateCount] = useState(0)
//   const [unrelatedCount, setUnrelatedCount] = useState(0)
//   const [fraudulentCount, setFraudulentCount] = useState(0)
//   const storage = new Storage()

//   useEffect(() => {
//     async function fetchLegitimateCount() {
//       const count = (await storage.get("legitimateJobsCount")) || 0
//       setLegimateCount(Number(count))
//     }
//     async function fetchUnrelatedCount() {
//       const count = (await storage.get("unrelatedCount")) || 0
//       setUnrelatedCount(Number(count))
//     }
//     async function fetchFraudulentCount() {
//       const count = (await storage.get("fraudulentJobsCount")) || 0
//       setFraudulentCount(Number(count))
//     }
//     fetchLegitimateCount()
//     fetchUnrelatedCount()
//     fetchFraudulentCount()
//   }, [])

//   return (
//     <div
//       style={{
//         width: "250px",
//         padding: "20px",
//         textAlign: "center",
//         fontFamily: "Arial, sans-serif",
//         backgroundColor: "transparent", // Outer div is transparent
//         display: "flex",
//         justifyContent: "center",
//         alignItems: "center"
//       }}>
//       <div
//         style={{
//           width: "100%",
//           // padding: "15px",
//           borderRadius: "15px", // Rounded corners
//           backgroundColor: "#007BFF", // Blue background for the inner div
//           color: "white", // White text for better contrast
//           boxShadow: "0 4px 10px rgba(0,0,0,0.2)" // Soft shadow
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


// import React, { useState, useEffect } from "react"
// import { Storage } from "@plasmohq/storage"

// function IndexPopup() {
//   const [legitimateCount, setLegimateCount] = useState(0)
//   const [unrelatedCount, setUnrelatedCount] = useState(0)
//   const [fraudulentCount, setFraudulentCount] = useState(0)
//   const storage = new Storage()

//   useEffect(() => {
//     async function fetchLegitimateCount() {
//       const count = (await storage.get("legitimateJobsCount")) || 0
//       setLegimateCount(Number(count))
//     }
//     async function fetchUnrelatedCount() {
//       const count = (await storage.get("unrelatedCount")) || 0
//       setUnrelatedCount(Number(count))
//     }
//     async function fetchFraudulentCount() {
//       const count = (await storage.get("fraudulentJobsCount")) || 0
//       setFraudulentCount(Number(count))
//     }
//     fetchLegitimateCount()
//     fetchUnrelatedCount()
//     fetchFraudulentCount()
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
//             <span style={{ color: "green" }}>{legitimateCount}</span>
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
    <div
      style={{
        width: "250px",
        padding: "20px",
        textAlign: "center",
        fontFamily: "Arial, sans-serif",
        backgroundColor: "transparent", // Fully remove background
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
      }}>
      <div
        style={{
          width: "100%",
          padding: "15px",
          borderRadius: "20px", // Rounded corners
          backgroundColor: "#007BFF", // Blue background for the inner div
          color: "white", // White text for contrast
          boxShadow: "0 4px 10px rgba(0,0,0,0.2)" // Soft shadow for floating effect
        }}>
        <h2>Job Fraud Detector</h2>
        <div>
          <p>
            <strong>Legitimate Jobs Detected:</strong>{" "}
            <span style={{ color: "lightgreen" }}>{legitimateCount}</span>
          </p>
          <p>
            <strong>Unrelated URLs:</strong>{" "}
            <span style={{ color: "yellow" }}>{unrelatedCount}</span>
          </p>
          <p>
            <strong>Fraudulent Jobs Detected:</strong>{" "}
            <span style={{ color: "red" }}>{fraudulentCount}</span>
          </p>
        </div>
      </div>
    </div>
  )
}

export default IndexPopup