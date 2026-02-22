import React, { useState } from "react"
import { useApp } from "@/contexts/AppContext"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

export default function ProjectsPage() {
  const { projects, loading, error, createNewProject, scanProjectSecrets, scanProjectTerraform } = useApp()
  const [isCreating, setIsCreating] = useState(false)
  const [newProjectName, setNewProjectName] = useState("")
  const [newProjectDescription, setNewProjectDescription] = useState("")

  const handleCreateProject = async (e) => {
    e.preventDefault()
    if (!newProjectName.trim()) return

    try {
      setIsCreating(true)
      await createNewProject({
        name: newProjectName,
        description: newProjectDescription,
        type: "terraform"
      })
      setNewProjectName("")
      setNewProjectDescription("")
    } catch (error) {
      console.error("Erro ao criar projeto:", error)
    } finally {
      setIsCreating(false)
    }
  }

  const handleScanSecrets = async (projectId) => {
    try {
      await scanProjectSecrets(projectId)
      alert("Scan de segredos iniciado!")
    } catch (error) {
      alert("Erro ao iniciar scan: " + error.message)
    }
  }

  const handleScanTerraform = async (projectId) => {
    try {
      await scanProjectTerraform(projectId)
      alert("Scan de Terraform iniciado!")
    } catch (error) {
      alert("Erro ao iniciar scan: " + error.message)
    }
  }

  if (loading && projects.length === 0) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-lg">Carregando projetos...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Gestão de Projetos</h1>
          <p className="text-slate-600">Gerencie e escaneie seus projetos de infraestrutura</p>
        </div>
        
        <Dialog>
          <DialogTrigger asChild>
            <Button>+ Novo Projeto</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Criar Novo Projeto</DialogTitle>
              <DialogDescription>
                Adicione um novo projeto para monitoramento de segurança.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreateProject}>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="name">Nome do Projeto</Label>
                  <Input
                    id="name"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    placeholder="meu-projeto-terraform"
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="description">Descrição</Label>
                  <Input
                    id="description"
                    value={newProjectDescription}
                    onChange={(e) => setNewProjectDescription(e.target.value)}
                    placeholder="Projeto de infraestrutura principal"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" disabled={isCreating}>
                  {isCreating ? "Criando..." : "Criar Projeto"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>Erro ao carregar projetos: {error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Projetos ({projects.length})</CardTitle>
          <CardDescription>
            Todos os projetos monitorados pelo CloudGuardian
          </CardDescription>
        </CardHeader>
        <CardContent>
          {projects.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-slate-500">Nenhum projeto encontrado.</p>
              <p className="text-sm text-slate-400 mt-2">
                Crie seu primeiro projeto para começar o monitoramento.
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Descrição</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Último Scan</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projects.map((project) => (
                  <TableRow key={project.id}>
                    <TableCell className="font-medium">{project.name}</TableCell>
                    <TableCell>{project.description || "-"}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{project.type || "terraform"}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={project.status === "active" ? "default" : "secondary"}>
                        {project.status || "active"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {project.last_scan ? 
                        new Date(project.last_scan).toLocaleDateString() : 
                        "Nunca"
                      }
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleScanSecrets(project.id)}
                        >
                          Scan Segredos
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleScanTerraform(project.id)}
                        >
                          Scan Terraform
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Cards de Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Projetos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{projects.length}</div>
            <p className="text-xs text-slate-600">Projetos ativos</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scans Realizados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {projects.reduce((acc, project) => acc + (project.scan_count || 0), 0)}
            </div>
            <p className="text-xs text-slate-600">Total de scans</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Projetos Conformes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {projects.filter(p => p.compliant).length}
            </div>
            <p className="text-xs text-slate-600">Em compliance</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
