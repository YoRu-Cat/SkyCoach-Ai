import { useEffect, useMemo, useState } from "react";
import { gsap } from "gsap";

interface ScoreGaugeProps {
  score: number;
}

const clampScore = (score: number): number => {
  return Math.max(0, Math.min(100, score));
};

export default function ScoreGauge({ score }: ScoreGaugeProps) {
  const [displayScore, setDisplayScore] = useState(0);
  const normalizedScore = clampScore(score);
  const segmentCount = 20;

  useEffect(() => {
    const tweenState = { value: 0 };
    const tween = gsap.to(tweenState, {
      value: normalizedScore,
      duration: 1.2,
      ease: "power3.out",
      onUpdate: () => {
        setDisplayScore(Math.round(tweenState.value));
      },
    });

    return () => {
      tween.kill();
    };
  }, [normalizedScore]);

  const activeSegments = Math.round(displayScore / 5);
  const segments = useMemo(
    () => Array.from({ length: segmentCount }, (_, index) => index),
    [segmentCount],
  );

  return (
    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-6 mx-auto w-fit">
      <div className="relative w-44 h-44 gauge-shell">
        <div className="gauge-ring">
          {segments.map((index) => (
            <span
              key={index}
              className={`gauge-segment gauge-segment-${index} ${index < activeSegments ? "is-active" : ""}`}
            />
          ))}
        </div>
      </div>

      <div className="text-center sm:text-left sm:pt-2">
        <p className="text-4xl font-bold text-cyan-300 leading-none">
          {displayScore}
        </p>
        <p className="text-xs text-slate-400 mt-1 tracking-wide uppercase">
          SkyScore
        </p>
      </div>
    </div>
  );
}
