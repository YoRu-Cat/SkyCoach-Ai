import { useMemo, useState, type ReactNode } from "react";
import { CalendarDays, ClipboardList, Menu, Sparkles, X } from "lucide-react";
import Dashboard from "../pages/Dashboard";
import TodoPage from "../pages/TodoPage";
import TimetablePage from "../pages/TimetablePage";
import PlannerPage from "../pages/PlannerPage";
import { useTaskStore } from "@hooks/useTaskStore";

export type AppView = "dashboard" | "todo" | "timetable" | "planner";

interface NavItem {
  id: AppView;
  label: string;
  icon: ReactNode;
}

export default function AppShell() {
  const [activeView, setActiveView] = useState<AppView>("dashboard");
  const [menuOpen, setMenuOpen] = useState(false);
  const taskStore = useTaskStore();

  const navItems: NavItem[] = useMemo(
    () => [
      {
        id: "dashboard",
        label: "SkyCoach",
        icon: <Sparkles className="w-4 h-4" />,
      },
      {
        id: "todo",
        label: "Todo List",
        icon: <ClipboardList className="w-4 h-4" />,
      },
      {
        id: "timetable",
        label: "Timetable",
        icon: <CalendarDays className="w-4 h-4" />,
      },
      {
        id: "planner",
        label: "Weather Planner",
        icon: <Sparkles className="w-4 h-4" />,
      },
    ],
    [],
  );

  const renderView = () => {
    switch (activeView) {
      case "todo":
        return <TodoPage {...taskStore} />;
      case "timetable":
        return <TimetablePage {...taskStore} />;
      case "planner":
        return <PlannerPage tasks={taskStore.tasks} />;
      case "dashboard":
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-slate-100">
      <header className="sticky top-0 z-40 border-b border-slate-700/60 bg-slate-900/75 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="lg:hidden p-2 rounded-lg bg-slate-800/80 border border-slate-700 hover:border-cyan-500/60"
              onClick={() => setMenuOpen(true)}
              aria-label="Open navigation menu">
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg sm:text-xl font-bold">SkyCoach Navigator</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            {navItems.find((item) => item.id === activeView)?.label}
          </p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 grid grid-cols-1 lg:grid-cols-[240px_minmax(0,1fr)] gap-6">
        <aside className="hidden lg:block card h-fit sticky top-24">
          <nav className="space-y-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setActiveView(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm border transition-colors ${
                  item.id === activeView
                    ? "bg-cyan-500/20 border-cyan-400 text-cyan-200"
                    : "bg-slate-800/50 border-slate-700 text-slate-300 hover:border-cyan-500/40"
                }`}>
                {item.icon}
                {item.label}
              </button>
            ))}
          </nav>
        </aside>

        <main>{renderView()}</main>
      </div>

      {menuOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <button
            type="button"
            className="absolute inset-0 bg-black/60"
            onClick={() => setMenuOpen(false)}
            aria-label="Close menu overlay"
          />
          <aside className="relative w-72 max-w-[85vw] h-full bg-slate-900 border-r border-slate-700 p-4 animate-slide-in-left">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Menu</h2>
              <button
                type="button"
                className="p-2 rounded-lg bg-slate-800 border border-slate-700"
                onClick={() => setMenuOpen(false)}
                aria-label="Close navigation menu">
                <X className="w-4 h-4" />
              </button>
            </div>

            <nav className="space-y-2">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => {
                    setActiveView(item.id);
                    setMenuOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm border transition-colors ${
                    item.id === activeView
                      ? "bg-cyan-500/20 border-cyan-400 text-cyan-200"
                      : "bg-slate-800/50 border-slate-700 text-slate-300 hover:border-cyan-500/40"
                  }`}>
                  {item.icon}
                  {item.label}
                </button>
              ))}
            </nav>
          </aside>
        </div>
      )}
    </div>
  );
}
