import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ✅ 1. Health Check
export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

// ✅ 2. Autenticação JWT
export const login = async (credentials) => {
  const response = await api.post('/token', credentials)
  return response.data
}

// ✅ 3. Scanner de Segredos
export const scanSecrets = async (projectId) => {
  const response = await api.post('/secrets/scan', { project_id: projectId })
  return response.data
}

// ✅ 4. Análise de Terraform
export const scanTerraform = async (projectId) => {
  const response = await api.post('/terraform/scan', { project_id: projectId })
  return response.data
}

// ✅ 5. Relatórios Compliance
export const getComplianceReport = async () => {
  const response = await api.get('/compliance/report')
  return response.data
}

// ✅ 6. Detecção de Drift
export const checkDrift = async (projectId) => {
  const response = await api.post('/drift/check', { project_id: projectId })
  return response.data
}

// ✅ 7. Gestão de Projetos
export const getProjects = async () => {
  const response = await api.get('/projects')
  return response.data
}

export const createProject = async (projectData) => {
  const response = await api.post('/projects', projectData)
  return response.data
}

// ✅ 8. Gestão de Usuários
export const getUsers = async () => {
  const response = await api.get('/users')
  return response.data
}

// ✅ 9. Métricas de Uso
export const getMetrics = async () => {
  const response = await api.get('/metrics')
  return response.data
}

// ✅ 10. Informações de Faturamento
export const getBillingInfo = async () => {
  const response = await api.get('/billing')
  return response.data
}

// ✅ 11. Relatórios Avançados
export const getAdvancedReports = async () => {
  const response = await api.get('/reports/advanced')
  return response.data
}

// ✅ 12. Utilitário para verificar status da API
export const checkApiStatus = async () => {
  try {
    const response = await healthCheck()
    return { status: 'online', data: response }
  } catch (error) {
    return { status: 'offline', error: error.message }
  }
}

export default api
