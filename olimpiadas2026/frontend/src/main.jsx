import { StrictMode } from 'react'
import { AuthProvider } from './AuthContext.jsx'
import { createRoot } from 'react-dom/client'
import { BrowserRouter} from 'react-router-dom'
import './index.css'
import App_header from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
    <AuthProvider>
        <App_header />
    </AuthProvider>
       
    </BrowserRouter>
  </StrictMode>,
)
