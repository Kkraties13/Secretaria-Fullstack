import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './pages/Layout'
import LoginPage from './pages/LoginPage'
import StudentDashboard from './pages/StudentDashboard'
import CoordinatorDashboard from './pages/CoordinatorDashboard'
import ProtectedRoute from './components/ProtectedRoute'
import HomeDashboard from './pages/HomeDashboard'

// Constantes de Cargos (Roles)
const ROLES = {
  ALUNO: 'aluno',
  COORDENADOR: 'coordenador',
  PROFESSOR: 'professor',
}

function App() {
  return (
    <Routes>
      {/* Rota pública de Login */}
      <Route path="/login" element={<LoginPage />} />

      {/* Rotas Protegidas (dentro do Layout principal) */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* Rota principal (Hub) */}
        <Route index element={<HomeDashboard />} />

        {/* Rotas para Alunos */}
        <Route
          element={<ProtectedRoute allowedRoles={[ROLES.ALUNO]} />}
        >
          <Route path="aluno/dashboard" element={<StudentDashboard />} />
          {/* Outras rotas de aluno: /aluno/notas, /aluno/faltas, etc. */}
        </Route>

        {/* Rotas para Coordenadores */}
        <Route
          element={<ProtectedRoute allowedRoles={[ROLES.COORDENADOR]} />}
        >
          <Route path="coordenador/dashboard" element={<CoordinatorDashboard />} />
          {/* Outras rotas de coordenador: /coordenador/alunos, /coordenador/turmas, etc. */}
        </Route>

        {/* Adicione aqui rotas para PROFESSORES */}
        
      </Route>

      {/* Rota para "Não Encontrado" */}
      <Route path="*" element={<h1>404 - Página Não Encontrada</h1>} />
    </Routes>
  )
}

export default App