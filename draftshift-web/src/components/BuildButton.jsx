import React from 'react'

export default function BuildButton({ onClick, loading }) {
  return (
    <button
      className={`build-button ${loading ? 'loading' : ''}`}
      onClick={onClick}
      disabled={loading}
    >
      {loading ? 'Building...' : 'Build Document'}
    </button>
  )
}
