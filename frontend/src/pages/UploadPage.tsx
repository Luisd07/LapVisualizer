import { useState } from 'react'
import { useNavigate } from 'react-router'
import { uploadSession } from '../api/client'

/** Page 1: choose (or drop) an RMonitor log file and upload it. */
export function UploadPage() {
  const navigate = useNavigate()

  // Three pieces of state: the chosen file, an error message, a busy flag.
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  /** Shared by the file <input> (click) and the drop zone (drag-and-drop). */
  function chooseFile(files: FileList | null) {
    setFile(files?.[0] ?? null)
    setError(null)
  }

  async function handleUpload() {
    if (!file) return
    setBusy(true)
    setError(null)
    try {
      const session = await uploadSession(file)
      // On success, jump straight to the new session's dashboard.
      navigate(`/sessions/${session.session_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="upload">
      <div className="card">
        <h2>Upload a timing log</h2>
        <p className="sub">
          Add an RMonitor <code>.log</code> file to parse and analyse the session.
        </p>

        {/* The real <input type="file"> is hidden by CSS; this <label>
            forwards clicks to it and also accepts dropped files. */}
        <label
          className="file-pick"
          onDragOver={(event) => event.preventDefault()}
          onDrop={(event) => {
            event.preventDefault()
            chooseFile(event.dataTransfer.files)
          }}
        >
          <input type="file" onChange={(event) => chooseFile(event.target.files)} />
          {file ? (
            <span className="file-name">{file.name}</span>
          ) : (
            <>
              <strong>Choose a file</strong>
              <span>or drop it here</span>
            </>
          )}
        </label>

        <div className="upload-actions">
          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={!file || busy}
          >
            {busy ? 'Uploading…' : 'Upload & analyse'}
          </button>
          {error && (
            <p className="state-error" role="alert">
              {error}
            </p>
          )}
        </div>
      </div>
    </section>
  )
}
