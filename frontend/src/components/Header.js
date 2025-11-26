import React, { useState, useEffect } from 'react';
import { getHealth, getStats } from '../api';
import './Header.css';

const Header = ({ uploadCount }) => {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchHealthAndStats();
    const interval = setInterval(fetchHealthAndStats, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [uploadCount]);

  const fetchHealthAndStats = async () => {
    try {
      const [healthData, statsData] = await Promise.all([
        getHealth(),
        getStats()
      ]);
      setHealth(healthData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch health/stats:', error);
    }
  };

  return (
    <header className="app-header">
      <div className="header-content">
        <h1>📚 RAG Application</h1>
        <p className="subtitle">Retrieval-Augmented Generation with Ollama</p>
        
        <div className="status-bar">
          {health && (
            <>
              <div className={`status-item ${health.ollama_status === 'available' ? 'healthy' : 'unhealthy'}`}>
                <span className="status-dot"></span>
                <span>Ollama: {health.ollama_status}</span>
              </div>
              
              {stats && (
                <>
                  <div className="status-item">
                    <span>📄 Documents: {stats.uploaded_files}</span>
                  </div>
                  <div className="status-item">
                    <span>🔖 Chunks: {stats.total_chunks}</span>
                  </div>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
