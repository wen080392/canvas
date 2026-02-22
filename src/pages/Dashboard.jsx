import React from "react"
import { useApp } from "@/contexts/AppContext"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function Dashboard() {
  const { projects, metrics, compliance, loading, error, apiStatus } = useApp()

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-lg">Carregando dados do CloudGuardian...</div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive" className="m-8">
        <AlertDescription>
          Erro ao carregar dados: {error}
          <Button variant="outline" className="ml-4" onClick={() => window.location.reload()}>
            Tentar Novamente
          </Button>
        </AlertDescription>
      </Alert>
    )
  }

  if (apiStatus === 'offline') {
    return (
      <Alert variant="destructive" className="m-8">
        <AlertDescription>
          ⚠️ API Backend offline. Verifique se o servidor está rodando em http://localhost:8000
          <Button variant="outline" className="ml-4" onClick={() => window.location.reload()}>
            Verificar Conexão
          </Button>
        </AlertDescription>
      </Alert>
    )
  }

  // Calcular métricas baseadas nos dados reais
  const totalProjects = projects.length || 0
  const compliantProjects = projects.filter(p => p.compliant).length || 0
  const complianceRate = totalProjects > 0 ? (compliantProjects / totalProjects) * 100 : 0

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Dashboard CloudGuardian</h1>
        <p className="text-slate-600">
          {apiStatus === 'online' ? '✅ Conectado ao Backend' : '🔄 Verificando conexão...'}
        </p>
      </div>
      
      {/* Stats Grid com dados reais da API */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Projetos Ativos</CardTitle>
            <Badge variant="outline">+{metrics.project_growth || 0}%</Badge>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalProjects}</div>
            <Progress value={complianceRate} className="mt-2" />
            <p className="text-xs text-slate-600 mt-2">{compliantProjects} projetos conformes</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scans Realizados</CardTitle>
            <Badge variant="outline">+{metrics.scan_growth || 0}%</Badge>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.total_scans || 0}</div>
            <Progress value={metrics.scan_success_rate || 0} className="mt-2" />
            <p className="text-xs text-slate-600 mt-2">{metrics.successful_scans || 0} sem problemas</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance</CardTitle>
            <Badge className="bg-green-100 text-green-800">
              {compliance.overall_score || 0}%
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{compliance.framework || 'SOC2/ISO27k'}</div>
            <Progress value={compliance.overall_score || 0} className="mt-2" />
            <p className="text-xs text-slate-600 mt-2">
              {compliance.status || 'Em conformidade'}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Segredos Detectados</CardTitle>
            <Badge variant="destructive">{metrics.secrets_found || 0}</Badge>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{metrics.secrets_found || 0}</div>
            <Progress value={((metrics.secrets_found || 0) / 10) * 100} className="mt-2" />
            <p className="text-xs text-slate-600 mt-2">Necessita atenção</p>
          </CardContent>
        </Card>
      </div>
      
      {/* Ações principais */}
      <div className="flex gap-4 mb-8">
        <Button>Executar Scan Completo</Button>
        <Button variant="outline">Ver Relatório Compliance</Button>
        <Button variant="outline">Gerenciar Projetos</Button>
      </div>

      {/* Status da API */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="text-sm">Status do Sistema</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="font-medium">Backend API:</span>
              <Badge variant={apiStatus === 'online' ? 'default' : 'destructive'} className="ml-2">
                {apiStatus === 'online' ? 'Online' : 'Offline'}
              </Badge>
            </div>
            <div>
              <span className="font-medium">Projetos:</span>
              <Badge variant="outline" className="ml-2">{totalProjects}</Badge>
            </div>
            <div>
              <span className="font-medium">Scans Hoje:</span>
              <Badge variant="outline" className="ml-2">{metrics.today_scans || 0}</Badge>
            </div>
            <div>
              <span className="font-medium">Versão:</span>
              <Badge variant="outline" className="ml-2">1.0.0</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
