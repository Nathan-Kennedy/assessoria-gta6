// M3: GTA 5 (ligação direta em 1 s) x GTA 6 (carro antigo -> chave mestra)  (12 s)
// M4: GTA 6 carro novo -> chave eletrônica -> clonador; sem ele, nem liga  (6 s)
import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {Camera, caixaNeon, COR, f, Flash, Fonte, Fundo, neon, Revela, useMola, useRampa} from './base';
import {Carro, Chave, Lamina, Raio} from './Icones';

// nó do "fluxograma" com linha que se desenha até ele
const No: React.FC<{x: number; y: number; em: number; cor: string; titulo: string; sub?: string; icone?: React.ReactNode; apagado?: boolean; w?: number; de?: [number, number]}> = ({x, y, em, cor, titulo, sub, icone, apagado, w = 600, de}) => {
  const m = useMola(em, {damping: 15});
  const linha = useRampa(em - 0.25, em + 0.05);
  const op = apagado ? 0.38 : 1;
  return (
    <>
      {de && (
        <svg width="1920" height="1080" style={{position: 'absolute', left: 0, top: 0, opacity: op}}>
          <path d={`M ${de[0]} ${de[1]} C ${de[0]} ${(de[1] + y) / 2}, ${x} ${(de[1] + y) / 2}, ${x} ${y - 70}`} fill="none" stroke={cor} strokeWidth={6}
            strokeDasharray="900" strokeDashoffset={900 * (1 - linha)} style={{filter: `drop-shadow(0 0 8px ${cor})`}} />
        </svg>
      )}
      <div style={{position: 'absolute', left: x - w / 2, top: y - 70, width: w, height: sub ? 170 : 140, borderRadius: 26, background: 'rgba(12,4,18,0.85)',
        border: `3px solid ${cor}`, boxShadow: caixaNeon(cor, apagado ? 0.3 : 1), display: 'flex', alignItems: 'center', gap: 22, padding: '0 30px', boxSizing: 'border-box',
        transform: `scale(${0.6 + 0.4 * m})`, opacity: Math.min(1, m * 1.6) * op, filter: apagado ? 'saturate(0.3)' : 'none'}}>
        {icone}
        <div>
          <div style={{fontFamily: 'Anton', fontSize: 58, color: '#fff', lineHeight: 1.05}}>{titulo}</div>
          {sub && <div style={{fontFamily: 'Mont', fontWeight: 800, fontSize: 30, color: cor, marginTop: 4}}>{sub}</div>}
        </div>
      </div>
    </>
  );
};

const Cabecalho: React.FC<{x: number; texto: string; cor: string; em: number}> = ({x, texto, cor, em}) => {
  const m = useMola(em, {damping: 12});
  return <div style={{position: 'absolute', left: x - 300, width: 600, top: 120, textAlign: 'center', fontFamily: 'Anton', fontSize: 150, color: cor,
    textShadow: `0 8px 0 #000, ${neon(cor, 0.8)}`, transform: `scale(${m}) translateY(${(1 - m) * -60}px)`}}>{texto}</div>;
};

// cronômetro de 1 segundo
const Cronometro: React.FC<{em: number}> = ({em}) => {
  const p = useRampa(em, em + 0.9, Easing.linear);
  const m = useMola(em - 0.3);
  const r = 70, c = 2 * Math.PI * r;
  return (
    <div style={{position: 'absolute', left: 480 - 110, top: 720, width: 220, height: 220, transform: `scale(${m})`}}>
      <svg width={220} height={220}>
        <circle cx={110} cy={110} r={r} fill="rgba(12,4,18,0.8)" stroke="#ffffff33" strokeWidth={14} />
        <circle cx={110} cy={110} r={r} fill="none" stroke={COR.ciano} strokeWidth={14} strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c * (1 - p)}
          transform="rotate(-90 110 110)" style={{filter: `drop-shadow(0 0 10px ${COR.ciano})`}} />
      </svg>
      <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Anton', fontSize: 64, color: '#fff'}}>{p.toFixed(1)}s</div>
    </div>
  );
};

const Carimbo: React.FC<{em: number; texto: string; x: number; y: number}> = ({em, texto, x, y}) => {
  const frame = useCurrentFrame();
  const d = frame - f(em);
  const s = interpolate(d, [0, 5, 9], [2.6, 0.92, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return d < 0 ? null : (
    <div style={{position: 'absolute', left: x - 330, top: y - 90, width: 660, height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center',
      border: `12px solid ${COR.verm}`, borderRadius: 26, transform: `rotate(-12deg) scale(${s})`, opacity: interpolate(d, [0, 3], [0, 1], {extrapolateRight: 'clamp'}),
      fontFamily: 'Anton', fontSize: 140, color: COR.verm, letterSpacing: 8, textShadow: neon(COR.verm, 0.6), boxShadow: caixaNeon(COR.verm, 0.8), background: 'rgba(40,0,0,0.35)'}}>
      {texto}
    </div>
  );
};

export const SplitAntigo: React.FC = () => {
  const frame = useCurrentFrame();
  const T = {gta5: 0.15, carro: 1.45, ligacao: 3.95, seg: 4.85, acabou: 5.98, nelson: 7.1, antigo: 9.25, mestra: 10.55};
  const abre = useRampa(T.nelson - 0.3, T.nelson + 0.5, Easing.bezier(0.65, 0, 0.35, 1));
  const morto = useRampa(T.acabou, T.acabou + 0.5);
  const carroM = useMola(T.carro);
  const div = interpolate(abre, [0, 1], [1920, 960]);
  return (
    <AbsoluteFill>
      <Fundo img="bg_noite.png" tom={COR.ciano} />
      <Camera zoom={[1.0, 1.05]} impactos={[T.acabou + 0.15]}>
        {/* metade GTA 5: ocupa a tela toda e depois vira a metade esquerda */}
        <div style={{position: 'absolute', left: interpolate(abre, [0, 1], [480, 0]), top: 0, width: 960, height: 1080, filter: `saturate(${1 - morto * 0.7}) brightness(${1 - morto * 0.35})`}}>
          <Cabecalho x={480} texto="GTA 5" cor={COR.ciano} em={T.gta5} />
          <div style={{position: 'absolute', left: 480 - 190, top: 330, transform: `translateX(${(1 - carroM) * -700}px)`, opacity: carroM}}><Carro cor={COR.ciano} w={380} /></div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 540, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 20}}>
            <div style={{transform: `scale(${useMola(T.ligacao)})`}}><Raio cor={COR.ciano} s={100} /></div>
            <Revela texto="LIGAÇÃO DIRETA" em={T.ligacao} style={{fontFamily: 'Anton', fontSize: 84, color: '#fff', textShadow: '0 6px 0 #000'}} />
          </div>
          <Cronometro em={T.seg} />
        </div>
        <Carimbo em={T.acabou} texto="ACABOU" x={interpolate(abre, [0, 1], [960, 480])} y={560} />
        {/* divisória e metade GTA 6 */}
        <div style={{position: 'absolute', left: div - 4, top: 60, width: 8, height: 960, background: '#fff', borderRadius: 8, boxShadow: neon('#fff', 0.7), opacity: abre}} />
        <div style={{position: 'absolute', left: div, top: 0, width: 960, height: 1080}}>
          <Cabecalho x={480} texto="GTA 6" cor={COR.rosa} em={T.nelson + 0.1} />
          <No x={480} y={470} em={T.antigo} cor={COR.rosa} titulo="CARRO ANTIGO" icone={<Carro cor={COR.rosa} w={150} />} w={640} />
          <No x={480} y={760} em={T.mestra} cor={COR.ciano} titulo="CHAVE MESTRA" sub="lâmina fina pela porta" icone={<Lamina cor={COR.ciano} s={100} />} w={680} de={[480, 545]} />
        </div>
      </Camera>
      {frame >= f(T.nelson) && <Fonte texto="FONTE: ROB NELSON À IGN" em={T.nelson + 0.2} />}
      <Flash em={[T.acabou]} />
    </AbsoluteFill>
  );
};

export const SplitNovo: React.FC = () => {
  const frame = useCurrentFrame();
  const T = {novo: 0.35, eletr: 1.05, clon: 2.7, sem: 3.95, liga: 5.28};
  const falha = frame >= f(T.liga);
  const pisca = falha ? (Math.floor((frame - f(T.liga)) / 3) % 2 === 0 ? 1 : 0.3) : 1;
  const btn = useMola(T.sem, {damping: 12});
  const aperta = interpolate(frame - f(T.sem + 0.6), [0, 3, 6], [1, 0.9, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      <Fundo tom={COR.rosa} />
      <Camera zoom={[1.0, 1.06]} impactos={[T.liga + 0.05]} foco={[1300, 600]}>
        <Cabecalho x={960} texto="GTA 6" cor={COR.rosa} em={0} />
        <svg width="1920" height="1080" style={{position: 'absolute', left: 0, top: 0}}>
          <path d="M 960 290 C 960 330, 520 330, 520 370" stroke={COR.rosa} strokeWidth={6} fill="none" opacity={0.35} />
        </svg>
        <No x={520} y={440} em={-1} cor={COR.rosa} titulo="CARRO ANTIGO" sub="chave mestra ou vidro" icone={<Carro cor={COR.rosa} w={130} />} apagado w={620} />
        <No x={1340} y={440} em={T.novo} cor={COR.ciano} titulo="CARRO NOVO" icone={<Carro cor={COR.ciano} w={130} />} w={600} de={[960, 290]} />
        <No x={1340} y={680} em={T.eletr} cor={COR.ciano} titulo="CHAVE ELETRÔNICA" icone={<Chave cor={COR.ciano} s={100} eletronica />} w={680} de={[1340, 515]} />
        <No x={1340} y={920} em={T.clon} cor={COR.laranja} titulo="CLONADOR DE CHAVE" sub="sem ele, nem liga" icone={<Chave cor={COR.laranja} s={100} eletronica />} w={720} de={[1340, 755]} />
        {/* botão de partida que falha */}
        <div style={{position: 'absolute', left: 520 - 150, top: 640, width: 300, height: 300, borderRadius: 999, transform: `scale(${btn * aperta})`, opacity: Math.min(1, btn * 2),
          border: `10px solid ${falha ? COR.verm : '#ffffffcc'}`, background: 'radial-gradient(circle, #2a1030 0%, #0c0410 70%)', boxShadow: caixaNeon(falha ? COR.verm : '#ffffff', 0.9),
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
          <div style={{fontFamily: 'Anton', fontSize: 64, color: falha ? COR.verm : '#fff', opacity: pisca}}>{falha ? 'NEM LIGA' : 'START'}</div>
          <div style={{fontFamily: 'Mont', fontWeight: 800, fontSize: 24, color: COR.cinza, letterSpacing: 3}}>ENGINE</div>
        </div>
        {falha && <div style={{position: 'absolute', left: 520 - 250, top: 960, width: 500, textAlign: 'center', fontFamily: 'Mont', fontWeight: 900, fontSize: 34, color: COR.verm, letterSpacing: 3, opacity: pisca}}>SEM CLONADOR</div>}
      </Camera>
      <Flash em={[T.liga]} />
    </AbsoluteFill>
  );
};
