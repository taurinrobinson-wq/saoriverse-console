import React from 'react'

export default function FixtureSelector({ onLoadFixture }) {
  const fixtures = ['motion', 'opposition', 'reply', 'declaration']

  return (
    <div className="fixture-selector">
      {fixtures.map((fixture) => (
        <button
          key={fixture}
          className="fixture-btn"
          onClick={() => onLoadFixture(fixture)}
        >
          Load {fixture.charAt(0).toUpperCase() + fixture.slice(1)}
        </button>
      ))}
    </div>
  )
}
