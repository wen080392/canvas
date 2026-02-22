import { Sidebar } from "./Sidebar";

export default function Shell({ children }) {
    return (
        <div className="min-h-screen bg-background font-sans antialiased text-foreground">
            <Sidebar />
            <main className="md:pl-64 min-h-screen transition-all duration-300 ease-in-out">
                {/* Top Header Placeholder */}
                <header className="h-16 border-b border-border/40 backdrop-blur-sm sticky top-0 z-10 px-6 flex items-center justify-between">
                    <h1 className="text-lg font-semibold text-foreground/80">Enterprise Dashboard</h1>
                    <div className="flex items-center gap-4">
                        {/* Actions like Theme Toggle, Notifications, etc. */}
                        <button className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Docs</button>
                        <button className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Support</button>
                    </div>
                </header>

                <div className="p-6 md:p-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {children}
                </div>
            </main>
        </div>
    );
}
