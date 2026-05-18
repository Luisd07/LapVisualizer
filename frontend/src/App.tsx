import { NavLink, Route, Routes } from 'react-router'
import { SessionPage } from './pages/SessionPage'
import { SessionsPage } from './pages/SessionsPage'
import { UploadPage } from './pages/UploadPage'

/**
 * The app shell: a sticky header shown on every page, plus the route table.
 * <Routes> renders whichever single <Route> matches the current URL.
 */
function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1 className="wordmark">
          <span className="wordmark-mark" aria-hidden="true" />
          LapVisualizer
        </h1>
        <nav className="app-nav">
          {/* `end` makes "/" match only the exact path, not every route. */}
          <NavLink to="/" end>
            Upload
          </NavLink>
          <NavLink to="/sessions">Sessions</NavLink>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/sessions" element={<SessionsPage />} />
          {/* `:sessionId` is a URL parameter — read with useParams(). */}
          <Route path="/sessions/:sessionId" element={<SessionPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
