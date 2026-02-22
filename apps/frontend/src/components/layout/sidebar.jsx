import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Cloud,
  ShieldCheck,
  FileText,
  Settings,
  LogOut,
  Menu,
  X
} from "lucide-react";

export function Sidebar({ className }) {
  const location = useLocation();

  const navigation = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Infrastructure", href: "/infrastructure", icon: Cloud },
    { name: "Drift Detection", href: "/drift", icon: ShieldCheck },
    { name: "Secret Scanner", href: "/secrets", icon: Lock },
    { name: "Compliance", href: "/compliance", icon: FileText },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <div className={cn("pb-12 h-screen w-64 glass-sidebar hidden md:block fixed left-0 top-0", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <Link to="/" className="flex items-center pl-2 mb-9">
            <ShieldCheck className="mr-2 h-8 w-8 text-primary" />
            <h2 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
              CloudGuardian
            </h2>
          </Link>
          <div className="space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "group flex items-center rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-all duration-200",
                  location.pathname === item.href ? "bg-accent/50 text-accent-foreground border-r-2 border-primary" : "text-muted-foreground"
                )}
              >
                <item.icon className={cn("mr-2 h-4 w-4", location.pathname === item.href ? "text-primary" : "text-muted-foreground group-hover:text-primary")} />
                {item.name}
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="absolute bottom-4 left-0 w-full px-3">
        <div className="rounded-lg bg-card p-4 border border-border">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
              AD
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium leading-none truncate">Admin User</p>
              <p className="text-xs text-muted-foreground truncate">admin@company.com</p>
            </div>
            <button
              onClick={() => {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
              }}
              className="ml-auto text-muted-foreground hover:text-destructive transition-colors"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
