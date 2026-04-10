import React, { useEffect, useState } from 'react';
import { ScanText, ServerCrash, Server } from 'lucide-react';
import { checkHealth } from '../../services/api';

const Navbar = () => {
  const [isHealthy, setIsHealthy] = useState(true);

  useEffect(() => {
    const verifyHealth = async () => {
      const healthy = await checkHealth();
      setIsHealthy(healthy);
    };
    verifyHealth();
    
    // Periodically check health
    const interval = setInterval(verifyHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-2 rounded-lg text-white">
              <ScanText size={24} />
            </div>
            <span className="font-bold text-xl text-gray-900 tracking-tight">Invoice<span className="text-blue-600">OCR</span></span>
          </div>
          
          <div className="flex items-center gap-2 text-sm font-medium">
            {isHealthy ? (
              <span className="flex items-center gap-1.5 text-green-600 bg-green-50 px-3 py-1.5 rounded-full ring-1 ring-green-600/20">
                <Server size={16} /> Backend Online
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-red-600 bg-red-50 px-3 py-1.5 rounded-full ring-1 ring-red-600/20">
                <ServerCrash size={16} /> Backend Offline
              </span>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
