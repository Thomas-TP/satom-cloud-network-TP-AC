import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {C, W, H, BAR, fontFamily} from './theme';

export type Mod = {num: number; name: string; sub: string};

// Bandeau bas : module courant + progression. Totalement statique (aucun tremblement).
export const Hud: React.FC<{mod: Mod | null}> = ({mod}) => {
  if (!mod) return null;
  return (
    <div style={{position: 'absolute', left: 0, top: H - BAR, width: W, height: BAR, background: 'linear-gradient(90deg,#0a1124,#0f1a33)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 28px', fontFamily, boxShadow: '0 -1px 0 rgba(255,255,255,0.06)'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
        <div style={{width: 28, height: 28, borderRadius: 14, background: `linear-gradient(135deg,${C.acc},${C.acc2})`, color: '#06101f', fontWeight: 800, fontSize: 15, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{mod.num}</div>
        <div style={{color: C.text, fontWeight: 600, fontSize: 19, letterSpacing: 0.2}}>Module {mod.num}</div>
        <div style={{color: C.mute, fontWeight: 500, fontSize: 19}}>· {mod.name}</div>
      </div>
      <div style={{display: 'flex', alignItems: 'center', gap: 6}}>
        {Array.from({length: 14}).map((_, i) => (
          <div key={i} style={{width: i === mod.num ? 30 : 16, height: 6, borderRadius: 3, background: i < mod.num ? C.acc2 : i === mod.num ? C.acc : 'rgba(148,163,184,0.28)'}} />
        ))}
      </div>
    </div>
  );
};

export const Badge: React.FC<{k: number; from: number; to: number}> = ({k, from, to}) => {
  const f = useCurrentFrame();
  const a = interpolate(f, [from, from + 6, to - 6, to], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (a <= 0) return null;
  return (
    <div style={{position: 'absolute', right: 34, top: 18, opacity: a, transform: `translateY(${(1 - a) * -8}px)`, background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', color: '#fff', fontFamily, fontWeight: 700, fontSize: 24, padding: '8px 20px', borderRadius: 999, boxShadow: '0 6px 20px rgba(0,0,0,0.35)', letterSpacing: 0.3}}>
      ▶▶  accéléré ×{k}
    </div>
  );
};
