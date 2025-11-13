import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const HomeDashboard = () => {
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    // Redireciona o usuário para o dashboard do seu cargo
    if (user.role === 'aluno') {
      navigate('/aluno/dashboard')
    } else if (user.role === 'coordenador') {
      navigate('/coordenador/dashboard')
    } else if (user.role === 'professor') {
      navigate('/professor/dashboard') // (Crie esta rota)
    }
  }, [user, navigate])

  // Exibe um "Carregando..." enquanto redireciona
  return <div>Carregando seu dashboard...</div>
}

export default HomeDashboard