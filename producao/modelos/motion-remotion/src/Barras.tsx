// M1: "O jogo pede até 212 GB ... o GTA 5 de PS4 pedia uns 50" (6,6 s)
import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {Camera, caixaNeon, Conta, COR, f, Flash, Fonte, Fundo, neon, Revela, useMola, useRampa} from './base';

const T = {titulo: 0.1, b212: 1.05, comparar: 2.7, b50: 3.9, n50: 5.55, badge: 5.95};
const CHAO = 900;

const Barra: React.FC<{x: number; altura: number; cor: string; rotulo: string; sub: string; em: number; valor: React.ReactNode; estoura?: boolean}> = ({x, altura, cor, rotulo, sub, em, valor, estoura}) => {
  const frame = useCurrentFrame();
  const m = useMola(em, {damping: estoura ? 11 : 15, stiffness: estoura ? 90 : 130, mass: estoura ? 1.2 : 0.8});
  const h = altura * m;
  const ap = useRampa(em - 0.25, em + 0.1);
  const brilho = 0.5 + 0.5 * Math.sin(frame / 6);
  return (
    <>
      <div style={{position: 'absolute', left: x - 170, width: 340, top: CHAO - h, height: h, borderRadius: '24px 24px 0 0', overflow: 'hidden',
        background: `linear-gradient(180deg, ${cor} 0%, ${cor}CC 60%, ${cor}66 100%)`, boxShadow: `${caixaNeon(cor, 1.2)}, 0 0 ${80 + brilho * 40}px ${cor}66`}}>
        <div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(180deg, rgba(255,255,255,0.13) 0 3px, transparent 3px 26px)', transform: `translateY(${(frame * 3) % 26}px)`}} />
        <div style={{position: 'absolute', top: 0, bottom: 0, width: 120, left: interpolate((frame + x) % 90, [0, 90], [-160, 380]), background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.35), transparent)', transform: 'skewX(-18deg)'}} />
      </div>
      <div style={{position: 'absolute', left: x - 260, width: 520, top: CHAO + 26, textAlign: 'center', opacity: ap, transform: `translateY(${(1 - ap) * 30}px)`}}>
        <div style={{fontFamily: 'Anton', fontSize: 76, color: '#fff', letterSpacing: 2, textShadow: '0 6px 0 #000'}}>{rotulo}</div>
        <div style={{fontFamily: 'Mont', fontWeight: 700, fontSize: 30, color: cor, marginTop: -6}}>{sub}</div>
      </div>
      <div style={{position: 'absolute', left: x - 300, width: 600, textAlign: 'center', top: estoura ? 300 : CHAO - h - 150, opacity: Math.min(1, m * 1.5),
        fontFamily: 'Anton', fontSize: estoura ? 170 : 120, color: '#fff', textShadow: `0 8px 0 #000, ${neon(cor, 0.8)}`, transform: `scale(${0.6 + 0.4 * Math.min(1, m)})`}}>
        {valor}
      </div>
    </>
  );
};

export const Barras: React.FC = () => {
  const frame = useCurrentFrame();
  const chao = useRampa(0, 0.6);
  const bm = useMola(T.badge, {damping: 9, stiffness: 160});
  const foco = interpolate(frame, [f(T.comparar), f(T.comparar + 1.2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return (
    <AbsoluteFill>
      <Fundo tom={COR.rosa} />
      <Camera zoom={[1.0, 1.06]} impactos={[T.b212 + 0.25, T.badge]} foco={[960, 700]}>
        <div style={{position: 'absolute', left: 140, right: 140, top: CHAO, height: 6, background: '#fff', transform: `scaleX(${chao})`, boxShadow: neon('#fff', 0.6), borderRadius: 4}} />
        <Barra x={1250 - foco * 60} altura={1150} cor={COR.rosa} rotulo="GTA 6" sub="PS5" em={T.b212} estoura
          valor={<><Conta de={0} ate={212} a={T.b212} b={T.b212 + 1.0} /> <span style={{fontSize: 110}}>GB</span></>} />
        <Barra x={640 - foco * 20} altura={50 * 4.1} cor={COR.ciano} rotulo="GTA 5" sub="PS4" em={T.b50}
          valor={<>~<Conta de={0} ate={50} a={T.b50} b={T.n50 + 0.2} /> <span style={{fontSize: 80}}>GB</span></>} />
        <div style={{position: 'absolute', left: 120, top: 160}}>
          <Revela texto="ESPAÇO PRA" em={T.titulo} style={{fontFamily: 'Anton', fontSize: 96, color: '#fff', textShadow: '0 6px 0 #000'}} />
          <Revela texto="INSTALAR" em={T.titulo + 0.15} style={{fontFamily: 'Anton', fontSize: 96, color: COR.rosa, textShadow: `0 6px 0 #000, ${neon(COR.rosa, 0.5)}`, marginTop: -18}} />
        </div>
        <div style={{position: 'absolute', left: 120, top: 470, transform: `scale(${bm}) rotate(${(1 - bm) * -20 - 6}deg)`, transformOrigin: 'left center', opacity: Math.min(1, bm * 2),
          padding: '14px 34px', borderRadius: 18, background: COR.laranja, boxShadow: caixaNeon(COR.laranja, 1), fontFamily: 'Anton', fontSize: 78, color: COR.roxo}}>
          4X MAIOR
        </div>
      </Camera>
      <Fonte texto="FONTE: PÁGINA DO JOGO NA PSN" em={0.6} cor={COR.ciano} />
      <Flash em={[T.b212 + 0.2]} />
    </AbsoluteFill>
  );
};
