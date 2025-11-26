import React, { useState } from 'react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import QueryInterface from './components/QueryInterface';
import DatabaseViewer from './components/DatabaseViewer';
import InstallPWA from './components/InstallPWA';
import OfflineIndicator from './components/OfflineIndicator';
import './App.css';

function App() {
  const [uploadCount, setUploadCount] = useState(0);
  const [activeTab, setActiveTab] = useState('query');

  const handleUploadSuccess = () => {
    setUploadCount(prev => prev + 1);
  };

  return (
    <div className="App">
      <Header uploadCount={uploadCount} />
      <OfflineIndicator />
      <InstallPWA />
      
      <div className="container">
        <div className="content">
          <FileUpload onUploadSuccess={handleUploadSuccess} />
          
          <div className="tabs">
            <button 
              className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
              onClick={() => setActiveTab('query')}
            >
              🔍 Query Documents
            </button>
            <button 
              className={`tab-button ${activeTab === 'database' ? 'active' : ''}`}
              onClick={() => setActiveTab('database')}
            >
              📊 View Database
            </button>
          </div>

          {activeTab === 'query' && <QueryInterface />}
          {activeTab === 'database' && <DatabaseViewer />}
        </div>
        
        <footer className="app-footer">
          <p>Built with React, FastAPI, FAISS, and Ollama</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
