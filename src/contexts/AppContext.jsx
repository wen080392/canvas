import React, { createContext, useContext, useReducer, useEffect } from 'react'
import * as api from '@/services/api'

const AppContext = createContext()

const initialState = {
  // Dados da API
  projects: [],
  metrics: {},
  compliance: {},
  users: [],
  billing: {},
  advancedReports: [],
  
  // Estado da aplicação
  loading: false,
  error: null,
  apiStatus: 'checking'
}

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_API_STATUS':
      return { ...state, apiStatus: action.payload }
    case 'SET_PROJECTS':
      return { ...state, projects: action.payload }
    case 'SET_METRICS':
      return { ...state, metrics: action.payload }
    case 'SET_COMPLIANCE':
      return { ...state, compliance: action.payload }
    case 'SET_USERS':
      return { ...state, users: action.payload }
    case 'SET_BILLING':
      return { ...state, billing: action.payload }
    case 'SET_ADVANCED_REPORTS':
      return { ...state, advancedReports: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    default:
      return state
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState)

  // Verificar status da API ao inicializar
  useEffect(() => {
    checkApiConnection()
    loadInitialData()
  }, [])

  const checkApiConnection = async () => {
    const status = await api.checkApiStatus()
    dispatch({ type: 'SET_API_STATUS', payload: status.status })
  }

  const loadInitialData = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      
      // Carregar dados essenciais em paralelo
      const [projects, metrics, compliance] = await Promise.all([
        api.getProjects(),
        api.getMetrics(),
        api.getComplianceReport()
      ])

      dispatch({ type: 'SET_PROJECTS', payload: projects })
      dispatch({ type: 'SET_METRICS', payload: metrics })
      dispatch({ type: 'SET_COMPLIANCE', payload: compliance })
      
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  // Ações para interações do usuário
  const scanProjectSecrets = async (projectId) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      const result = await api.scanSecrets(projectId)
      // Recarregar métricas após scan
      const metrics = await api.getMetrics()
      dispatch({ type: 'SET_METRICS', payload: metrics })
      return result
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message })
      throw error
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const scanProjectTerraform = async (projectId) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      const result = await api.scanTerraform(projectId)
      // Recarregar métricas após scan
      const metrics = await api.getMetrics()
      dispatch({ type: 'SET_METRICS', payload: metrics })
      return result
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message })
      throw error
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const createNewProject = async (projectData) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      const newProject = await api.createProject(projectData)
      // Recarregar lista de projetos
      const projects = await api.getProjects()
      dispatch({ type: 'SET_PROJECTS', payload: projects })
      return newProject
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message })
      throw error
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const refreshAllData = async () => {
    await loadInitialData()
  }

  const value = {
    ...state,
    scanProjectSecrets,
    scanProjectTerraform,
    createNewProject,
    refreshAllData,
    checkApiConnection
  }

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}

export const useApp = () => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}
