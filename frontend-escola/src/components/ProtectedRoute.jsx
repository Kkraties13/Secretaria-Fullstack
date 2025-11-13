import React from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/**
 * Rota protegida.
 * Se `allowedRoles` for passado, verifica se o usuário tem um desses cargos.
 * Se não, apenas verifica se o usuário está logado.
 */
const ProtectedRoute = ({ allowedRoles }) => {
  const { user } = useAuth()
  const location = useLocation()

  // 1. O usuário está logado?
  if (!user) {
    // Redireciona para o login, guardando a página que ele tentou acessar
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // 2. A rota exige um cargo específico?
  if (allowedRoles) {
    // O usuário tem o cargo permitido?
    const hasRole = allowedRoles.includes(user.role)
    if (!hasRole) {
      // Usuário logado, mas sem permissão
      return <Navigate to="/nao-autorizado" replace /> // (Você pode criar essa página)
    }
  }

  // Se passou em tudo, renderiza a página filha (ex: <StudentDashboard />)
  return <Outlet />
}

export default ProtectedRoute