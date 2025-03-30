import { useState, useEffect } from "react";

const IndexPopup = () => {
  const [legitimateCount, setLegitimateCount] = useState(33);
  const [unrelatedCount, setUnrelatedCount] = useState(28);
  const [fraudulentCount, setFraudulentCount] = useState(14);

  useEffect(() => {
    const fetchCounts = () => {
      setLegitimateCount((prev) => prev + Math.floor(Math.random() * 2));
      setUnrelatedCount((prev) => prev + Math.floor(Math.random() * 2));
      setFraudulentCount((prev) => prev + (Math.random() < 0.3 ? 1 : 0));
    };

    const interval = setInterval(fetchCounts, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-64 bg-gray-900 rounded-xl overflow-hidden p-4 font-sans" style={{ backgroundColor: "#1e2430" }}>
      {/* Header */}
      <div className="flex items-center mb-4">
        <div className="mr-2 text-yellow-400">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
          </svg>
        </div>
        <h2 className="text-xl font-bold" style={{ color: "#00b4d8" }}>SafeHire Wizard</h2>
      </div>

      {/* Stats Cards */}
      <div className="space-y-3">
        {/* Legitimate Jobs */}
        <div className="rounded-lg p-3" style={{ backgroundColor: "#3a4151" }}>
          <div className="flex items-center">
            <div className="mr-3 text-green-500">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <div className="flex justify-between items-center w-full">
              <span className="text-white text-sm font-medium">Legitimate Jobs:</span>
              <span className="text-green-400 font-bold">{legitimateCount}</span>
            </div>
          </div>
        </div>

        {/* Unrelated URLs */}
        <div className="rounded-lg p-3" style={{ backgroundColor: "#3a4151" }}>
          <div className="flex items-center">
            <div className="mr-3 text-yellow-500">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
            <div className="flex justify-between items-center w-full">
              <span className="text-white text-sm font-medium">Unrelated URLs:</span>
              <span className="text-yellow-400 font-bold">{unrelatedCount}</span>
            </div>
          </div>
        </div>

        {/* Fraudulent Jobs */}
        <div className="rounded-lg p-3" style={{ backgroundColor: "#3a4151" }}>
          <div className="flex items-center">
            <div className="mr-3 text-red-500">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </div>
            <div className="flex justify-between items-center w-full">
              <span className="text-white text-sm font-medium">Fraudulent Jobs:</span>
              <span className="text-red-400 font-bold">{fraudulentCount}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IndexPopup;