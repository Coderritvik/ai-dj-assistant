import { useState } from 'react'
import './App.css'

function EnergyBar({ value }) {
  const pct = Math.min(100, (value / 0.5) * 100)
  return (
    <span className="energy-bar">
      <span className="energy-bar-fill" style={{ width: `${pct}%` }} />
    </span>
  )
}

function Stars({ rating }) {
  return (
    <span className="stars">
      {[1, 2, 3, 4, 5].map((n) => (
        <span key={n} className={n <= rating ? 'star filled' : 'star'}>★</span>
      ))}
    </span>
  )
}

function App() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [recommendations, setRecommendations] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [folderFiles, setFolderFiles] = useState([])
  const [batchResults, setBatchResults] = useState(null)
  const [batchLoading, setBatchLoading] = useState(false)

  const [setContext, setSetContext] = useState('peak')
  const [setCount, setSetCount] = useState(20)
  const [generatedSet, setGeneratedSet] = useState(null)
  const [isBuildingSet, setIsBuildingSet] = useState(false)

  const handleFileChange = (event) => {
    setFile(event.target.files[0])
    setResult(null)
    setRecommendations(null)
    setError(null)
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://127.0.0.1:8000/analyze', {
        method: 'POST',
        body: formData,
      })
      if (!response.ok) throw new Error('Analysis failed')
      const data = await response.json()
      setResult(data)

      const recResponse = await fetch(`http://127.0.0.1:8000/recommendations/${data.id}`)
      const recData = await recResponse.json()
      setRecommendations(recData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleFolderChange = (event) => {
    setFolderFiles(Array.from(event.target.files))
    setBatchResults(null)
  }

  const handleFolderUpload = async () => {
    if (folderFiles.length === 0) return
    setBatchLoading(true)

    const formData = new FormData()
    folderFiles.forEach((f) => {
      formData.append('files', f)
    })

    try {
      const response = await fetch('http://127.0.0.1:8000/analyze-folder', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      setBatchResults(data.analyzed)
    } catch (err) {
      console.error(err)
    } finally {
      setBatchLoading(false)
    }
  }

  const handleGenerateSet = async () => {
    setIsBuildingSet(true)
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/generate-set?context=${setContext}&count=${setCount}`
      )
      const data = await response.json()
      setGeneratedSet(data)
    } catch (err) {
      console.error(err)
    } finally {
      setIsBuildingSet(false)
    }
  }

  const handleExportSet = () => {
    window.location.href = `http://127.0.0.1:8000/export-set?context=${setContext}&count=${setCount}`
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">AI DJ Assistant</h1>
        <p className="app-subtitle">bpm · key · energy · harmonic mixing</p>
      </header>

      <section className="section">
        <h2 className="section-heading">Analyze a track</h2>

        <div className="control-row">
          <input className="file-input" type="file" accept=".mp3,.wav" onChange={handleFileChange} />
          <button className="btn" onClick={handleUpload} disabled={!file || loading}>
            {loading ? 'Analyzing…' : 'Analyze'}
          </button>
        </div>

        {error && <p className="error-text">{error}</p>}

        {result && (
          <div className="readout">
            <div className="readout-grid">
              <div className="readout-item">
                <span className="readout-label">bpm</span>
                <span className="readout-value accent">{result.bpm}</span>
              </div>
              <div className="readout-item">
                <span className="readout-label">key</span>
                <span className="readout-value">
                  {result.key}{result.camelot ? ` · ${result.camelot}` : ''}
                </span>
              </div>
              <div className="readout-item">
                <span className="readout-label">key confidence</span>
                <Stars rating={result.key_confidence_rating} />
              </div>
              <div className="readout-item">
                <span className="readout-label">energy</span>
                <Stars rating={result.energy_rating} />
              </div>
              <div className="readout-item">
                <span className="readout-label">danceability</span>
                <Stars rating={result.danceability_rating} />
              </div>
            </div>
          </div>
        )}

        {recommendations && recommendations.recommendations && (
          <>
            <p className="section-note">recommended next — from {recommendations.target_track}</p>
            <ul className="track-list">
              {recommendations.recommendations.map((track) => (
                <li className="track-row" key={track.id}>
                  <span className={`match-dot ${track.harmonic_match ? 'compatible' : ''}`} />
                  <div className="track-main">
                    <div className="track-name">{track.filename}</div>
                    <div className="track-meta">
                      <span>{track.bpm} bpm</span>
                      <span>{track.camelot}</span>
                      <span>score {track.score}</span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      <section className="section">
        <h2 className="section-heading">Analyze a library</h2>

        <div className="control-row">
          <input
            className="file-input"
            type="file"
            webkitdirectory="true"
            directory="true"
            multiple
            onChange={handleFolderChange}
          />
          <button className="btn" onClick={handleFolderUpload} disabled={folderFiles.length === 0 || batchLoading}>
            {batchLoading ? `Analyzing ${folderFiles.length}…` : 'Analyze folder'}
          </button>
        </div>

        {folderFiles.length > 0 && (
          <p className="section-note">{folderFiles.length} files selected</p>
        )}

        {batchResults && (
          <>
            <p className="section-note">{batchResults.length} tracks analyzed</p>
            <ul className="track-list">
              {batchResults.map((track, index) => (
                <li className="track-row" key={index}>
                  <div className="track-main">
                    {track.error ? (
                      <div className="track-name track-error">{track.filename} — {track.error}</div>
                    ) : (
                      <>
                        <div className="track-name">{track.filename}</div>
                        <div className="track-meta">
                          <span>{track.bpm} bpm</span>
                          <span>
                            {track.key}{track.camelot ? ` · ${track.camelot}` : ''}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      <section className="section">
        <h2 className="section-heading">Build a set</h2>

        <div className="control-row">
          <label className="field-label">
            type
            <select className="select" value={setContext} onChange={(e) => setSetContext(e.target.value)}>
              <option value="opening">Opening</option>
              <option value="peak">Peak time</option>
              <option value="closing">Closing</option>
            </select>
          </label>

          <label className="field-label">
            tracks
            <input
              className="number-input"
              type="number"
              value={setCount}
              onChange={(e) => setSetCount(e.target.value)}
            />
          </label>

          <button className="btn" onClick={handleGenerateSet} disabled={isBuildingSet}>
            {isBuildingSet ? 'Building…' : 'Generate set'}
          </button>

          <button className="btn" onClick={handleExportSet} disabled={!generatedSet}>
            Download for Rekordbox
          </button>
        </div>

        {generatedSet && generatedSet.set && (
          <>
            <p className="section-note">
              {generatedSet.context} · {generatedSet.track_count} tracks
            </p>
            <ol className="track-list">
              {generatedSet.set.map((track, i) => (
                <li className="track-row" key={track.id}>
                  <span className="track-index">{i + 1}</span>
                  <div className="track-main">
                    <div className="track-name">{track.filename}</div>
                    <div className="track-meta">
                      <span>{track.bpm} bpm</span>
                      <span>
                        {track.key}{track.camelot ? ` · ${track.camelot}` : ''}
                      </span>
                      <EnergyBar value={track.energy} />
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </>
        )}
      </section>
    </div>
  )
}

export default App