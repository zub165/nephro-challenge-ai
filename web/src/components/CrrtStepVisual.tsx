import { motion } from 'framer-motion';
import type { AnimationMetrics, AnimationVisual } from '@/lib/animationUtils';

interface CrrtStepVisualProps {
  visual: AnimationVisual;
  metrics?: AnimationMetrics;
}

function PressureGauge({
  label,
  value,
  unit,
  warn,
}: {
  label: string;
  value: string;
  unit: string;
  warn?: boolean;
}) {
  const num = parseInt(value, 10);
  const pct = Math.min(100, Math.max(8, (Math.abs(num) / 300) * 100));
  return (
    <div className={`rounded-lg border px-3 py-2 ${warn ? 'border-red-400/50 bg-red-500/10' : 'border-white/10 bg-white/5'}`}>
      <p className="text-[10px] uppercase tracking-wide text-teal-300/80">{label}</p>
      <p className={`text-lg font-bold ${warn ? 'text-red-300' : 'text-white'}`}>
        {value} <span className="text-xs font-normal text-teal-200/70">{unit}</span>
      </p>
      <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-white/10">
        <motion.div
          className={`h-full rounded-full ${warn ? 'bg-red-400' : 'bg-teal-400'}`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6 }}
        />
      </div>
    </div>
  );
}

function CircuitDiagram({ mode }: { mode: 'cvvh' | 'cvvhd' | 'scuf' }) {
  const showDialysate = mode === 'cvvhd';
  const showReplacement = mode !== 'scuf';
  return (
    <svg viewBox="0 0 400 120" className="mx-auto w-full max-w-md" aria-hidden>
      <defs>
        <linearGradient id="bloodGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#ef4444" />
          <stop offset="100%" stopColor="#dc2626" />
        </linearGradient>
        <linearGradient id="fluidGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#2dd4bf" />
          <stop offset="100%" stopColor="#14b8a6" />
        </linearGradient>
      </defs>
      <rect x="155" y="35" width="90" height="50" rx="6" fill="#1e3a5f" stroke="#5eead4" strokeWidth="2" />
      <text x="200" y="65" textAnchor="middle" fill="#99f6e4" fontSize="11" fontWeight="600">
        Hemofilter
      </text>
      <path d="M 20 60 H 155" stroke="url(#bloodGrad)" strokeWidth="4" fill="none" />
      <path d="M 245 60 H 380" stroke="url(#bloodGrad)" strokeWidth="4" fill="none" />
      <motion.circle r="5" fill="#fca5a5" animate={{ cx: [20, 155], cy: 60 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }} />
      <motion.circle r="5" fill="#fca5a5" animate={{ cx: [245, 380], cy: 60 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear', delay: 1 }} />
      {showReplacement && (
        <>
          <path d="M 80 15 H 120 V 35" stroke="url(#fluidGrad)" strokeWidth="2" fill="none" strokeDasharray="4 2" />
          <text x="50" y="12" fill="#5eead4" fontSize="9">Replacement</text>
        </>
      )}
      {showDialysate && (
        <>
          <path d="M 280 15 H 240 V 35" stroke="#60a5fa" strokeWidth="2" fill="none" strokeDasharray="4 2" />
          <text x="285" y="12" fill="#93c5fd" fontSize="9">Dialysate</text>
        </>
      )}
      <text x="30" y="78" fill="#94a3b8" fontSize="9">Access</text>
      <text x="350" y="78" fill="#94a3b8" fontSize="9">Return</text>
      {mode === 'scuf' && (
        <text x="200" y="100" textAnchor="middle" fill="#fbbf24" fontSize="9">UF only — no replacement</text>
      )}
    </svg>
  );
}

export default function CrrtStepVisual({ visual, metrics }: CrrtStepVisualProps) {
  if (visual === 'circuit-cvvh') {
    return <CircuitDiagram mode="cvvh" />;
  }
  if (visual === 'circuit-cvvhd') {
    return <CircuitDiagram mode="cvvhd" />;
  }
  if (visual === 'circuit-scuf') {
    return <CircuitDiagram mode="scuf" />;
  }

  if (visual === 'pressures' && metrics) {
    const tmpWarn = parseInt(metrics.tmp || '0', 10) > 200;
    const accessWarn = parseInt(metrics.access || '0', 10) < -150;
    const returnWarn = parseInt(metrics.return || '0', 10) > 250;
    return (
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <PressureGauge label="Access" value={metrics.access || '—'} unit="mmHg" warn={accessWarn} />
        <PressureGauge label="Pre-filter" value={metrics.prefilter || '—'} unit="mmHg" />
        <PressureGauge label="Return" value={metrics.return || '—'} unit="mmHg" warn={returnWarn} />
        <PressureGauge label="TMP" value={metrics.tmp || '—'} unit="mmHg" warn={tmpWarn} />
      </div>
    );
  }

  if (visual === 'dose-summary' && metrics) {
    return (
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: 'Effluent', value: `${metrics.effluent} mL/hr`, color: 'text-teal-300' },
          { label: 'Dose', value: `${metrics.dose} mL/kg/hr`, color: 'text-amber-300' },
          { label: 'Total input', value: `${metrics.input} mL/hr`, color: 'text-blue-300' },
          { label: 'Net balance', value: `${metrics.balance} mL/hr`, color: 'text-emerald-300' },
        ].map((m) => (
          <div key={m.label} className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-center">
            <p className="text-[10px] uppercase tracking-wide text-teal-300/70">{m.label}</p>
            <p className={`text-sm font-bold ${m.color}`}>{m.value}</p>
          </div>
        ))}
      </div>
    );
  }

  if (visual === 'monitoring') {
    const items = [
      'q4h: Ionized Ca²⁺ (if citrate)',
      'q6h: K⁺, Na⁺, HCO₃⁻, BUN, Cr',
      'q2h: Filter pressures',
      'Daily: Mg²⁺, PO₄³⁻, weight',
    ];
    return (
      <ul className="space-y-1.5 rounded-xl border border-white/10 bg-white/5 p-3">
        {items.map((item) => (
          <li key={item} className="flex gap-2 text-xs text-teal-100/90">
            <span className="text-teal-400">●</span> {item}
          </li>
        ))}
      </ul>
    );
  }

  return null;
}
