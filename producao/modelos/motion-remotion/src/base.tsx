// Base visual "Vice Neon Doc": fundo vivo, tipografia, glow, molas e câmera.
import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

export const COR = {rosa: '#FF3D8B', ciano: '#19E3D3', laranja: '#FF8A3D', roxo: '#120614', branco: '#FFFFFF', verm: '#FF2D2D', cinza: '#9A93AE', ouro: '#FFD23F'};
export const FPS = 30;

const css = `
@font-face { font-family: 'Anton'; src: url('${staticFile('fonts/Anton-Regular.ttf')}'); }
@font-face { font-family: 'Mont'; src: url('${staticFile('fonts/Montserrat.ttf')}'); font-weight: 100 900; }
`;
export const Fontes: React.FC = () => <style>{css}</style>;

// segundos -> frames
export const f = (s: number) => Math.round(s * FPS);

// mola que começa no segundo `s`
export const useMola = (s: number, cfg: {damping?: number; stiffness?: number; mass?: number} = {}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: frame - f(s), fps, config: {damping: 14, stiffness: 140, mass: 0.9, ...cfg}});
};
// rampa suave entre dois instantes
export const useRampa = (a: number, b: number, ease = Easing.bezier(0.22, 1, 0.36, 1)) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [f(a), f(b)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
};
// tremida de câmera que decai depois do impacto em `s`
export const useTremor = (impactos: number[], forca = 18) => {
  const frame = useCurrentFrame();
  let x = 0, y = 0, r = 0;
  for (const s of impactos) {
    const d = frame - f(s);
    if (d < 0 || d > 14) continue;
    const k = Math.exp(-d / 4) * forca;
    x += (random(`x${s}${frame}`) - 0.5) * 2 * k;
    y += (random(`y${s}${frame}`) - 0.5) * 2 * k;
    r += (random(`r${s}${frame}`) - 0.5) * 0.6 * k / 10;
  }
  return {x, y, r};
};
// flash branco curto
export const Flash: React.FC<{em: number[]}> = ({em}) => {
  const frame = useCurrentFrame();
  let o = 0;
  for (const s of em) o = Math.max(o, interpolate(frame - f(s), [0, 1, 7], [0, 0.55, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return <AbsoluteFill style={{background: '#fff', opacity: o, mixBlendMode: 'screen'}} />;
};

export const neon = (cor: string, forca = 1) =>
  `0 0 ${6 * forca}px ${cor}, 0 0 ${18 * forca}px ${cor}, 0 0 ${42 * forca}px ${cor}AA`;
export const caixaNeon = (cor: string, forca = 1) =>
  `0 0 ${8 * forca}px ${cor}, 0 0 ${26 * forca}px ${cor}99, inset 0 0 ${18 * forca}px ${cor}55`;

// Fundo: frame do trailer desfocado com Ken Burns + gradiente + grade synthwave + partículas + grão + vinheta
export const Fundo: React.FC<{img?: string; tom?: string; grade?: boolean; escurece?: number}> = ({img = 'bg_neon.png', tom = COR.rosa, grade = true, escurece = 0.78}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const z = interpolate(frame, [0, durationInFrames], [1.12, 1.2]);
  const parts = new Array(38).fill(0).map((_, i) => {
    const x = random(`px${i}`) * 1920;
    const vel = 0.4 + random(`pv${i}`) * 1.2;
    const y = 1080 - ((random(`py${i}`) * 1200 + frame * vel * 2) % 1250);
    const tam = 2 + random(`ps${i}`) * 4;
    const cor = random(`pc${i}`) > 0.5 ? COR.rosa : COR.ciano;
    return <div key={i} style={{position: 'absolute', left: x, top: y, width: tam, height: tam, borderRadius: 99, background: cor, boxShadow: `0 0 10px ${cor}`, opacity: 0.25 + random(`po${i}`) * 0.5}} />;
  });
  return (
    <AbsoluteFill style={{background: COR.roxo, overflow: 'hidden'}}>
      <Img src={staticFile(img)} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${z})`, filter: 'blur(22px) saturate(1.3)'}} />
      <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(18,6,20,${escurece}) 0%, rgba(18,6,20,${escurece - 0.1}) 55%, rgba(30,6,40,${escurece + 0.1}) 100%)`}} />
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 120%, ${tom}40 0%, transparent 60%)`}} />
      {grade && (
        <div style={{position: 'absolute', left: -600, right: -600, bottom: -200, height: 620, transform: 'perspective(500px) rotateX(62deg)', transformOrigin: '50% 100%',
          backgroundImage: `linear-gradient(${tom}55 2px, transparent 2px), linear-gradient(90deg, ${tom}55 2px, transparent 2px)`,
          backgroundSize: '90px 90px', backgroundPosition: `0px ${(frame * 2.2) % 90}px`, maskImage: 'linear-gradient(to top, black 10%, transparent 85%)', WebkitMaskImage: 'linear-gradient(to top, black 10%, transparent 85%)'}} />
      )}
      {parts}
      <AbsoluteFill style={{background: 'repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0 1px, transparent 1px 3px)'}} />
      <AbsoluteFill>
        <svg width="1920" height="1080" style={{opacity: 0.09, mixBlendMode: 'overlay'}}>
          <filter id="grao"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={frame % 30} /></filter>
          <rect width="100%" height="100%" filter="url(#grao)" />
        </svg>
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.75) 100%)'}} />
    </AbsoluteFill>
  );
};

// Câmera: push-in contínuo + tremor; tudo dentro dela se move junto
export const Camera: React.FC<{children: React.ReactNode; zoom?: [number, number]; impactos?: number[]; foco?: [number, number]}> = ({children, zoom = [1, 1.05], impactos = [], foco = [960, 540]}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const z = interpolate(frame, [0, durationInFrames], zoom, {easing: Easing.inOut(Easing.sin)});
  const t = useTremor(impactos);
  return (
    <AbsoluteFill style={{transform: `translate(${t.x}px, ${t.y}px) rotate(${t.r}deg) scale(${z})`, transformOrigin: `${foco[0]}px ${foco[1]}px`}}>
      {children}
    </AbsoluteFill>
  );
};

// Texto que entra palavra por palavra (sobe + desfoca -> nítido)
export const Revela: React.FC<{texto: string; em: number; style?: React.CSSProperties; passo?: number}> = ({texto, em, style, passo = 0.07}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{display: 'flex', gap: '0.25em', flexWrap: 'wrap', ...style}}>
      {texto.split(' ').map((w, i) => {
        const p = interpolate(frame - f(em + i * passo), [0, 9], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.22, 1, 0.36, 1)});
        return <span key={i} style={{display: 'inline-block', opacity: p, transform: `translateY(${(1 - p) * 40}px)`, filter: `blur(${(1 - p) * 10}px)`}}>{w}</span>;
      })}
    </div>
  );
};

// Contador numérico rolando
export const Conta: React.FC<{de: number; ate: number; a: number; b: number; fmt?: (n: number) => string; style?: React.CSSProperties}> = ({de, ate, a, b, fmt = (n) => Math.round(n).toString(), style}) => {
  const p = useRampa(a, b, Easing.bezier(0.16, 1, 0.3, 1));
  return <span style={style}>{fmt(de + (ate - de) * p)}</span>;
};

// Selo "fonte"
export const Fonte: React.FC<{texto: string; em: number; cor?: string}> = ({texto, em, cor = COR.rosa}) => {
  const m = useMola(em, {damping: 18});
  return (
    <div style={{position: 'absolute', left: 70, top: 64, display: 'flex', alignItems: 'center', gap: 14, padding: '12px 24px', borderRadius: 999,
      background: 'rgba(10,4,14,0.75)', border: `2px solid ${cor}`, boxShadow: caixaNeon(cor, 0.6), transform: `translateX(${(1 - m) * -500}px)`, opacity: m,
      fontFamily: 'Mont', fontWeight: 800, fontSize: 26, color: '#fff', letterSpacing: 1}}>
      <div style={{width: 14, height: 14, borderRadius: 99, background: cor, boxShadow: `0 0 12px ${cor}`}} />{texto}
    </div>
  );
};

export const Etiqueta: React.FC<{texto: string; em: number}> = ({texto, em}) => {
  const p = useRampa(em, em + 0.4);
  return <div style={{position: 'absolute', right: 70, bottom: 52, fontFamily: 'Mont', fontWeight: 600, fontSize: 24, color: COR.cinza, opacity: p * 0.9, letterSpacing: 2}}>{texto}</div>;
};
