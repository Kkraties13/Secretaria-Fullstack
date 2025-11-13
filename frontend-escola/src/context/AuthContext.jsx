import React, { createContext, useState, useContext, useEffect } from 'react'
import { jwtDecode } from 'jwt-decode' // Importa o decoder
import api from '../services/api' // Importa o axios configurado

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem('authToken'))

  useEffect(() => {
    if (token) {
      try {
        const decodedToken = jwtDecode(token)
        // O ideal é que sua API JWT inclua o 'role' e 'name' no token
        setUser({
          id: decodedToken.user_id,
          username: decodedToken.username,
          role: decodedToken.role, // Ex: 'aluno' ou 'coordenador'
          name: decodedToken.name,
        })
        // Configura o token no cabeçalho do axios
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } catch (error) {
        console.error('Token inválido:', error)
        logout()
      }
    }
  }, [token])

  const login = async (username, password) => {
    try {
      // /api/token/ é a rota padrão do SimpleJWT
      const response = await api.post('/api/token/', {
        username,
        password,
      })

      const accessToken = response.data.access
      localStorage.setItem('authToken', accessToken)
      setToken(accessToken)
      
      // Decodifica para setar o usuário
      const decodedToken = jwtDecode(accessToken)
      setUser({
        id: decodedToken.user_id,
        username: decodedToken.username,
        role: decodedToken.role, // IMPORTANTE: Sua API precisa incluir isso no token!
        name: decodedToken.name,
      })

      return true // Sucesso
    } catch (error) {
      console.error('Falha no login:', error)
      return false // Falha
    }
  }

  const logout = () => {
    localStorage.removeItem('authToken')
    setUser(null)
    setToken(null)
    delete api.defaults.headers.common['Authorization']
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook customizado para facilitar o uso do contexto
export const useAuth = () => {
  return useContext(AuthContext)
}