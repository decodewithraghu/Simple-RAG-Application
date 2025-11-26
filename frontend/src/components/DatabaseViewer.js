import React, { useState, useEffect } from 'react';
import { getCollections, getDocumentsInCollection, getDocumentDetails, deleteDocument, deleteCollection } from '../api';
import './DatabaseViewer.css';

const DatabaseViewer = () => {
  const [collections, setCollections] = useState({});
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [documentDetails, setDocumentDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCollections();
  }, []);

  useEffect(() => {
    if (selectedCollection) {
      loadDocuments(selectedCollection);
    }
  }, [selectedCollection]);

  const loadCollections = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCollections();
      setCollections(data.collections || {});
      
      // Auto-select first collection
      const collectionNames = Object.keys(data.collections || {});
      if (collectionNames.length > 0 && !selectedCollection) {
        setSelectedCollection(collectionNames[0]);
      }
    } catch (err) {
      setError('Failed to load collections');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadDocuments = async (collectionName) => {
    setLoading(true);
    setError(null);
    setDocumentDetails(null);
    setSelectedDocument(null);
    try {
      const data = await getDocumentsInCollection(collectionName);
      setDocuments(data.documents || []);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadDocumentDetails = async (collectionName, documentId) => {
    setLoading(true);
    setError(null);
    try {
      const data = await getDocumentDetails(collectionName, documentId);
      setDocumentDetails(data);
      setSelectedDocument(documentId);
    } catch (err) {
      setError('Failed to load document details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async (collectionName, documentId, filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await deleteDocument(collectionName, documentId);
      setDocumentDetails(null);
      setSelectedDocument(null);
      await loadDocuments(collectionName);
      await loadCollections();
    } catch (err) {
      setError('Failed to delete document');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCollection = async (collectionName) => {
    if (!window.confirm(`Are you sure you want to delete collection "${collectionName}" and all its documents?`)) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await deleteCollection(collectionName);
      setSelectedCollection(null);
      setDocuments([]);
      setDocumentDetails(null);
      setSelectedDocument(null);
      await loadCollections();
    } catch (err) {
      setError('Failed to delete collection');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="database-viewer-container">
      <h2>📊 Vector Database Viewer</h2>

      {error && (
        <div className="db-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="db-layout">
        {/* Collections Sidebar */}
        <div className="db-sidebar">
          <div className="sidebar-header">
            <h3>Collections</h3>
            <button onClick={loadCollections} className="refresh-btn" disabled={loading}>
              🔄
            </button>
          </div>
          
          <div className="collections-list">
            {Object.entries(collections).map(([name, count]) => (
              <div
                key={name}
                className={`collection-item ${selectedCollection === name ? 'active' : ''}`}
                onClick={() => setSelectedCollection(name)}
              >
                <div className="collection-name">{name}</div>
                <div className="collection-count">{count} chunks</div>
                <button
                  className="delete-collection-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteCollection(name);
                  }}
                  disabled={loading}
                >
                  🗑️
                </button>
              </div>
            ))}
            
            {Object.keys(collections).length === 0 && (
              <div className="empty-state">No collections yet</div>
            )}
          </div>
        </div>

        {/* Documents List */}
        <div className="db-main">
          {selectedCollection && (
            <>
              <div className="main-header">
                <h3>Documents in "{selectedCollection}"</h3>
                <span className="doc-count">{documents.length} documents</span>
              </div>

              <div className="documents-list">
                {documents.map((doc) => (
                  <div
                    key={doc.document_id}
                    className={`document-item ${selectedDocument === doc.document_id ? 'active' : ''}`}
                  >
                    <div className="document-info">
                      <div className="document-filename">{doc.filename}</div>
                      <div className="document-meta">
                        <span className="doc-id">{doc.document_id.substring(0, 8)}...</span>
                        <span className="chunk-count">{doc.num_chunks} chunks</span>
                      </div>
                    </div>
                    
                    <div className="document-actions">
                      <button
                        className="view-btn"
                        onClick={() => loadDocumentDetails(selectedCollection, doc.document_id)}
                        disabled={loading}
                      >
                        View
                      </button>
                      <button
                        className="delete-btn"
                        onClick={() => handleDeleteDocument(selectedCollection, doc.document_id, doc.filename)}
                        disabled={loading}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}

                {documents.length === 0 && (
                  <div className="empty-state">No documents in this collection</div>
                )}
              </div>
            </>
          )}

          {!selectedCollection && (
            <div className="empty-state-large">
              Select a collection to view documents
            </div>
          )}
        </div>

        {/* Document Details */}
        <div className="db-details">
          {documentDetails && (
            <>
              <div className="details-header">
                <h3>Document Details</h3>
                <button
                  className="close-btn"
                  onClick={() => {
                    setDocumentDetails(null);
                    setSelectedDocument(null);
                  }}
                >
                  ✕
                </button>
              </div>

              <div className="details-info">
                <div className="info-row">
                  <span className="info-label">Filename:</span>
                  <span className="info-value">{documentDetails.filename}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Document ID:</span>
                  <span className="info-value">{documentDetails.document_id}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Collection:</span>
                  <span className="info-value">{documentDetails.collection}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Total Chunks:</span>
                  <span className="info-value">{documentDetails.num_chunks}</span>
                </div>
              </div>

              <div className="chunks-container">
                <h4>Chunks</h4>
                {documentDetails.chunks.map((chunk) => (
                  <div key={chunk.chunk_index} className="chunk-detail">
                    <div className="chunk-header">
                      <span className="chunk-number">Chunk #{chunk.chunk_index + 1}</span>
                      <span className="chunk-length">{chunk.text.length} chars</span>
                    </div>
                    <div className="chunk-text">{chunk.text}</div>
                  </div>
                ))}
              </div>
            </>
          )}

          {!documentDetails && (
            <div className="empty-state-large">
              Select a document to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DatabaseViewer;
