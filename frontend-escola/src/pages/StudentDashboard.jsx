import React, { useState, useEffect } from 'react'
import api from '../services/api' // Nosso axios configurado
import { useAuth } from '../context/AuthContext'

const StudentDashboard = () => {
  const { user } = useAuth()
  const [boletim, setBoletim] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchBoletim = async () => {
      try {
        setLoading(true)
        // A API precisa ter uma rota como /api/boletim/ (que pega o aluno pelo token)
        // ou /api/alunos/{user.id}/boletim/
        const response = await api.get(`/api/boletim/`) 
        setBoletim(response.data)
      } catch (err) {
        setError('Não foi possível carregar seu boletim.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchBoletim()
  }, [user.id])

  if (loading) return <div>Carregando informações...</div>
  if (error) return <div style={{ color: 'red' }}>{error}</div>

  return (
    <div>
      <h1>Dashboard do Aluno</h1>
      <p>Bem-vindo, {user.name}!</p>
      
      <h2>Meu Boletim (Exemplo)</h2>
      {boletim ? (
        <ul>
          {/* Isso é um exemplo, ajuste à estrutura da sua API */}
          {boletim.notas.map((nota) => (
            <li key={nota.materia_id}>
              <strong>{nota.materia_nome}:</strong> {nota.nota_final}
            </li>
          ))}
        </ul>
      ) : (
        <p>Nenhuma nota encontrada.</p>
      )}

      <h2>Minhas Faltas</h2>
      <p>Total de faltas: {boletim?.total_faltas || 0}</p>
    </div>
  )
}

export default StudentDashboard