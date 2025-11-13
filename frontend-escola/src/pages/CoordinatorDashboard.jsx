import React from 'react'
import { useAuth } from '../context/AuthContext'

const CoordinatorDashboard = () => {
  const { user } = useAuth()

  return (
    <div>
      <h1>Dashboard do Coordenador</h1>
      <p>Bem-vindo, Coordenador(a) {user.name}!</p>
      <p>Aqui você pode gerenciar alunos, turmas e professores.</p>

      {/* Aqui você faria chamadas de API para:
        - Listar Alunos (/api/alunos/)
        - Listar Turmas (/api/turmas/)
      */}
    </div>
  )
}

export default CoordinatorDashboard