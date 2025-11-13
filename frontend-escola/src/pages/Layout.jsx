import React from 'react'
import { Outlet, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Layout = () => {
  const { user, logout } = useAuth()
  
  // Define quais links exibir baseado no cargo
  const getNavLinks = () => {
    if (user.role === 'aluno') {
      return (
        <>
          <li><Link to="/aluno/dashboard">Meu Dashboard</Link></li>
          <li><Link to="/aluno/notas">Minhas Notas</Link></li>
          <li><Link to="/aluno/faltas">Minhas Faltas</Link></li>
        </>
      )
    }
    if (user.role === 'coordenador') {
      return (
        <>
          <li><Link to="/coordenador/dashboard">Dashboard Coordenação</Link></li>
          <li><Link to="/coordenador/alunos">Gerenciar Alunos</Link></li>
          <li><Link to="/coordenador/turmas">Gerenciar Turmas</Link></li>
        </>
      )
    }
    // Adicione links para 'professor'
    return null
  }

  return (
    <div className="layout-container">
      <header className="header">
        <div className="header-title">Colégio XYZ</div>
        <div className="user-info">
          <span>Olá, {user?.name || user?.username}</span>
          <button onClick={logout} style={{ marginLeft: '1rem' }}>
            Sair
          </button>
        </div>
      </header>

      <aside className="sidebar">
        <h2>Navegação</h2>
        <nav>
          <ul>
            <li><Link to="/">Início</Link></li>
            {getNavLinks()}
          </ul>
        </nav>
      </aside>

      <main className="content">
        {/* As páginas (StudentDashboard, etc.) serão renderizadas aqui */}
        <Outlet />
      </main>
    </div>
  )
}

export default Layout