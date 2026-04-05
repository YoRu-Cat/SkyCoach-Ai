import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  Home,
  CalendarDays,
  ClipboardList,
  MessageSquare,
  Sparkles,
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

export default function AppShell() {
  const [activeView, setActiveView] = useState<AppView>("home");
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
      className="relative min-h-screen overflow-hidden bg-baltic_blue-100 text-alabaster_grey-900">
      <div className="pointer-events-none absolute inset-0 z-0 opacity-95">
        <ParticlesComponent id="skycoach-tech-particles" />
      </div>

      <div className="pointer-events-none absolute inset-0 z-0 bg-[radial-gradient(circle_at_20%_10%,rgba(47,102,144,0.34),transparent_42%),radial-gradient(circle_at_80%_70%,rgba(58,124,165,0.28),transparent_44%)]" />

      <header className="sticky top-0 z-40 border-b border-cerulean-500/45 bg-gradient-to-b from-yale_blue-300/92 to-yale_blue-200/84 backdrop-blur-2xl shadow-[0_10px_34px_rgba(9,20,28,0.45)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          <h1 className="text-lg sm:text-xl font-semibold tracking-tight text-alabaster_grey-900">
            SkyCoach Quantum Deck
          </h1>
          <p className="text-xs sm:text-sm text-sky_blue_light-800">
            {navItems.find((item) => item.id === activeView)?.label}
          </p>
        </div>
      </header>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-7">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div
            data-scroll
            data-scroll-speed="-2"
            className="absolute top-6 right-[7%] w-56 h-56 rounded-full bg-[#3e5c76]/35 blur-3xl"
          />
          <div
            data-scroll
            data-scroll-speed="2"
            className="absolute top-40 left-[8%] w-52 h-52 rounded-full bg-[#5e8fb4]/25 blur-3xl"
          />
        </div>

        <motion.section
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="card border border-cerulean-600/45 bg-baltic_blue-200/72 overflow-hidden">
          <p className="hero-line text-xs uppercase tracking-[0.24em] text-sky_blue_light-600">
            High-Tech Command Surface
          </p>
          <h2 className="hero-line mt-3 text-3xl md:text-5xl leading-tight font-semibold max-w-4xl text-alabaster_grey-900">
            One cinematic chat cockpit to run your planning stack.
          </h2>
          <p className="hero-line mt-4 text-sky_blue_light-700 max-w-3xl">
            Scroll down and watch the command panel rise from grounded cinematic
            depth into full precision mode.
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
              className={`nav-pill flex items-center gap-2 px-5 py-2.5 rounded-full border text-sm font-medium transition-all backdrop-blur-md shadow-[0_4px_12px_rgba(9,20,28,0.28)] ${
                item.id === activeView
                  ? "bg-cerulean-500/62 border-sky_blue_light-500 text-alabaster_grey-900 shadow-[0_0_0_1px_rgba(178,219,231,0.25),0_10px_18px_rgba(22,66,91,0.45)]"
                  : "bg-yale_blue-300/95 border-baltic_blue-500 text-sky_blue_light-800 hover:border-cerulean-600 hover:bg-baltic_blue-400/85"
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
            className="home-main-panel preserve-3d card border border-cerulean-500/60 bg-baltic_blue-200/80 transform-gpu">
            {renderView()}
          </main>
        </div>
      </div>
    </div>
  );
}
