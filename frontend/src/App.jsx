import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import PredictionDashboard from './pages/PredictionDashboard'

export default function App() {
  const [page, setPage] = useState('graph')

  return (
    <>
      {page === 'graph' && <Dashboard onNavigate={setPage} />}
      {page === 'predictions' && <PredictionDashboard onNavigate={setPage} />}
    </>
  )
}
