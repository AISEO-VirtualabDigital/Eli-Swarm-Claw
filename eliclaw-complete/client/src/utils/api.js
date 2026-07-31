const API_BASE = '/api'

export const api = {
  async get(endpoint, token) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
    return res.json()
  },

  async post(endpoint, data, token) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify(data)
    })
    return res.json()
  },

  async delete(endpoint, token) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'DELETE',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
    return res.json()
  }
}