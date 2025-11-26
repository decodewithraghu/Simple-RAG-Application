import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadDocument, getCollections } from '../api';
import './FileUpload.css';

const FileUpload = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState(null);
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('default');
  const [newCollection, setNewCollection] = useState('');
  const [showNewCollection, setShowNewCollection] = useState(false);

  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    try {
      const data = await getCollections();
      const collectionNames = Object.keys(data.collections || {});
      setCollections(collectionNames.length > 0 ? collectionNames : ['default']);
    } catch (err) {
      console.error('Failed to load collections:', err);
      setCollections(['default']);
    }
  };

  const onDrop = async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    const collection = showNewCollection && newCollection ? newCollection : selectedCollection;
    
    setUploading(true);
    setError(null);
    setUploadStatus(null);

    try {
      const result = await uploadDocument(file, collection);
      setUploadStatus(result);
      await loadCollections();
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
      setNewCollection('');
      setShowNewCollection(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div className="file-upload-container">
      <h2>Upload Document</h2>
      
      <div className="collection-selector">
        <label htmlFor="collection">Collection (Partition):</label>
        <div className="collection-input-group">
          {!showNewCollection ? (
            <>
              <select
                id="collection"
                value={selectedCollection}
                onChange={(e) => setSelectedCollection(e.target.value)}
                disabled={uploading}
              >
                {collections.map(coll => (
                  <option key={coll} value={coll}>{coll}</option>
                ))}
              </select>
              <button
                className="new-collection-btn"
                onClick={() => setShowNewCollection(true)}
                disabled={uploading}
              >
                + New Collection
              </button>
            </>
          ) : (
            <>
              <input
                type="text"
                value={newCollection}
                onChange={(e) => setNewCollection(e.target.value)}
                placeholder="Enter new collection name"
                disabled={uploading}
              />
              <button
                className="cancel-btn"
                onClick={() => {
                  setShowNewCollection(false);
                  setNewCollection('');
                }}
                disabled={uploading}
              >
                Cancel
              </button>
            </>
          )}
        </div>
      </div>
      
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'disabled' : ''}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="upload-spinner">
            <div className="spinner"></div>
            <p>Uploading and processing...</p>
          </div>
        ) : isDragActive ? (
          <p>Drop the file here...</p>
        ) : (
          <div>
            <p>Drag & drop a PDF or TXT file here</p>
            <p className="or-text">or</p>
            <button className="browse-button">Browse Files</button>
            <p className="file-types">Supported: PDF, TXT (max 10MB)</p>
          </div>
        )}
      </div>

      {uploadStatus && (
        <div className="upload-success">
          <h3>✓ Upload Successful!</h3>
          <p><strong>File:</strong> {uploadStatus.filename}</p>
          <p><strong>Collection:</strong> {uploadStatus.collection}</p>
          <p><strong>Chunks Created:</strong> {uploadStatus.chunks_created}</p>
          <p><strong>Document ID:</strong> {uploadStatus.document_id}</p>
        </div>
      )}

      {error && (
        <div className="upload-error">
          <h3>✗ Upload Failed</h3>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
