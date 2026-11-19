import React from 'react';
import {AbsoluteFill, Easing, OffthreadVideo, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, W, H, BAR, fontFamily} from './theme';
import {Badge, Hud, Mod} from './Hud';

type Cam = number[][]; // [t, cx, cy, zoom]

export type GuiScene = {id: string; src: string; dur: number; cam: Cam; badges: number[][]; title: string; detail: string; mod: Mod | null; dark: boolean; masks?: number[][]; trim?: number};

const camAt = (cam: Cam, t: number) => {
  let lo = 0, hi = cam.length - 1;
  if (t <= cam[0][0]) return cam[0];
  if (t >= cam[hi][0]) return cam[hi];
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (cam[m][0] <= t) lo = m; else hi = m; }
  const a = cam[lo], b = cam[hi], u = (t - a[0]) / (b[0] - a[0]);
  return [t, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u, a[3] + (b[3] - a[3]) * u];
};

export const Gui: React.FC<{s: GuiScene; fadeIn: number}> = ({s, fadeIn}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  const [, cx, cy, z] = camAt(s.cam, t);
  const tx = W / 2 - cx * z, ty = H / 2 - cy * z;
  const op = fadeIn > 0 ? interpolate(f, [0, fadeIn], [0, 1], {extrapolateRight: 'clamp'}) : 1;

  // legende : entre apres 0,5 s, reste ~4,5 s
  const capIn = 15, capLen = Math.min(150, s.dur - 45);
  const cp = spring({frame: f - capIn, fps, config: {damping: 18, stiffness: 120, mass: 0.8}});
  const co = interpolate(f, [capIn, capIn + 8, capIn + capLen - 10, capIn + capLen], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const showCap = s.title && capLen > 30 && co > 0;

  return (
    <AbsoluteFill style={{background: '#fff', opacity: op}}>
      <AbsoluteFill style={{overflow: 'hidden', background: '#f2f3f3'}}>
        <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, transformOrigin: '0 0', transform: `translate(${tx}px,${ty}px) scale(${z})`, willChange: 'transform'}}>
          <OffthreadVideo src={s.src} startFrom={s.trim || 0} muted style={{width: W, height: H}} />
          {(s.masks || []).map((m, i) => (t >= m[0] && t <= m[1]) ? (
            <div key={i} style={{position: 'absolute', left: m[2], top: m[3], width: m[4], height: m[5], borderRadius: 5, background: s.dark ? '#2a303c' : '#dfe3e8', color: s.dark ? '#8b95a5' : '#6b7280', fontFamily, fontWeight: 700, fontSize: Math.max(10, m[5] * 0.8), display: 'flex', alignItems: 'center', justifyContent: 'center', letterSpacing: 2, overflow: 'hidden'}}>{'•'.repeat(Math.max(4, Math.min(14, Math.round(m[4] / 9))))}</div>
          ) : null)}
        </div>
      </AbsoluteFill>
      <Hud mod={s.mod} />
      {s.badges.map((b, i) => <Badge key={i} k={b[2]} from={Math.round(b[0] * fps)} to={Math.round(b[1] * fps)} />)}
      {showCap && (
        <div style={{position: 'absolute', left: 48, bottom: BAR + 26, opacity: co, transform: `translateY(${(1 - cp) * 26}px)`, fontFamily, maxWidth: 1180}}>
          <div style={{display: 'flex', background: C.panel, borderRadius: 18, overflow: 'hidden', boxShadow: '0 14px 40px rgba(2,6,23,0.45)', border: '1px solid rgba(255,255,255,0.08)'}}>
            <div style={{width: 8, background: `linear-gradient(180deg,${C.acc},${C.acc2})`}} />
            <div style={{padding: '16px 28px 16px 22px'}}>
              <div style={{color: C.text, fontWeight: 700, fontSize: 38, letterSpacing: -0.3, lineHeight: 1.15}}>{s.title}</div>
              {s.detail ? <div style={{color: C.mute, fontWeight: 500, fontSize: 25, marginTop: 6, lineHeight: 1.25}}>{s.detail}</div> : null}
            </div>
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
