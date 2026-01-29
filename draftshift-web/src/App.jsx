import { useState } from 'react'
import FixtureSelector from './components/FixtureSelector'
import JSONEditor from './components/JSONEditor'
import BuildButton from './components/BuildButton'
import DownloadButton from './components/DownloadButton'
import DraftShiftRenamer from './DraftShiftRenamer'
import './App.css'
import './DraftShiftRenamer.css'

function App() {
  const [activeTab, setActiveTab] = useState('build')
  const [jsonData, setJsonData] = useState({
    type: 'motion',
    title: 'MOTION FOR NEW TRIAL',
    body: ['Enter your motion text here.'],
    signature_block: ['Name', 'Title'],
  })
  const [buildResult, setBuildResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleLoadFixture = async (fixtureName) => {
    try {
      const response = await fetch(`/api/fixtures/${fixtureName}`)
      if (!response.ok) throw new Error('Failed to load fixture')
      const data = await response.json()
      setJsonData(data)
      setError(null)
    } catch (err) {
      setError(`Failed to load fixture: ${err.message}`)
    }
  }

  const handleBuild = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/build', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonData),
      })
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(errorText || 'Build failed')
      }
      const result = await response.json()
      setBuildResult(result)
    } catch (err) {
      setError(`Build error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>DraftShift</h1>
        <p>Automated Litigation Document Generator</p>
        
        <nav className="tab-nav">
          <button 
            className={`tab-btn ${activeTab === 'build' ? 'active' : ''}`}
            onClick={() => setActiveTab('build')}
          >
            📋 Document Builder
          </button>
          <button 
            className={`tab-btn ${activeTab === 'renamer' ? 'active' : ''}`}
            onClick={() => setActiveTab('renamer')}
          >
            📁 File Renamer
          </button>
        </nav>
      </header>

      {activeTab === 'build' && (
        <main className="app-main">
          <div className="sidebar">
            <section className="panel">
              <h2>Load Template</h2>
              <FixtureSelector onLoadFixture={handleLoadFixture} />
            </section>

            <section className="panel">
              <h2>Build Options</h2>
              <div className="pleading-type">
                <label htmlFor="type-select">Document Type:</label>
                <select
                  id="type-select"
                  value={jsonData.type}
                  onChange={(e) => setJsonData({ ...jsonData, type: e.target.value })}
                >
                  <option value="motion">Motion</option>
                  <option value="opposition">Opposition</option>
                  <option value="reply">Reply</option>
                  <option value="declaration">Declaration</option>
                </select>
              </div>
              <BuildButton onClick={handleBuild} loading={loading} />
            </section>

            {buildResult && (
              <section className="panel result-panel">
                <h2>Generated Document</h2>
                <DownloadButton result={buildResult} />
              </section>
            )}
          </div>

          <div className="editor-section">
            <JSONEditor value={jsonData} onChange={setJsonData} />
          </div>
        </main>
      )}

      {activeTab === 'renamer' && (
        <main className="app-main full-width">
          <DraftShiftRenamer />
        </main>
      )}

      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}
    </div>
  )
}

export default App
