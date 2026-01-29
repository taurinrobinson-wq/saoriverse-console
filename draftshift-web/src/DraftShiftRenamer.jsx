import React, { useState } from 'react';
import './DraftShiftRenamer.css';

const DraftShiftRenamer = () => {
  const [files, setFiles] = useState([]);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle file drop
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFiles = Array.from(e.dataTransfer.files);
    setFiles(droppedFiles);
    handlePreview(droppedFiles);
  };

  // Handle file selection
  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    handlePreview(selectedFiles);
  };

  // Preview renames
  const handlePreview = async (filesToPreview) => {
    setLoading(true);
    setError(null);

    const formData = new FormData();
    filesToPreview.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('/api/renamer/preview', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Preview failed');

      const data = await response.json();
      setPreview(data.preview);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Download renamed files
  const handleDownload = async () => {
    setLoading(true);
    setError(null);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('/api/renamer/rename-and-download', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Download failed');

      // Get the blob and create download link
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `renamed_files_${new Date().toISOString().slice(0, 10)}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      // Reset
      setFiles([]);
      setPreview(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="renamer-container">
      <div className="renamer-header">
        <h1>🔄 DraftShift Renamer</h1>
        <p>Batch rename litigation documents to litigation-grade format: YYMMDD – Slug</p>
      </div>

      {/* Upload Zone */}
      <div
        className={`upload-zone ${files.length > 0 ? 'has-files' : ''}`}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        <div className="upload-content">
          <div className="upload-icon">📁</div>
          <h2>Drag files here or click to select</h2>
          <p>Accepts: PDF, DOCX, DOC, TXT, JPG, PNG</p>
          <input
            type="file"
            multiple
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            id="file-input"
            accept=".pdf,.docx,.doc,.txt,.jpg,.png,.jpeg"
          />
          <label htmlFor="file-input" className="file-label">
            Choose Files
          </label>
        </div>
      </div>

      {/* File Count */}
      {files.length > 0 && (
        <div className="file-count">
          <p>{files.length} file{files.length !== 1 ? 's' : ''} selected</p>
          <button onClick={() => setFiles([])}>Clear</button>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="error-box">
          <p>⚠️ {error}</p>
        </div>
      )}

      {/* Preview Table */}
      {preview && (
        <div className="preview-section">
          <h3>Preview Renames</h3>
          <div className="preview-table">
            <div className="table-header">
              <div className="col-original">Original</div>
              <div className="col-renamed">Renamed To</div>
              <div className="col-date">Date Detected</div>
              <div className="col-confidence">Confidence</div>
            </div>

            {preview.map((item, idx) => (
              <div key={idx} className="table-row">
                <div className="col-original">
                  <code>{item.original}</code>
                </div>
                <div className="col-renamed">
                  {item.error ? (
                    <span className="error">Error: {item.error}</span>
                  ) : (
                    <code className="renamed">{item.renamed}</code>
                  )}
                </div>
                <div className="col-date">
                  {item.date_detected ? (
                    <small>{new Date(item.date_detected).toLocaleDateString()}</small>
                  ) : (
                    <small>-</small>
                  )}
                </div>
                <div className="col-confidence">
                  {item.confidence && (
                    <div className="confidence-bar">
                      <div
                        className="confidence-fill"
                        style={{ width: `${item.confidence * 100}%` }}
                      />
                      <span>{Math.round(item.confidence * 100)}%</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Download Button */}
          <div className="action-buttons">
            <button
              className="download-btn"
              onClick={handleDownload}
              disabled={loading}
            >
              {loading ? 'Processing...' : '⬇️ Download ZIP'}
            </button>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Processing files...</p>
        </div>
      )}

      {/* Info */}
      <div className="info-section">
        <h4>How It Works</h4>
        <ul>
          <li>✅ Drag or select files</li>
          <li>✅ AI detects dates and document types</li>
          <li>✅ Preview all renames</li>
          <li>✅ Download ZIP with renamed files</li>
        </ul>
      </div>
    </div>
  );
};

export default DraftShiftRenamer;
