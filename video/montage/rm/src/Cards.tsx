import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, W, H, fontFamily} from './theme';
import {Mod} from './Hud';

const Bg: React.FC<{children?: React.ReactNode}> = ({children}) => (
  <AbsoluteFill style={{background: `radial-gradient(1200px 700px at 78% 20%, #1b2a55 0%, transparent 60%), radial-gradient(900px 600px at 10% 90%, #17325a 0%, transparent 55%), ${C.bg}`, fontFamily}}>
    {children}
  </AbsoluteFill>
);

const Grad: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <span style={{background: `linear-gradient(135deg,${C.acc},${C.acc2})`, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', ...style}}>{children}</span>
);

export const Title: React.FC<{dur: number}> = ({dur}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const s1 = spring({frame: f - 6, fps, config: {damping: 20, stiffness: 90}});
  const s2 = spring({frame: f - 20, fps, config: {damping: 20, stiffness: 90}});
  const s3 = spring({frame: f - 34, fps, config: {damping: 20, stiffness: 90}});
  const out = interpolate(f, [dur - 10, dur], [1, 0], {extrapolateLeft: 'clamp'});
  return (
    <Bg>
      <div style={{position: 'absolute', inset: 0, opacity: out, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{opacity: s1, transform: `translateY(${(1 - s1) * 30}px)`, color: C.mute, fontSize: 30, fontWeight: 600, letterSpacing: 8, textTransform: 'uppercase'}}>Groupe Léman Finance SA</div>
        <div style={{opacity: s2, transform: `translateY(${(1 - s2) * 40}px)`, fontSize: 150, fontWeight: 800, letterSpacing: -4, marginTop: 18, color: C.text}}>Satom <Grad>Cloud Network</Grad></div>
        <div style={{width: 520 * s2, height: 6, borderRadius: 3, background: `linear-gradient(90deg,${C.acc},${C.acc2})`, marginTop: 26}} />
        <div style={{opacity: s3, transform: `translateY(${(1 - s3) * 30}px)`, color: '#cbd5e1', fontSize: 38, fontWeight: 500, marginTop: 34}}>Un réseau complet sur AWS, construit à la main dans la console</div>
        <div style={{opacity: s3, color: C.mute, fontSize: 28, marginTop: 20}}>Équipe TP-AC · Thomas Prud'homme et Abderahmane Chaouche</div>
      </div>
    </Bg>
  );
};

export const Diagram: React.FC<{img: string; dur: number; label: string; sub: string; focus?: number[][]}> = ({img, dur, label, sub, focus}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const p = spring({frame: f - 4, fps, config: {damping: 22, stiffness: 80}});
  let k = interpolate(f, [0, dur], [1.0, 1.045], {easing: Easing.inOut(Easing.quad)});
  let tx = 0, ty = 0;
  if (focus && focus.length > 1) {
    const kf = focus.filter((q, i) => i === 0 || q[0] > focus[i - 1][0] + 0.05);       // temps strictement croissants
    const t = f / fps; const ts = kf.map((q) => q[0]);
    const ez = {easing: Easing.inOut(Easing.cubic), extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
    const cx = interpolate(t, ts, kf.map((q) => q[1]), ez), cy = interpolate(t, ts, kf.map((q) => q[2]), ez); k = interpolate(t, ts, kf.map((q) => q[3]), ez);
    tx = k * (0.5 - cx) * 1440; ty = k * (0.5 - cy) * 810;
  }
  const out = interpolate(f, [dur - 10, dur], [1, 0], {extrapolateLeft: 'clamp'});
  const t2 = spring({frame: f - 18, fps, config: {damping: 20, stiffness: 90}});
  return (
    <Bg>
      <div style={{position: 'absolute', inset: 0, opacity: out}}>
        <div style={{position: 'absolute', left: 120, top: 70, opacity: t2, transform: `translateY(${(1 - t2) * 24}px)`}}>
          <div style={{color: C.acc, fontSize: 26, fontWeight: 700, letterSpacing: 6, textTransform: 'uppercase'}}>{label}</div>
          <div style={{color: C.text, fontSize: 58, fontWeight: 800, letterSpacing: -1.5, marginTop: 6}}>{sub}</div>
        </div>
        <div style={{position: 'absolute', left: 240, top: 215, width: 1440, height: 810, borderRadius: 28, overflow: 'hidden', boxShadow: '0 30px 80px rgba(0,0,0,0.55)', opacity: p, transform: `scale(${0.94 + 0.06 * p})`, background: '#fff'}}>
          <Img src={img} style={{width: 1440, height: 810, transform: `translate(${tx}px, ${ty}px) scale(${k})`, transformOrigin: '50% 50%'}} />
        </div>
      </div>
    </Bg>
  );
};

export const Chapter: React.FC<{mod: Mod; img: string; dur: number}> = ({mod, img, dur}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const sp = (d: number) => spring({frame: f - d, fps, config: {damping: 19, stiffness: 95, mass: 0.9}});
  const a = sp(2), b = sp(10), c = sp(18), d = sp(26), im = sp(14);
  const out = interpolate(f, [dur - 10, dur], [1, 0], {extrapolateLeft: 'clamp'});
  const kb = interpolate(f, [0, dur], [1.0, 1.04], {easing: Easing.inOut(Easing.quad)});
  return (
    <Bg>
      <div style={{position: 'absolute', inset: 0, opacity: out}}>
        <div style={{position: 'absolute', left: 90, top: 64, display: 'flex', gap: 8, opacity: a}}>
          {Array.from({length: 14}).map((_, i) => <div key={i} style={{width: i === mod.num ? 44 : 22, height: 7, borderRadius: 4, background: i < mod.num ? C.acc2 : i === mod.num ? C.acc : 'rgba(148,163,184,0.25)'}} />)}
        </div>
        <div style={{position: 'absolute', left: 90, top: 250}}>
          <div style={{opacity: a, transform: `translateY(${(1 - a) * 24}px)`, color: C.mute, fontSize: 30, fontWeight: 700, letterSpacing: 10, textTransform: 'uppercase'}}>Module</div>
          <div style={{opacity: b, transform: `translateY(${(1 - b) * 40}px)`, fontSize: 230, fontWeight: 800, lineHeight: 1, letterSpacing: -8, marginTop: 4}}><Grad>{String(mod.num).padStart(2, '0')}</Grad></div>
          <div style={{width: 360 * c, height: 6, borderRadius: 3, background: `linear-gradient(90deg,${C.acc},${C.acc2})`, margin: '18px 0 26px'}} />
          <div style={{opacity: c, transform: `translateY(${(1 - c) * 30}px)`, color: C.text, fontSize: 76, fontWeight: 800, letterSpacing: -2, lineHeight: 1.05, maxWidth: 700}}>{mod.name}</div>
          <div style={{opacity: d, transform: `translateY(${(1 - d) * 24}px)`, color: '#cbd5e1', fontSize: 34, fontWeight: 500, marginTop: 18, maxWidth: 700}}>{mod.sub}</div>
        </div>
        <div style={{position: 'absolute', left: 850, top: 265, width: 980, height: 551, borderRadius: 26, overflow: 'hidden', background: '#fff', boxShadow: '0 30px 80px rgba(0,0,0,0.55)', opacity: im, transform: `translateX(${(1 - im) * 60}px)`}}>
          <Img src={img} style={{width: 980, height: 551, transform: `scale(${kb})`, transformOrigin: '50% 50%'}} />
        </div>
      </div>
    </Bg>
  );
};

export const End: React.FC<{img: string; dur: number}> = ({img, dur}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const p = spring({frame: f - 4, fps, config: {damping: 22, stiffness: 80}});
  const t = spring({frame: f - 16, fps, config: {damping: 20, stiffness: 90}});
  const out = interpolate(f, [dur - 18, dur], [1, 0], {extrapolateLeft: 'clamp'});
  const facts = ['14 modules faits à la main dans la console', 'VPN, Direct Connect et Transit Gateway', 'Équilibreur, DNS, CloudFront et supervision', 'Tout décrit aussi en CloudFormation'];
  return (
    <Bg>
      <div style={{position: 'absolute', inset: 0, opacity: out}}>
        <div style={{position: 'absolute', left: 100, top: 130, opacity: t, transform: `translateY(${(1 - t) * 30}px)`}}>
          <div style={{color: C.acc, fontSize: 26, fontWeight: 700, letterSpacing: 6, textTransform: 'uppercase'}}>Voilà le résultat</div>
          <div style={{color: C.text, fontSize: 74, fontWeight: 800, letterSpacing: -2, marginTop: 10, lineHeight: 1.05}}>Satom Cloud<br /><Grad>Network</Grad></div>
          <div style={{marginTop: 40}}>
            {facts.map((x, i) => {
              const q = spring({frame: f - 30 - i * 8, fps, config: {damping: 20, stiffness: 100}});
              return <div key={i} style={{display: 'flex', alignItems: 'center', gap: 16, color: '#dbe4f3', fontSize: 28, fontWeight: 500, marginBottom: 20, maxWidth: 640, opacity: q, transform: `translateX(${(1 - q) * 30}px)`}}><div style={{width: 14, height: 14, borderRadius: 7, background: C.green}} />{x}</div>;
            })}
          </div>
          <div style={{color: C.mute, fontSize: 26, marginTop: 36}}>Équipe TP-AC · Groupe Léman Finance SA</div>
        </div>
        <div style={{position: 'absolute', left: 860, top: 258, width: 1000, height: 562, borderRadius: 26, overflow: 'hidden', background: '#fff', boxShadow: '0 30px 80px rgba(0,0,0,0.55)', opacity: p, transform: `scale(${0.95 + 0.05 * p})`}}>
          <Img src={img} style={{width: 1000, height: 562}} />
        </div>
      </div>
    </Bg>
  );
};
