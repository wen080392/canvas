import React from "react"
import { AppProvider } from "@/contexts/AppContext"
import { Header } from "@/components/layout/header"
import { Sidebar } from "@/components/layout/sidebar"
import Router from "@/components/Router"

function App() {
  return (
    <AppProvider>
      <div className="min-h-screen bg-white">
        <Header />
        <div className="flex">
          <Sidebar />
          <main className="flex-1">
            <Router />
          </main>
        </div>
      </div>
    </AppProvider>
  )
}

export default App
