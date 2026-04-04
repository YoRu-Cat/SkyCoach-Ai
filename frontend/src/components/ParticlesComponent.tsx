import Particles, { initParticlesEngine } from "@tsparticles/react";
import { useEffect, useMemo, useState } from "react";
import { loadSlim } from "@tsparticles/slim";

interface ParticlesComponentProps {
  id?: string;
}

export default function ParticlesComponent({
  id = "skycoach-particles",
}: ParticlesComponentProps) {
  const [init, setInit] = useState(false);

  useEffect(() => {
    initParticlesEngine(async (engine) => {
      await loadSlim(engine);
    }).then(() => {
      setInit(true);
    });
  }, []);

  const options = useMemo(
    () =>
      ({
        fullScreen: {
          enable: false,
          zIndex: 0,
        },
        background: {
          color: {
            value: "transparent",
          },
        },
        fpsLimit: 120,
        interactivity: {
          events: {
            onClick: {
              enable: true,
              mode: "repulse",
            },
            onHover: {
              enable: true,
              mode: "grab",
            },
          },
          modes: {
            repulse: {
              distance: 180,
              duration: 0.3,
            },
            grab: {
              distance: 170,
            },
          },
        },
        particles: {
          color: {
            value: "#8ab7d8",
          },
          links: {
            color: "#98c1d9",
            distance: 140,
            enable: true,
            opacity: 0.38,
            width: 1,
          },
          move: {
            direction: "none",
            enable: true,
            outModes: {
              default: "bounce",
            },
            random: true,
            speed: 1.4,
            straight: false,
          },
          number: {
            density: {
              enable: true,
            },
            value: 132,
          },
          opacity: {
            value: 0.9,
          },
          shape: {
            type: "circle",
          },
          size: {
            value: { min: 1, max: 3 },
          },
        },
        detectRetina: true,
      }) as const,
    [],
  );

  if (!init) {
    return null;
  }

  return <Particles id={id} className="h-full w-full" options={options} />;
}
