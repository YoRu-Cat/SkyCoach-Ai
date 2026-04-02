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
  const segmentCount = 12;

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
    <div className="flex items-center justify-center w-fit">
      <div className="relative w-24 h-24 sm:w-28 sm:h-28 gauge-shell gauge-shell--compact">
        <div className="gauge-ring">
          {segments.map((index) => (
            <span
              key={index}
              className={`gauge-segment gauge-segment-${index} ${index < activeSegments ? "is-active" : ""}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
