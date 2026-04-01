import { useEffect, useState } from "react";
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

  const needleAngle = -120 + (displayScore / 100) * 240;

  return (
    <div className="relative w-44 h-44 mx-auto">
      <svg viewBox="0 0 220 220" className="w-full h-full">
        <defs>
          <linearGradient id="score-arc" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#22d3ee" />
            <stop offset="55%" stopColor="#38bdf8" />
            <stop offset="100%" stopColor="#4ade80" />
          </linearGradient>
        </defs>

        <circle
          cx="110"
          cy="110"
          r="84"
          fill="none"
          stroke="rgba(51,65,85,0.8)"
          strokeWidth="14"
          strokeDasharray="3 11"
          transform="rotate(-120 110 110)"
          strokeLinecap="round"
        />

        <circle
          cx="110"
          cy="110"
          r="84"
          fill="none"
          stroke="url(#score-arc)"
          strokeWidth="14"
          strokeDasharray={`${(displayScore / 100) * 352} 528`}
          transform="rotate(-120 110 110)"
          strokeLinecap="round"
        />
      </svg>

      <div
        className="absolute left-1/2 top-1/2 w-1 h-16 origin-bottom rounded-full score-needle"
        style={{
          transform: `translate(-50%, -100%) rotate(${needleAngle}deg)`,
        }}
      />

      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
        <p className="text-4xl font-bold text-cyan-300 leading-none">{displayScore}</p>
        <p className="text-xs text-slate-400 mt-1 tracking-wide uppercase">SkyScore</p>
      </div>

      <div className="absolute left-1/2 top-1/2 w-4 h-4 rounded-full bg-cyan-300 -translate-x-1/2 -translate-y-1/2 shadow-[0_0_14px_rgba(34,211,238,0.7)]" />
    </div>
  );
}