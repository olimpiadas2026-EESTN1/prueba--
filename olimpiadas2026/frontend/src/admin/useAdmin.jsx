import { createContext, useContext, useState } from 'react';
import { API_URL } from '../api';
const Context = createContext(null);

export function AdminProvider({ children }) {
  const [session, setSession] = useState(null);
  async function request(path, options = {}) {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...(session ? { Authorization: `Bearer ${session.token}` } : {}) },
    });
    const data = await response.json();
    if (response.status === 401) setSession(null);
    if (!response.ok || data?.error) throw new Error(typeof data.detail === 'string' ? data.detail : 'No se pudo completar la operación. Revisá los datos.');
    return data;
  }
  async function login(email, password) {
    const data = await request('/admin/login', { method: 'POST', body: JSON.stringify({ email, password }) });
    setSession(data);
  }
  async function logout() {
    try { await request('/admin/logout', { method: 'POST' }); }
    finally { setSession(null); }
  }
  return <Context.Provider value={{ admin: session?.admin, login, logout, request }}>{children}</Context.Provider>;
}
export function useAdmin() {
  const context = useContext(Context);
  if (!context) throw new Error('useAdmin requiere AdminProvider');
  return context;
}
