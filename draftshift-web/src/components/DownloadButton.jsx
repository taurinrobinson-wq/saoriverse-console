import React from 'react'

export default function DownloadButton({ result }) {
  const handleDownload = () => {
    try {
      // Decode base64 to bytes
      const binaryString = atob(result.data)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }

      // Create blob and download
      const blob = new Blob([bytes], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = result.filename || 'document.docx'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      console.error('Download failed:', err)
    }
  }

  return (
    <div className="download-button-container">
      <p className="success-message">✓ Document generated successfully!</p>
      <p className="file-info">{result.filename || 'document.docx'}</p>
      <button className="download-button" onClick={handleDownload}>
        Download DOCX
      </button>
    </div>
  )
}
