import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [recommendations, setRecommendations] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

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

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const data = await response.json()
      setResult(data)

      // Once we have the track's id, fetch recommendations for it
      const recResponse = await fetch(`http://127.0.0.1:8000/recommendations/${data.id}`)
      const recData = await recResponse.json()
      setRecommendations(recData)

    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif' }}>
      <h1>AI DJ Assistant</h1>

      <input type="file" accept=".mp3,.wav" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? 'Analyzing...' : 'Analyze Track'}
      </button>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      {result && (
        <div style={{ marginTop: '20px' }}>
          <h2>Results</h2>
          <p>BPM: {result.bpm}</p>
          <p>Key: {result.key}</p>
          <p>Key Confidence: {result.key_confidence}</p>
          <p>Energy: {result.energy}</p>
          <p>Danceability: {result.danceability}</p>
        </div>
      )}

      {recommendations && recommendations.recommendations && (
        <div style={{ marginTop: '20px' }}>
          <h2>Recommended Next Tracks</h2>
          {recommendations.recommendations.length === 0 && (
            <p>No other tracks in your library yet — upload more to get recommendations.</p>
          )}
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
    </div>
  )
}

export default App