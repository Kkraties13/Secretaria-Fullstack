import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate, useLocation } from 'react-router-dom'

const LoginPage = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  // Para onde redirecionar após o login
  const from = location.state?.from?.pathname || '/'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    const success = await login(username, password)

    if (success) {
      navigate(from, { replace: true })
    } else {
      setError('Usuário ou senha inválidos.')
    }
  }

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Portal Escolar</h1>
        <div>
          <label htmlFor="username">Usuário (Matrícula/CPF):</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="password">Senha:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        {error && <p className="error">{error}</p>}
        <button type="submit">Entrar</button>
      </form>
    </div>
  )
}

export default LoginPage