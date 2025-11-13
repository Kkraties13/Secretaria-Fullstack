import axios from 'axios'

// Cria uma instância do axios.
// Graças ao proxy no vite.config.js, não precisamos da URL base.
const api = axios.create()

// (O AuthContext vai configurar o cabeçalho de autorização aqui)

export default api