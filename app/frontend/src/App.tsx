import { useState } from 'react'

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('dark')

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  return (
    <div className={theme}>
      <div className="min-h-screen bg-background text-foreground">
        <div className="flex">
          {/* Sidebar placeholder */}
          <div className="w-64 bg-muted/20 p-4 border-r border-r">
            <h1 className="text-2xl font-bold text-primary">Auto-Applier v2</h1>
            <div className="mt-4 space-y-2">
              <nav className="space-y-1">
                <a href="#" className="block p-2 rounded hover:bg-muted/50">Dashboard</a>
                <a href="#" className="block p-2 rounded hover:bg-muted/50">Jobs</a>
                <a href="#" className="block p-2 rounded hover:bg-muted/50">Run</a>
                <a href="#" className="block p-2 rounded hover:bg-muted/50">History</a>
                <a href="#" className="block p-2 rounded hover:bg-muted/50">Profile</a>
                <a href="#" className="block p-2 rounded hover:bg-muted/50">Settings</a>
              </nav>
            </div>
          </div>

          {/* Main content area */}
          <div className="flex-1 p-6">
            <div className="max-w-6xl mx-auto">
              <h2 className="text-3xl font-bold mb-6">Welcome to Auto-Applier v2</h2>

              <div className="bg-card border border rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Getting Started</h3>
                <div className="space-y-3">
                  <p className="text-muted-foreground">
                    v2 is under active development. The application structure has been scaffolded.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                    <div className="space-y-2">
                      <h4 className="font-medium text-primary">Backend</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                        <li>FastAPI server created</li>
                        <li>Database models scaffolded</li>
                        <li>API routes defined (profiles, jobs, runs, applications, settings, ws)</li>
                        <li>Settings management</li>
                      </ul>
                    </div>
                    <div className="space-y-2">
                      <h4 className="font-medium text-primary">Frontend</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                        <li>React + TypeScript + Vite</li>
                        <li>Tailwind CSS configured</li>
                        <li>App layout with sidebar</li>
                        <li>Routes structure created</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-900 rounded-lg">
                <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Next Steps</h4>
                <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
                  <li className="flex items-start gap-2">
                    <span className="font-mono bg-blue-100 dark:bg-blue-900 px-2 py-1 rounded text-blue-900 dark:text-blue-100">Phase 1</span>
                    <span>Backend Core: SQLAlchemy models, repository layer, ATS adapter</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-mono bg-blue-100 dark:bg-blue-900 px-2 py-1 rounded text-blue-900 dark:text-blue-100">Phase 2</span>
                    <span>Frontend Shell: Layout, routing, shadcn/ui</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="font-mono bg-blue-100 dark:bg-blue-900 px-2 py-1 rounded text-blue-900 dark:text-blue-100">Phase 3</span>
                    <span>API Client & WebSocket: Type-safe client + WS connection</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Theme toggle button */}
      <button
        onClick={toggleTheme}
        className="fixed bottom-4 right-4 p-2 rounded-full bg-primary text-primary-foreground hover:bg-primary/90"
        title="Toggle theme"
      >
        {theme === 'light' ? '🌙' : '☀️'}
      </button>
    </div>
  )
}

export default App
