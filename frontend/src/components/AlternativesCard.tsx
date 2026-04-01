import React from 'react';

interface AlternativesCardProps {
  alternatives: string[];
  classification: string;
}

export default function AlternativesCard({
  alternatives,
  classification,
}: AlternativesCardProps) {
  return (
    <div className="card space-y-4 glow-cyan">
      <h3 className="text-lg font-bold text-slate-100">
        💡 Alternative {classification} Activities
      </h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {alternatives.map((activity, idx) => (
          <div
            key={idx}
            className="p-3 bg-slate-800/50 border border-slate-700/50 rounded-lg hover:border-cyan-500/50 transition-colors group cursor-pointer"
          >
            <p className="text-slate-200 group-hover:text-cyan-300 transition-colors">
              {activity}
            </p>
          </div>
        ))}
      </div>

      <p className="text-xs text-slate-500 text-center pt-2">
        Based on current weather conditions and your activity classification
      </p>
    </div>
  );
}
