// M2: "E tem outra. O jogo libera por fuso horário. A Nova Zelândia joga umas 16 horas antes da gente." (7,56 s)
import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {Camera, caixaNeon, Conta, COR, f, Flash, Fundo, neon, Revela, useMola, useRampa} from './base';

const T = {titulo: 1.3, faixa: 2.35, nz: 3.45, br: 4.0, horas: 4.85, antes: 6.3};

// faixa de 24 h com dia/noite e o "agora" andando
const Faixa: React.FC = () => {
  const frame = useCurrentFrame();
  const ap = useRampa(T.faixa, T.faixa + 0.8);
  const ponte = useRampa(T.horas, T.horas + 1.1, Easing.bezier(0.65, 0, 0.35, 1));
  const xNZ = 360, xBR = 1560;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 760, height: 200, opacity: ap}}>
      <div style={{position: 'absolute', left: 200, right: 200, top: 70, height: 18, borderRadius: 99, overflow: 'hidden', transform: `scaleX(${ap})`,
        background: `linear-gradient(90deg, ${COR.ouro}, ${COR.laranja} 30%, ${COR.rosa} 55%, #3a1a6a 80%, #120614)`, boxShadow: `0 0 30px ${COR.rosa}66`}}>
        <div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(90deg, rgba(0,0,0,0.35) 0 2px, transparent 2px 60px)'}} />
      </div>
      {/* arco de 16 h entre os dois pontos */}
      <svg width="1920" height="200" style={{position: 'absolute', left: 0, top: -60}}>
        <path d={`M ${xNZ} 140 Q 960 -40 ${xBR} 140`} fill="none" stroke={COR.laranja} strokeWidth={8} strokeLinecap="round"
          strokeDasharray="1500" strokeDashoffset={1500 * (1 - ponte)} style={{filter: `drop-shadow(0 0 10px ${COR.laranja})`}} />
      </svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: -150, textAlign: 'center', fontFamily: 'Anton', fontSize: 150, color: COR.laranja,
        opacity: ponte, transform: `scale(${0.7 + 0.3 * ponte})`, textShadow: `0 8px 0 #000, ${neon(COR.laranja, 0.7)}`}}>
        <Conta de={0} ate={16} a={T.horas} b={T.horas + 1.1} /> HORAS
        <div style={{fontFamily: 'Mont', fontWeight: 800, fontSize: 44, color: '#fff', marginTop: -24, letterSpacing: 4, opacity: useRampa(T.antes, T.antes + 0.4)}}>ANTES DA GENTE</div>
      </div>
      {frame > f(T.faixa) && [0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
        <div key={i} style={{position: 'absolute', left: 200 + i * 190, top: 104, fontFamily: 'Mont', fontWeight: 700, fontSize: 22, color: COR.cinza, transform: 'translateX(-50%)'}}>{`${String(i * 3).padStart(2, '0')}h`}</div>
      ))}
    </div>
  );
};

const Cartao: React.FC<{x: number; em: number; cor: string; lugar: string; hora: string; status: string; ok: boolean}> = ({x, em, cor, lugar, hora, status, ok}) => {
  const frame = useCurrentFrame();
  const m = useMola(em, {damping: 13});
  const pulso = 0.5 + 0.5 * Math.sin((frame - f(em)) / 4);
  const conf = ok ? new Array(26).fill(0).map((_, i) => {
    const d = frame - f(em + 0.15); if (d < 0) return null;
    const ang = random(`a${i}`) * Math.PI * 2, v = 6 + random(`v${i}`) * 10;
    return <div key={i} style={{position: 'absolute', left: 230 + Math.cos(ang) * v * d, top: 150 + Math.sin(ang) * v * d + d * d * 0.35, width: 12, height: 6,
      background: i % 2 ? COR.rosa : COR.ouro, transform: `rotate(${d * 20 + i * 30}deg)`, opacity: Math.max(0, 1 - d / 30)}} />;
  }) : null;
  return (
    <div style={{position: 'absolute', left: x - 230, top: 330, width: 460, height: 330, borderRadius: 30, background: 'rgba(12,4,18,0.82)', border: `3px solid ${cor}`,
      boxShadow: caixaNeon(cor, 1), transform: `translateY(${(1 - m) * 120}px) scale(${0.85 + 0.15 * m})`, opacity: Math.min(1, m * 1.4)}}>
      {conf}
      <div style={{textAlign: 'center', fontFamily: 'Anton', fontSize: 64, color: '#fff', marginTop: 26, letterSpacing: 2}}>{lugar}</div>
      <div style={{textAlign: 'center', fontFamily: 'Anton', fontSize: hora.length > 6 ? 68 : 96, color: cor, marginTop: hora.length > 6 ? 14 : -6, marginBottom: hora.length > 6 ? 20 : 0, textShadow: neon(cor, 0.5)}}>{hora}</div>
      <div style={{margin: '8px auto 0', width: 330, padding: '10px 0', borderRadius: 99, textAlign: 'center', fontFamily: 'Mont', fontWeight: 900, fontSize: 30, letterSpacing: 2,
        background: ok ? cor : 'transparent', color: ok ? COR.roxo : cor, border: `3px solid ${cor}`, opacity: ok ? 1 : 0.55 + 0.45 * pulso}}>
        {status}
      </div>
    </div>
  );
};

export const Fuso: React.FC = () => (
  <AbsoluteFill>
    <Fundo img="bg_noite.png" tom={COR.laranja} />
    <Camera zoom={[1.0, 1.07]} impactos={[T.nz + 0.1]} foco={[960, 600]}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 80, display: 'flex', justifyContent: 'center'}}>
        <Revela texto="O JOGO LIBERA POR" em={T.titulo} style={{fontFamily: 'Anton', fontSize: 84, color: '#fff', textShadow: '0 6px 0 #000'}} />
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 185, display: 'flex', justifyContent: 'center'}}>
        <Revela texto="FUSO HORÁRIO" em={T.faixa} style={{fontFamily: 'Anton', fontSize: 84, color: COR.laranja, textShadow: `0 6px 0 #000, ${neon(COR.laranja, 0.5)}`}} />
      </div>
      <Cartao x={420} em={T.nz} cor={COR.rosa} lugar="NOVA ZELÂNDIA" hora="00:00" status="LIBERADO ✓" ok />
      <Cartao x={1500} em={T.br} cor={COR.ciano} lugar="BRASIL" hora="08:00 · DIA 18" status="ESPERANDO..." ok={false} />
      <Faixa />
    </Camera>
    <Flash em={[T.nz + 0.05]} />
  </AbsoluteFill>
);
