import React from 'react'

export default function JSONEditor({ value, onChange }) {
  const handleChange = (e) => {
    try {
      const parsed = JSON.parse(e.target.value)
      onChange(parsed)
    } catch (err) {
      // Allow invalid JSON while user is typing
    }
  }

  return (
    <div className="json-editor">
      <h2>JSON Configuration</h2>
      <textarea
        className="json-textarea"
        value={JSON.stringify(value, null, 2)}
        onChange={handleChange}
        spellCheck="false"
      />
      <p className="json-hint">Edit JSON to customize your document. Valid JSON required for build.</p>
    </div>
  )
}
