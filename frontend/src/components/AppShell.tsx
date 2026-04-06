import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  Home,
  CalendarDays,
  ClipboardList,
  MessageSquare,
  Moon,
  Sparkles,
  Sun,
} from "lucide-react";
import { motion } from "framer-motion";
import { gsap } from "gsap";
import "locomotive-scroll/dist/locomotive-scroll.css";
import Dashboard from "../pages/Dashboard";
import TodoPage from "../pages/TodoPage";
import TimetablePage from "../pages/TimetablePage";
import PlannerPage from "../pages/PlannerPage";
import ChatPage from "../pages/ChatPage";
import HomePage from "../pages/HomePage";
import ParticlesComponent from "@components/ParticlesComponent";
import { useTaskStore } from "@hooks/useTaskStore";

export type AppView =
  | "home"
  | "dashboard"
  | "todo"
  | "timetable"
  | "planner"
  | "chat";

interface NavItem {
  id: AppView;
  label: string;
  icon: ReactNode;
}

const clamp = (value: number, min: number, max: number) =>
  Math.max(min, Math.min(max, value));

type ThemeMode = "dark" | "light";

const THEME_STORAGE_KEY = "skycoach_theme_v1";

const loadTheme = (): ThemeMode => {
  if (typeof window === "undefined") return "dark";
  const value = window.localStorage.getItem(THEME_STORAGE_KEY);
  return value === "light" ? "light" : "dark";
};

export default function AppShell() {
  const [activeView, setActiveView] = useState<AppView>("home");
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => loadTheme());
  const taskStore = useTaskStore();
  const shellRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const panelWrapRef = useRef<HTMLDivElement>(null);
  const cursorOrbRef = useRef<HTMLDivElement>(null);

  const navItems: NavItem[] = useMemo(
    () => [
      {
        id: "home",
        label: "Home",
        icon: <Home className="w-4 h-4" />,
      },
      {
        id: "chat",
        label: "Command Chat",
        icon: <MessageSquare className="w-4 h-4" />,
      },
      {
        id: "dashboard",
        label: "SkyCoach Core",
        icon: <Sparkles className="w-4 h-4" />,
      },
      {
        id: "todo",
        label: "Todo",
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
      case "home":
        return (
          <HomePage
            taskStore={taskStore}
            onNavigate={(target) => setActiveView(target)}
          />
        );
      case "todo":
        return <TodoPage {...taskStore} />;
      case "timetable":
        return <TimetablePage {...taskStore} />;
      case "planner":
        return (
          <PlannerPage
            tasks={taskStore.tasks}
            updateTask={taskStore.updateTask}
          />
        );
      case "chat":
        return (
          <ChatPage
            taskStore={taskStore}
            onNavigate={(target) => setActiveView(target)}
          />
        );
      case "dashboard":
      default:
        return <Dashboard embedded />;
    }
  };

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", themeMode);
    window.localStorage.setItem(THEME_STORAGE_KEY, themeMode);
  }, [themeMode]);

  useEffect(() => {
    if (!shellRef.current) return;

    let loco: {
      destroy: () => void;
      on?: (event: string, cb: () => void) => void;
    } | null = null;

    const panel = panelRef.current;
    const panelWrap = panelWrapRef.current;
    const orb = cursorOrbRef.current;

    if (!panel || !panelWrap || !orb) {
      return;
    }

    const updatePanelByScroll = () => {
      if (!panel) return;
      const rect = panel.getBoundingClientRect();
      const start = window.innerHeight * 0.92;
      const end = window.innerHeight * 0.34;
      const progress = clamp((start - rect.top) / (start - end), 0, 1);

      gsap.to(panel, {
        rotateX: 16 * (1 - progress),
        rotateY: 0,
        y: 90 * (1 - progress),
        scaleX: 0.965 + progress * 0.035,
        opacity: 0.72 + progress * 0.28,
        duration: 0.22,
        ease: "power2.out",
        overwrite: true,
      });
    };

    const ctx = gsap.context(() => {
      gsap.set(panel, {
        rotateX: 16,
        rotateY: 0,
        y: 90,
        scaleX: 0.965,
        opacity: 0.72,
        transformPerspective: 1000,
        transformOrigin: "50% 10%",
      });

      gsap.fromTo(
        ".hero-line",
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.8, stagger: 0.08, ease: "power3.out" },
      );

      updatePanelByScroll();
    }, shellRef);

    void import("locomotive-scroll")
      .then(({ default: LocomotiveScroll }) => {
        if (!shellRef.current) return;
        loco = new (LocomotiveScroll as unknown as new (options: object) => {
          destroy: () => void;
          on?: (event: string, cb: () => void) => void;
        })({
          el: shellRef.current,
          smooth: true,
          multiplier: 0.9,
          smartphone: { smooth: false },
          tablet: { smooth: false },
        });

        if (typeof loco.on === "function") {
          loco.on("scroll", updatePanelByScroll);
        }
      })
      .catch(() => {
        // Keep native scrolling if locomotive fails to load.
      });

    const onWindowScroll = () => updatePanelByScroll();
    window.addEventListener("scroll", onWindowScroll, { passive: true });

    let moveHandler: ((event: MouseEvent) => void) | null = null;
    let enterHandler: (() => void) | null = null;
    let leaveHandler: (() => void) | null = null;

    if (panelWrap && orb) {
      const xTo = gsap.quickTo(orb, "x", {
        duration: 0.42,
        ease: "power3.out",
      });
      const yTo = gsap.quickTo(orb, "y", {
        duration: 0.42,
        ease: "power3.out",
      });

      moveHandler = (event: MouseEvent) => {
        const rect = panelWrap.getBoundingClientRect();
        xTo(event.clientX - rect.left - 70);
        yTo(event.clientY - rect.top - 70);
      };

      enterHandler = () => {
        gsap.to(orb, {
          opacity: 1,
          scale: 1,
          duration: 0.2,
          ease: "power2.out",
        });
      };

      leaveHandler = () => {
        gsap.to(orb, {
          opacity: 0,
          scale: 0.7,
          duration: 0.25,
          ease: "power2.out",
        });
      };

      panelWrap.addEventListener("mousemove", moveHandler);
      panelWrap.addEventListener("mouseenter", enterHandler);
      panelWrap.addEventListener("mouseleave", leaveHandler);
    }

    return () => {
      if (panelWrap && moveHandler)
        panelWrap.removeEventListener("mousemove", moveHandler);
      if (panelWrap && enterHandler)
        panelWrap.removeEventListener("mouseenter", enterHandler);
      if (panelWrap && leaveHandler)
        panelWrap.removeEventListener("mouseleave", leaveHandler);
      window.removeEventListener("scroll", onWindowScroll);
      ctx.revert();
      if (loco) {
        loco.destroy();
      }
    };
  }, []);

  return (
    <div
      ref={shellRef}
      data-scroll-container
      className={`relative min-h-screen overflow-hidden ${
        themeMode === "light"
          ? "theme-light bg-[#f6f2fc] text-[#210f3c]"
          : "theme-dark bg-midnight_violet-100 text-alabaster_grey-900"
      }`}>
      <div className="pointer-events-none absolute inset-0 z-0 opacity-95">
        <ParticlesComponent
          id="skycoach-tech-particles"
          themeMode={themeMode}
        />
      </div>

      <div
        className={`pointer-events-none absolute inset-0 z-0 ${
          themeMode === "light"
            ? "bg-[radial-gradient(circle_at_20%_10%,rgba(181,150,229,0.34),transparent_44%),radial-gradient(circle_at_80%_70%,rgba(208,190,242,0.35),transparent_48%)]"
            : "bg-[radial-gradient(circle_at_20%_10%,rgba(149,5,233,0.24),transparent_44%),radial-gradient(circle_at_80%_70%,rgba(73,0,122,0.26),transparent_46%)]"
        }`}
      />

      <header
        className={`sticky top-0 z-40 border-b backdrop-blur-2xl shadow-[0_8px_24px_rgba(9,0,20,0.2)] ${
          themeMode === "light"
            ? "border-[#b596e5]/45 bg-gradient-to-r from-[#e1d8f7]/76 via-[#d7c8f3]/70 to-[#d0bef2]/76"
            : "border-[#5f2e86]/45 bg-gradient-to-r from-[#220135]/74 via-[#190028]/70 to-[#11001c]/74"
        }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          <h1
            className={`text-lg sm:text-xl font-semibold tracking-tight ${
              themeMode === "light"
                ? "text-[#210f3c]"
                : "text-alabaster_grey-900"
            }`}>
            SkyCoach Quantum Deck
          </h1>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() =>
                setThemeMode((prev) => (prev === "dark" ? "light" : "dark"))
              }
              aria-label="Toggle theme"
              title="Toggle theme"
              className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs ${
                themeMode === "light"
                  ? "border-[#9166dc]/60 bg-[#f2eefb]/85 text-[#421e79]"
                  : "border-[#b13dff]/55 bg-[#220135]/70 text-[#e9d8ff]"
              }`}>
              {themeMode === "light" ? (
                <Moon className="h-3.5 w-3.5" />
              ) : (
                <Sun className="h-3.5 w-3.5" />
              )}
              {themeMode === "light" ? "Dark" : "Light"}
            </button>
            <p
              className={`text-xs sm:text-sm ${
                themeMode === "light" ? "text-[#431e83]" : "text-[#e2c8ff]"
              }`}>
              {navItems.find((item) => item.id === activeView)?.label}
            </p>
          </div>
        </div>
      </header>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-7">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div
            data-scroll
            data-scroll-speed="-2"
            className={`absolute top-6 right-[7%] w-56 h-56 rounded-full blur-3xl ${
              themeMode === "light" ? "bg-[#b596e5]/36" : "bg-[#5c0390]/30"
            }`}
          />
          <div
            data-scroll
            data-scroll-speed="2"
            className={`absolute top-40 left-[8%] w-52 h-52 rounded-full blur-3xl ${
              themeMode === "light" ? "bg-[#d0bef2]/38" : "bg-[#49007a]/28"
            }`}
          />
        </div>

        <motion.section
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className={`card border overflow-hidden ${
            themeMode === "light"
              ? "border-[#b596e5]/55 bg-[#f2eefb]/78"
              : "border-[#5f2e86]/45 bg-[#190028]/72"
          }`}>
          <p
            className={`hero-line text-xs uppercase tracking-[0.24em] ${
              themeMode === "light" ? "text-[#642db5]" : "text-[#d3a7ff]"
            }`}>
            Smart Planning Assistant
          </p>
          <h2
            className={`hero-line mt-3 text-3xl md:text-5xl leading-tight font-semibold max-w-4xl ${
              themeMode === "light"
                ? "text-[#210f3c]"
                : "text-alabaster_grey-900"
            }`}>
            SkyCoach helps you plan tasks, schedule your week, and adapt to
            weather in one workspace.
          </h2>
          <p
            className={`hero-line mt-4 max-w-3xl ${
              themeMode === "light" ? "text-[#431e83]" : "text-[#d9b8ff]"
            }`}>
            Use chat commands, timetable controls, and weather-aware scoring to
            turn ideas into clear, executable daily plans.
          </p>
        </motion.section>

        <nav className="flex flex-wrap gap-2">
          {navItems.map((item, index) => (
            <motion.button
              key={item.id}
              type="button"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 * index, duration: 0.35 }}
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setActiveView(item.id)}
              className={`nav-pill flex items-center gap-2 px-5 py-2.5 rounded-full border text-sm font-medium transition-all backdrop-blur-md ${
                themeMode === "light"
                  ? `shadow-[0_4px_12px_rgba(9,20,28,0.28)] ${
                      item.id === activeView
                        ? "bg-[#c0a7eb]/86 border-[#9166dc] text-[#210f3c] shadow-[0_0_0_1px_rgba(145,102,220,0.2),0_8px_14px_rgba(66,30,121,0.16)]"
                        : "bg-[#e7def8]/88 border-[#b596e5] text-[#421e79] hover:border-[#8a59d5] hover:bg-[#d9cbf3]/92"
                    }`
                  : "bg-[#6b2e99]/72 border-[#9d66d9] text-[#f5e6ff] shadow-[0_0_0_1px_rgba(157,102,217,0.3),0_8px_14px_rgba(66,30,121,0.16)]"
              }`}>
              {item.icon}
              {item.label}
            </motion.button>
          ))}
        </nav>

        <div ref={panelWrapRef} className="relative">
          <div
            ref={cursorOrbRef}
            className="cursor-orb pointer-events-none absolute top-0 left-0 w-36 h-36 rounded-full opacity-0 scale-75 mix-blend-screen"
          />

          <main
            ref={panelRef}
            className={`home-main-panel preserve-3d card border transform-gpu ${
              themeMode === "light"
                ? "border-[#b596e5]/55 bg-[#f7f4fd]/80"
                : "border-[#5c0390]/55 bg-[#11001c]/78"
            }`}>
            {renderView()}
          </main>
        </div>
      </div>
    </div>
  );
}
