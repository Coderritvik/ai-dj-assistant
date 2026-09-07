import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [recommendations, setRecommendations] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // New state for folder/batch upload
  const [folderFiles, setFolderFiles] = useState([])
  const [batchResults, setBatchResults] = useState(null)
  const [batchLoading, setBatchLoading] = useState(false)

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

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif' }}>
      <h1>AI DJ Assistant</h1>

      <h2>Single Track</h2>
      <input type="file" accept=".mp3,.wav" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? 'Analyzing...' : 'Analyze Track'}
      </button>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {result && (
        <div style={{ marginTop: '20px' }}>
          <h3>Results</h3>
          <p>BPM: {result.bpm}</p>
          <p>Key: {result.key}</p>
          <p>Key Confidence: {result.key_confidence}</p>
          <p>Energy: {result.energy}</p>
          <p>Danceability: {result.danceability}</p>
        </div>
      )}

      {recommendations && recommendations.recommendations && (
        <div style={{ marginTop: '20px' }}>
          <h3>Recommended Next Tracks</h3>
          <ul>
            {recommendations.recommendations.map((track) => (
              <li key={track.id} style={{ marginBottom: '10px' }}>
                {track.harmonic_match ? '✓' : '✗'} {track.filename}
                <br />
                {track.bpm} BPM, {track.camelot} — score: {track.score}
              </li>
            ))}
          </ul>
        </div>
      )}

      <hr style={{ margin: '40px 0' }} />

      <h2>Upload a Folder of Tracks</h2>
      <input
        type="file"
        webkitdirectory="true"
        directory="true"
        multiple
        onChange={handleFolderChange}
      />
      <p>{folderFiles.length > 0 && `${folderFiles.length} files selected`}</p>
      <button onClick={handleFolderUpload} disabled={folderFiles.length === 0 || batchLoading}>
        {batchLoading ? `Analyzing ${folderFiles.length} tracks...` : 'Analyze Folder'}
      </button>

      {batchResults && (
        <div style={{ marginTop: '20px' }}>
          <h3>Batch Results ({batchResults.length} tracks)</h3>
          <ul>
            {batchResults.map((track, index) => (
              <li key={index} style={{ marginBottom: '10px' }}>
                {track.error ? (
                  <span style={{ color: 'red' }}>{track.filename} — failed: {track.error}</span>
                ) : (
                  <span>{track.filename} — {track.bpm} BPM, {track.key}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default App