import React, { useState, useEffect } from 'react';
import { queryDocuments, getCollections } from '../api';
import './QueryInterface.css';

const QueryInterface = () => {
  const [query, setQuery] = useState('');
  const [numResults, setNumResults] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('default');

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await queryDocuments(query, numResults, selectedCollection);
      setResult(response);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="query-interface-container">
      <h2>Query Documents</h2>
      
      <form onSubmit={handleSubmit} className="query-form">
        <div className="form-group">
          <label htmlFor="query">Your Question:</label>
          <textarea
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about your uploaded documents..."
            rows="4"
            disabled={loading}
          />
        </div>

        <div className="form-row">
          <div className="form-group-small">
            <label htmlFor="collection">Collection:</label>
            <select
              id="collection"
              value={selectedCollection}
              onChange={(e) => setSelectedCollection(e.target.value)}
              disabled={loading}
            >
              {collections.map(coll => (
                <option key={coll} value={coll}>{coll}</option>
              ))}
            </select>
          </div>

          <div className="form-group-small">
            <label htmlFor="numResults">Number of Sources:</label>
            <select
              id="numResults"
              value={numResults}
              onChange={(e) => setNumResults(parseInt(e.target.value))}
              disabled={loading}
            >
              <option value="3">3</option>
              <option value="5">5</option>
              <option value="7">7</option>
              <option value="10">10</option>
            </select>
          </div>

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? (
              <>
                <span className="button-spinner"></span>
                Processing...
              </>
            ) : (
              'Ask Question'
            )}
          </button>
        </div>
      </form>

      {result && (
        <div className="result-container">
          <div className="stats-bar">
            <div className="stat-item">
              <span className="stat-label">Collection:</span>
              <span className="stat-value-small">{result.collection_used}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Chunks in DB:</span>
              <span className="stat-value">{result.total_chunks_in_db}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Chunks Used:</span>
              <span className="stat-value">{result.chunks_used}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Relevance:</span>
              <span className="stat-value">
                {result.total_chunks_in_db > 0 
                  ? `${((result.chunks_used / result.total_chunks_in_db) * 100).toFixed(1)}%`
                  : 'N/A'}
              </span>
            </div>
          </div>

          <div className="answer-section">
            <h3>Answer:</h3>
            <div className="answer-text">{result.answer}</div>
          </div>

          {result.source_metadata && result.source_metadata.length > 0 && (
            <div className="sources-section">
              <h3>Sources Used ({result.chunks_used} of {result.total_chunks_in_db} chunks):</h3>
              <div className="sources-list">
                {result.source_metadata.map((source, index) => (
                  <div key={index} className="source-item">
                    <div className="source-header">
                      <span className="source-number">Chunk {source.chunk_number}</span>
                      <span className="source-file">📄 {source.filename}</span>
                      <span className="source-similarity">
                        Score: {source.similarity_score.toFixed(4)}
                      </span>
                    </div>
                    <div className="source-meta">
                      Document ID: {source.document_id.substring(0, 8)}... | 
                      Chunk Index: {source.chunk_index}
                    </div>
                    <div className="source-text">{source.text}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="query-error">
          <h3>✗ Error</h3>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default QueryInterface;
