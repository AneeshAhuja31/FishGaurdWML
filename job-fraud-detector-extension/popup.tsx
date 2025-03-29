import React, { useState, useEffect } from "react"
import { Storage } from "@plasmohq/storage"

function IndexPopup() {
  const [fraudulentCount, setFraudulentCount] = useState(0)
  const storage = new Storage()

  useEffect(() => {
    async function fetchFraudulentCount() {
      const count = await storage.get('fraudulentJobsCount') || 0
      setFraudulentCount(Number(count))
    }
    fetchFraudulentCount()
  }, [])

  return (
    <div style={{
      width: '300px', 
      padding: '20px', 
      textAlign: 'center', 
      fontFamily: 'Arial, sans-serif'
    }}>
      <h2>Job Fraud Detector</h2>
      <div>
        <p>Fraudulent Jobs Detected:</p>
        <h3 style={{ color: 'red' }}>{fraudulentCount}</h3>
      </div>
    </div>
  )
}

export default IndexPopup