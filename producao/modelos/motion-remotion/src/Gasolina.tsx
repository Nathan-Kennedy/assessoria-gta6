// M6/M7/M8: ponteiro de gasolina (três trechos, intercalados com cenas do trailer)
import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {Camera, caixaNeon, COR, f, Flash, Fonte, Fundo, neon, Revela, useMola, useRampa} from './base';
import {Bomba} from './Icones';

const CX = 960, CY = 760, R = 400;
const A0 = 210, A1 = 330; // E (esquerda) ... F (direita), em graus no sentido horário a partir das 3h
const ang = (frac: number) => (A0 + (A1 - A0) * frac) * Math.PI / 180;
const pt = (frac: number, r: number) => [CX + r * Math.cos(ang(frac)), CY + r * Math.sin(ang(frac))];

const Mostrador: React.FC<{frac: number; ap: number; perigo: number; destaque?: number}> = ({frac, ap, perigo, destaque = 0}) => {
  const frame = useCurrentFrame();
  const arco = (a: number, b: number) => {
    const [x0, y0] = pt(a, R), [x1, y1] = pt(b, R);
    return `M ${x0} ${y0} A ${R} ${R} 0 0 1 ${x1} ${y1}`;
  };
  const [nx, ny] = pt(frac, R - 50);
  const luz = perigo > 0 ? (Math.floor(frame / 5) % 2 === 0 ? 1 : 0.25) : 0;
  const corP = frac < 0.12 ? COR.verm : frac < 0.3 ? COR.laranja : '#fff';
  return (
    <div style={{position: 'absolute', inset: 0, opacity: ap, transform: `scale(${0.85 + 0.15 * ap})`, transformOrigin: `${CX}px ${CY}px`}}>
      <svg width="1920" height="1080" style={{position: 'absolute'}}>
        <defs>
          <linearGradient id="gArco" x1="0" x2="1"><stop offset="0" stopColor={COR.verm} /><stop offset="0.3" stopColor={COR.laranja} /><stop offset="1" stopColor={COR.ciano} /></linearGradient>
        </defs>
        <path d={arco(0, 1)} stroke="#ffffff22" strokeWidth={46} fill="none" strokeLinecap="round" />
        <path d={arco(0, 1)} stroke="url(#gArco)" strokeWidth={22} fill="none" strokeLinecap="round" strokeDasharray={2000} strokeDashoffset={2000 * (1 - ap)} style={{filter: 'drop-shadow(0 0 14px rgba(255,61,139,0.8))'}} />
        {new Array(17).fill(0).map((_, i) => {
          const fr = i / 16; const [a, b] = pt(fr, R - 40); const [c, d] = pt(fr, R - (i % 4 === 0 ? 90 : 66));
          return <line key={i} x1={a} y1={b} x2={c} y2={d} stroke="#fff" strokeWidth={i % 4 === 0 ? 8 : 4} opacity={0.9} />;
        })}
        {['E', '1/4', '1/2', '3/4', 'F'].map((t, i) => {
          const [x, y] = pt(i / 4, R + 70);
          return <text key={t} x={x} y={y} fill={i === 0 ? COR.verm : '#fff'} fontFamily="Anton" fontSize={62} textAnchor="middle" dominantBaseline="middle">{t}</text>;
        })}
        {destaque > 0 && <circle cx={CX} cy={CY} r={R - 30 + 20 * Math.sin(frame / 4)} fill="none" stroke={COR.ouro} strokeWidth={6} opacity={destaque * 0.8} strokeDasharray="20 18" />}
        <line x1={CX} y1={CY} x2={nx} y2={ny} stroke={corP} strokeWidth={16} strokeLinecap="round" style={{filter: `drop-shadow(0 0 16px ${corP})`}} />
        <circle cx={CX} cy={CY} r={44} fill="#0c0410" stroke="#fff" strokeWidth={8} />
      </svg>
      <div style={{position: 'absolute', left: CX - 40, top: CY + 90, opacity: 0.4 + 0.6 * luz}}><Bomba cor={perigo > 0 ? COR.verm : '#ffffff66'} s={80} /></div>
    </div>
  );
};

// tremidinha natural do ponteiro
const useTremePonteiro = () => {
  const frame = useCurrentFrame();
  return 0.006 * Math.sin(frame / 2.3) + 0.004 * (random(`t${Math.floor(frame / 2)}`) - 0.5);
};

const Titulo: React.FC<{texto: string; cor: string; em: number}> = ({texto, cor, em}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: 110, display: 'flex', justifyContent: 'center'}}>
    <Revela texto={texto} em={em} style={{fontFamily: 'Anton', fontSize: 120, color: cor, textShadow: `0 8px 0 #000, ${neon(cor, 0.6)}`}} />
  </div>
);

// "E lembra da gasolina... olhe o ponteiro antes de escolher o carro de fuga" (5,52 s)
export const GasolinaA: React.FC = () => {
  const ap = useRampa(0.0, 0.9);
  const desce = useRampa(0.5, 2.6, Easing.bezier(0.33, 1, 0.68, 1));
  const tr = useTremePonteiro();
  const destaque = useRampa(3.0, 3.3);
  const seta = useMola(3.05, {damping: 12});
  return (
    <AbsoluteFill>
      <Fundo img="bg_noite.png" tom={COR.laranja} />
      <Camera zoom={[1.0, 1.08]} foco={[960, 700]}>
        <Titulo texto="COMBUSTÍVEL" cor={COR.laranja} em={0.45} />
        <Mostrador frac={interpolate(desce, [0, 1], [1, 0.5]) + tr} ap={ap} perigo={0} destaque={destaque} />
        <div style={{position: 'absolute', left: 1330, top: 330, transform: `scale(${seta}) rotate(-8deg)`, transformOrigin: 'left center', opacity: Math.min(1, seta * 2),
          padding: '12px 30px', borderRadius: 18, background: COR.ouro, boxShadow: caixaNeon(COR.ouro, 0.9), fontFamily: 'Anton', fontSize: 64, color: COR.roxo}}>
          OLHA O PONTEIRO
        </div>
      </Camera>
    </AbsoluteFill>
  );
};

// "...com um quarto de tanque" (1,79 s)
export const GasolinaB: React.FC = () => {
  const tr = useTremePonteiro();
  const desce = useRampa(0.0, 1.0, Easing.bezier(0.33, 1, 0.68, 1));
  return (
    <AbsoluteFill>
      <Fundo img="bg_noite.png" tom={COR.laranja} />
      <Camera zoom={[1.06, 1.12]} foco={[960, 700]}>
        <Titulo texto="1/4 DE TANQUE" cor={COR.laranja} em={0.55} />
        <Mostrador frac={interpolate(desce, [0, 1], [0.5, 0.25]) + tr} ap={1} perigo={0} />
      </Camera>
      <Fonte texto="FONTE: ROB NELSON" em={0} />
    </AbsoluteFill>
  );
};

// "a gasolina acabou antes dele despistar a polícia" (2,86 s)
export const GasolinaC: React.FC = () => {
  const frame = useCurrentFrame();
  const cai = useRampa(0.35, 1.0, Easing.in(Easing.cubic));
  const quique = frame > f(1.0) ? 0.012 * Math.exp(-(frame - f(1.0)) / 4) * Math.sin((frame - f(1.0)) * 1.4) : 0;
  const morto = useRampa(1.0, 1.6);
  return (
    <AbsoluteFill style={{filter: `saturate(${1 - morto * 0.4})`}}>
      <Fundo img="bg_noite.png" tom={COR.verm} />
      <AbsoluteFill style={{background: `radial-gradient(ellipse at center, transparent 45%, rgba(255,0,30,${0.35 * morto}) 100%)`}} />
      <Camera zoom={[1.1, 1.16]} impactos={[1.0]} foco={[960, 700]}>
        <Titulo texto="TANQUE VAZIO" cor={COR.verm} em={0.5} />
        <Mostrador frac={Math.max(0, interpolate(cai, [0, 1], [0.25, 0]) + quique)} ap={1} perigo={morto} />
      </Camera>
      <Flash em={[1.0]} />
    </AbsoluteFill>
  );
};
