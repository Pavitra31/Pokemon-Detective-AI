
import { useEffect, useRef, useState } from 'react'
import './App.css'
import PikachuDetective from './PikachuDetective'

const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000').replace(/\/$/, '')
const MAX_FILE_SIZE = 10 * 1024 * 1024
const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']

const EXTENSION_BY_TYPE = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
  'image/webp': 'webp',
  'image/gif': 'gif',
}

function App() {
  const fileInputRef = useRef(null)
  const [selectedImage, setSelectedImage] = useState('')
  const [result, setResult] = useState(null)
  const [pokemonDetails, setPokemonDetails] = useState(null)
  const [loading, setLoading] = useState(false)
  const [detailsLoading, setDetailsLoading] = useState(false)
  const [error, setError] = useState('')
  const [detailsMessage, setDetailsMessage] = useState('')
  const [isDragOver, setIsDragOver] = useState(false)
  const [theme, setTheme] = useState('dark')

  useEffect(() => {
    return () => {
      if (selectedImage.startsWith('blob:')) {
        URL.revokeObjectURL(selectedImage)
      }
    }
  }, [selectedImage])

  async function investigateImage(file) {
    if (!file) return

    const fileType = (file.type || '').toLowerCase()

    if (!ACCEPTED_TYPES.includes(fileType)) {
      setError('Please use a JPG, PNG, WEBP, or GIF image.')
      return
    }

    if (file.size > MAX_FILE_SIZE) {
      setError('The image must be smaller than 10 MB.')
      return
    }

    const previewUrl = URL.createObjectURL(file)

    setSelectedImage(previewUrl)
    setResult(null)
    setPokemonDetails(null)
    setError('')
    setDetailsMessage('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('image', file)

      const response = await fetch(`${API_URL}/api/predict`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Prediction failed.')
      }

      if (!data.pokemon) {
        throw new Error('The API did not return a Pokémon name.')
      }

      setResult(data)
      setDetailsLoading(true)

      try {
        const detailsResponse = await fetch(
          `${API_URL}/api/pokemon/${encodeURIComponent(data.pokemon)}`
        )

        const details = await detailsResponse.json().catch(() => ({}))

        if (!detailsResponse.ok) {
          throw new Error(
            details.error || 'Pokédex details are unavailable.'
          )
        }

        setPokemonDetails(details)
      } catch (detailsError) {
        setDetailsMessage(
          detailsError.message || 'Could not load Pokédex details.'
        )
      } finally {
        setDetailsLoading(false)
      }
    } catch (requestError) {
      setError(
        requestError.message ||
          'Cannot reach the detective server. Check that Flask is running.'
      )
    } finally {
      setLoading(false)
    }
  }

  async function imageUrlToFile(url) {
    let response

    try {
      response = await fetch(url, {
        mode: 'cors',
        credentials: 'omit',
        redirect: 'follow',
      })
    } catch {
      throw new Error(
        'The image website blocked access (CORS). Open the image itself in a new tab and try dragging it, or download the image and upload it.'
      )
    }

    if (!response.ok) {
      throw new Error(
        `The image server returned ${response.status}. Try opening the image itself in a new tab, or download and upload it.`
      )
    }

    const blob = await response.blob()
    const type = (blob.type || '').split(';')[0].toLowerCase()

    if (!type.startsWith('image/')) {
      throw new Error(
        'The dragged item is a webpage, not an image file. Open the image itself in a new tab or download it first.'
      )
    }

    if (!ACCEPTED_TYPES.includes(type)) {
      throw new Error('Please use a JPG, PNG, WEBP, or GIF image.')
    }

    if (blob.size > MAX_FILE_SIZE) {
      throw new Error('The image must be smaller than 10 MB.')
    }

    return new File(
      [blob],
      `dragged-image.${EXTENSION_BY_TYPE[type]}`,
      {
        type,
        lastModified: Date.now(),
      }
    )
  }

  function handleDragOver(event) {
    event.preventDefault()

    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'copy'
    }

    setIsDragOver(true)
  }

  function handleDragLeave(event) {
    if (!event.currentTarget.contains(event.relatedTarget)) {
      setIsDragOver(false)
    }
  }

  function getDroppedImageUrl(transfer) {
    const candidates = []

    const add = (value) => {
      if (typeof value === 'string' && value.trim()) {
        candidates.push(value.trim())
      }
    }

    add(transfer.getData('text/uri-list'))
    add(transfer.getData('text/x-moz-url-data'))
    add(transfer.getData('text/plain'))

    const html = transfer.getData('text/html')

    if (html) {
      try {
        const doc = new DOMParser().parseFromString(html, 'text/html')
        const img = doc.querySelector('img')

        add(img?.currentSrc)
        add(img?.src)
        add(img?.getAttribute('src'))
        add(img?.getAttribute('data-src'))
      } catch {
        // Ignore malformed HTML drag data.
      }
    }

    for (const value of candidates) {
      const firstLine = value
        .split(/\r?\n/)
        .map((line) => line.trim())
        .find((line) => line && !line.startsWith('#'))

      if (!firstLine) continue

      const possibleUrl = firstLine.match(
        /https?:\/\/[^\s"'<>]+/i
      )?.[0]

      if (possibleUrl) return possibleUrl
    }

    return ''
  }

  async function handleDrop(event) {
    event.preventDefault()
    setIsDragOver(false)
    setError('')

    const transfer = event.dataTransfer

    if (!transfer) {
      setError('Could not read the dropped item. Try uploading the image file.')
      return
    }

    const files = Array.from(transfer.files || [])

    const droppedFile = files.find((file) =>
      ACCEPTED_TYPES.includes((file.type || '').toLowerCase())
    )

    if (droppedFile) {
      await investigateImage(droppedFile)
      return
    }

    const candidate = getDroppedImageUrl(transfer)

    if (!candidate) {
      setError(
        'The browser did not provide an image URL or file. Try opening the image itself in a new tab, or download it and upload it.'
      )
      return
    }

    setLoading(true)

    try {
      const file = await imageUrlToFile(candidate)
      await investigateImage(file)
    } catch (dropError) {
      setError(
        dropError.message ||
          'Could not import this image. Download it and upload the file instead.'
      )
    } finally {
      setLoading(false)
    }
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0]

    if (file) {
      void investigateImage(file)
    }

    event.target.value = ''
  }

  function scrollToPokedex() {
    document.getElementById('pokedex-profile')?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })
  }

  const pikachuPose = loading && !result
    ? 'investigating'
    : result
      ? 'success'
      : 'idle'

  const pokemonName =
    pokemonDetails?.name ||
    pokemonDetails?.pokemon ||
    result?.pokemon ||
    'Unknown Pokémon'

  const types = pokemonDetails?.types || []
  const abilities = pokemonDetails?.abilities || []
  const stats = pokemonDetails?.stats || []

  const artwork =
    pokemonDetails?.image ||
    pokemonDetails?.sprite ||
    pokemonDetails?.sprites?.front_default ||
    ''

  return (
    <main
      className={`detective-app ${
        theme === 'light' ? 'theme-light' : ''
      }`}
    >
      <div className="app-shell">
        <header className="topbar">
          <a
            className="brand"
            href="#home"
            aria-label="Pokémon Detective AI home"
          >
            <span className="brand-mark">⌕</span>
            <span>
              POKÉMON <strong>DETECTIVE AI</strong>
            </span>
          </a>

          <nav className="top-navigation" aria-label="Main navigation">
            <a href="#home">Home</a>

            <button type="button" onClick={scrollToPokedex}>
              Pokédex Profile
            </button>
          </nav>

          <div className="header-actions">
            <button
              className="theme-toggle"
              type="button"
              role="switch"
              aria-checked={theme === 'light'}
              aria-label="Toggle light and dark theme"
              onClick={() =>
                setTheme((current) =>
                  current === 'dark' ? 'light' : 'dark'
                )
              }
            >
              <span className="sun">☀</span>

              <span className="theme-track">
                <span className="theme-knob" />
              </span>

              <span className="moon">☾</span>
            </button>

            <span className="system-status">
              <span className="status-dot" />
              AI SYSTEM ONLINE
            </span>
          </div>
        </header>

        <section className="hero-section" id="home">
          <div className="hero-copy">
            <p className="eyebrow">
              THE POKÉDEX INVESTIGATION BUREAU
            </p>

            <h1>
              Every Pokémon leaves a <span>clue.</span>
            </h1>

            <p className="hero-description">
              Found an unfamiliar Pokémon? Upload the evidence. Let our AI
              detective identify your discovery.
            </p>

            <p className="case-status">
              <span className="status-dot" />
              CASE FILE #001 —{' '}
              {loading ? 'INVESTIGATING' : 'READY FOR INVESTIGATION'}
            </p>

            <button
              className="primary-button"
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
            >
              {loading
                ? 'INVESTIGATING…'
                : '⌕ INVESTIGATE A POKÉMON'}
            </button>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              hidden
              onChange={handleFileChange}
            />

            <p className="file-hint">
              JPG · PNG · WEBP · GIF · MAXIMUM 10 MB
            </p>
          </div>

          <div className="mascot-zone">
            <PikachuDetective pose={pikachuPose} />

            {/* <p className="mascot-caption">
              {loading
                ? 'ON THE CASE…'
                : result
                  ? 'CASE SOLVED!'
                  : 'READY, DETECTIVE?'}
            </p> */}
          </div>

          <div
            className={`evidence-zone ${
              isDragOver ? 'drag-over' : ''
            } ${loading ? 'is-scanning' : ''}`}
            onDragEnter={handleDragOver}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="evidence-card">
              <div className="evidence-heading">
                <span>EVIDENCE ANALYSIS</span>
                <span className="live-indicator">● LIVE</span>
              </div>

              <div className="evidence-image">
                {selectedImage ? (
                  <img
                    src={selectedImage}
                    alt="Uploaded Pokémon evidence"
                  />
                ) : (
                  <div className="upload-placeholder">
                    <span className="upload-icon">⌁</span>
                    <strong>Drop your evidence here</strong>
                    <span>or click Investigate a Pokémon</span>
                    <span className="placeholder-formats">
                      JPG · PNG · WEBP · GIF
                    </span>
                  </div>
                )}

                {isDragOver && (
                  <div className="drop-overlay">
                    DROP IMAGE TO INVESTIGATE
                  </div>
                )}
              </div>

              <div className="evidence-footer">
                <span>VISUAL RECOGNITION</span>
                <span>
                  {loading
                    ? 'ANALYZING'
                    : result
                      ? 'COMPLETE'
                      : 'STANDBY'}
                </span>
              </div>

              {error && (
                <p className="error-message" role="alert">
                  {error}
                </p>
              )}

              {loading && (
                <p className="loading-message">
                  Examining evidence and identifying Pokémon…
                </p>
              )}

              {result && (
                <div className="prediction-result" aria-live="polite">
                  <p className="eyebrow">IDENTIFICATION RESULT</p>
                  <h2>{result.pokemon}</h2>

                  {result.confidence !== undefined && (
                    <p>
                      Confidence:{' '}
                      {(
                        Number(result.confidence) *
                        (Number(result.confidence) <= 1 ? 100 : 1)
                      ).toFixed(1)}
                      %
                    </p>
                  )}

                  {result.dominant_color && (
                    <p>
                      Dominant color: {String(result.dominant_color)}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="pokedex-section" id="pokedex-profile">
          <div className="section-heading">
            <p className="eyebrow">CASE FILE DETAILS</p>
            <h2>Pokédex Profile</h2>
            <p>Everything the evidence reveals about your discovery.</p>
          </div>

          {!result && (
            <div className="pokedex-empty">
              <p>
                Your Pokédex profile will appear here after identification.
              </p>
            </div>
          )}

          {result && (
            <article className="pokedex-card">
              <div className="pokemon-artwork">
                {artwork ? (
                  <img src={artwork} alt={pokemonName} />
                ) : (
                  <div className="artwork-placeholder">
                    {detailsLoading
                      ? 'Loading artwork…'
                      : 'Artwork unavailable'}
                  </div>
                )}
              </div>

              <div className="pokemon-information">
                <p className="eyebrow">IDENTIFIED POKÉMON</p>
                <h3>{pokemonName}</h3>

                {types.length > 0 && (
                  <div className="pokemon-types">
                    {types.map((type, index) => {
                      const typeName =
                        typeof type === 'string' ? type : type?.name

                      return (
                        <span
                          className="type-badge"
                          key={`${typeName || 'type'}-${index}`}
                        >
                          {typeName || 'Unknown'}
                        </span>
                      )
                    })}
                  </div>
                )}

                {detailsLoading && <p>Loading Pokédex details…</p>}

                {detailsMessage && (
                  <p className="error-message">{detailsMessage}</p>
                )}

                {(pokemonDetails?.height !== undefined ||
                  pokemonDetails?.weight !== undefined) && (
                  <div className="physical-details">
                    {pokemonDetails.height !== undefined && (
                      <div>
                        <span>HEIGHT</span>
                        <strong>{pokemonDetails.height} m</strong>
                      </div>
                    )}

                    {pokemonDetails.weight !== undefined && (
                      <div>
                        <span>WEIGHT</span>
                        <strong>{pokemonDetails.weight} kg</strong>
                      </div>
                    )}
                  </div>
                )}

                {abilities.length > 0 && (
                  <div className="detail-group">
                    <h4>Abilities</h4>

                    <div className="abilities-list">
                      {abilities.map((ability, index) => {
                        const abilityName =
                          typeof ability === 'string'
                            ? ability
                            : ability?.name

                        return (
                          <span
                            key={`${abilityName || 'ability'}-${index}`}
                          >
                            {abilityName || 'Unknown'}
                          </span>
                        )
                      })}
                    </div>
                  </div>
                )}

                {stats.length > 0 && (
                  <div className="detail-group">
                    <h4>Base Stats</h4>

                    <div className="stats-list">
                      {stats.map((stat, index) => {
                        const statName =
                          stat.name ||
                          stat.stat?.name ||
                          `Stat ${index + 1}`

                        const statValue =
                          stat.value ??
                          stat.base_stat ??
                          stat.baseStat ??
                          0

                        const percentage = Math.min(
                          100,
                          (Number(statValue) / 255) * 100
                        )

                        return (
                          <div
                            className="stat-row"
                            key={`${statName}-${index}`}
                          >
                            <span>
                              {statName.replaceAll('-', ' ')}
                            </span>

                            <div className="stat-bar">
                              <span
                                style={{ width: `${percentage}%` }}
                              />
                            </div>

                            <strong>{statValue}</strong>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}

                {pokemonDetails?.url && (
                  <a
                    className="pokedex-link"
                    href={pokemonDetails.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View Pokédex entry ↗
                  </a>
                )}
              </div>
            </article>
          )}
        </section>

        <footer className="app-footer">
          <span>POKÉMON DETECTIVE AI</span>
          <span>EVERY IMAGE TELLS A STORY.</span>
        </footer>
      </div>
    </main>
  )
}

export default App
