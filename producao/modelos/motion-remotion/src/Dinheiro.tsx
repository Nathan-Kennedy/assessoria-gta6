// Blocos 7-8: bolso x banco, custo de morrer, Pay 'n' Spray x receptador, regras, a conta
import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {Camera, caixaNeon, Conta, COR, f, Flash, Fonte, Fundo, neon, Revela, useMola, useRampa} from './base';
import {Carro} from './Icones';

const brl = (n: number) => Math.round(n).toLocaleString('pt-BR');

const Nota: React.FC<{x: number; y: number; r?: number; s?: number; o?: number}> = ({x, y, r = 0, s = 1, o = 1}) => (
  <div style={{position: 'absolute', left: x, top: y, width: 120 * s, height: 58 * s, borderRadius: 8, background: 'linear-gradient(135deg, #3ddc84, #1b8f52)', border: '3px solid #bfffd9',
    transform: `rotate(${r}deg)`, opacity: o, boxShadow: '0 0 14px #3ddc8488', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Anton', fontSize: 34 * s, color: '#0b3d22'}}>$</div>
);

const Titulo: React.FC<{texto: string; cor?: string; em: number; y?: number; tam?: number}> = ({texto, cor = '#fff', em, y = 90, tam = 96}) => (
  <div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center'}}>
    <Revela texto={texto} em={em} style={{fontFamily: 'Anton', fontSize: tam, color: cor, textShadow: `0 7px 0 #000${cor !== '#fff' ? ', ' + neon(cor, 0.5) : ''}`}} />
  </div>
);

const Carimbo: React.FC<{em: number; texto: string; x: number; y: number; cor?: string; tam?: number; rot?: number}> = ({em, texto, x, y, cor = COR.verm, tam = 130, rot = -10}) => {
  const frame = useCurrentFrame();
  const d = frame - f(em);
  if (d < 0) return null;
  const s = interpolate(d, [0, 5, 9], [2.6, 0.93, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) rotate(${rot}deg) scale(${s})`, opacity: interpolate(d, [0, 3], [0, 1], {extrapolateRight: 'clamp'}),
      padding: '6px 40px', border: `11px solid ${cor}`, borderRadius: 24, fontFamily: 'Anton', fontSize: tam, color: cor, letterSpacing: 6, textShadow: neon(cor, 0.5),
      boxShadow: caixaNeon(cor, 0.7), background: 'rgba(40,0,0,0.35)', whiteSpace: 'nowrap'}}>{texto}</div>
  );
};

const Painel: React.FC<{x: number; y: number; w: number; h: number; cor: string; em: number; children?: React.ReactNode; apagado?: number}> = ({x, y, w, h, cor, em, children, apagado = 0}) => {
  const m = useMola(em, {damping: 15});
  return (
    <div style={{position: 'absolute', left: x - w / 2, top: y, width: w, height: h, borderRadius: 32, background: 'rgba(12,4,18,0.85)', border: `3px solid ${cor}`,
      boxShadow: caixaNeon(cor, 1 - apagado * 0.7), transform: `translateY(${(1 - m) * 140}px) scale(${0.85 + 0.15 * m})`, opacity: Math.min(1, m * 1.5) * (1 - apagado * 0.55), overflow: 'hidden'}}>
      {children}
    </div>
  );
};

// N1 bolso x banco (6,47 s): morre@1.38 preso@2.56 some@3.9 banco@5.84
export const BolsoBanco: React.FC = () => {
  const frame = useCurrentFrame();
  const T = {ap: 0.1, morre: 1.35, preso: 2.5, some: 3.85, banco: 5.8};
  const vazio = useRampa(T.some, T.some + 0.9);
  const tranca = useMola(T.banco, {damping: 11});
  const notas = new Array(16).fill(0).map((_, i) => {
    const d = frame - f(T.some + i * 0.03);
    const x0 = 420 + (i % 4) * 30, y0 = 520 + Math.floor(i / 4) * 30;
    if (d < 0) return <Nota key={i} x={x0} y={y0} r={(i % 3 - 1) * 8} s={0.9} />;
    const vx = (random(`nx${i}`) - 0.3) * 22, vy = -18 - random(`ny${i}`) * 14;
    return <Nota key={i} x={x0 + vx * d} y={y0 + vy * d + d * d * 0.9} r={d * (8 + i)} s={0.9} o={Math.max(0, 1 - d / 28)} />;
  });
  return (
    <AbsoluteFill>
      <Fundo tom={COR.verm} />
      <Camera zoom={[1.0, 1.06]} impactos={[T.morre, T.preso, T.banco]}>
        <Titulo texto="ONDE TÁ O SEU DINHEIRO?" em={T.ap} />
        <Painel x={560} y={300} w={620} h={560} cor={COR.rosa} em={T.ap + 0.2} apagado={vazio * 0.4}>
          <div style={{textAlign: 'center', fontFamily: 'Anton', fontSize: 110, color: '#fff', marginTop: 20}}>BOLSO</div>
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 40, textAlign: 'center', fontFamily: 'Anton', fontSize: 120, color: vazio > 0.5 ? COR.verm : COR.rosa}}>
            $ <Conta de={8500} ate={0} a={T.some} b={T.some + 0.9} fmt={brl} />
          </div>
        </Painel>
        {notas}
        <Painel x={1360} y={300} w={620} h={560} cor={COR.ciano} em={T.ap + 0.35}>
          <div style={{textAlign: 'center', fontFamily: 'Anton', fontSize: 110, color: '#fff', marginTop: 20}}>BANCO</div>
          <div style={{position: 'absolute', left: 0, right: 0, top: 210, textAlign: 'center', fontSize: 120, transform: `scale(${tranca})`, filter: `drop-shadow(0 0 20px ${COR.ciano})`}}>🔒</div>
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 40, textAlign: 'center', fontFamily: 'Anton', fontSize: 120, color: COR.ciano}}>$ 3.000</div>
        </Painel>
        <Carimbo em={T.morre} texto="WASTED" x={560} y={560} tam={100} />
        <Carimbo em={T.preso} texto="BUSTED" x={560} y={720} cor={COR.ouro} rot={7} tam={84} />
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 40, textAlign: 'center', fontFamily: 'Mont', fontWeight: 600, fontSize: 26, color: COR.cinza}}>valores ilustrativos</div>
      </Camera>
      <Flash em={[T.morre]} />
    </AbsoluteFill>
  );
};

// N2 custo de morrer (7,34 s): GTA5@0.16 taxinha@1.91 GTA6@3.41 noite inteira@5.23
export const CustoMorrer: React.FC = () => {
  const frame = useCurrentFrame();
  const T = {g5: 0.1, taxa: 1.85, g6: 3.35, noite: 5.15};
  const moeda = useMola(T.taxa, {damping: 9});
  const pilha = new Array(14).fill(0).map((_, i) => {
    const ap = interpolate(frame - f(T.g6 + 0.3 + i * 0.05), [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    const d = frame - f(T.noite + i * 0.06);
    const sobe = d > 0 ? d : 0;
    return <Nota key={i} x={1250 + (i % 2) * 40} y={800 - i * 18 - sobe * (6 + i * 0.6)} r={(i % 3 - 1) * 4 + sobe * (i % 2 ? 3 : -3)} s={1.3} o={ap * Math.max(0, 1 - sobe / 26)} />;
  });
  return (
    <AbsoluteFill>
      <Fundo img="bg_noite.png" tom={COR.rosa} />
      <Camera zoom={[1.0, 1.06]} impactos={[T.noite + 0.2]}>
        <Titulo texto="QUANTO CUSTA MORRER" em={T.g5} />
        <Painel x={520} y={260} w={700} h={640} cor={COR.ciano} em={T.g5 + 0.1}>
          <div style={{textAlign: 'center', fontFamily: 'Anton', fontSize: 130, color: COR.ciano, marginTop: 10, textShadow: neon(COR.ciano, 0.5)}}>GTA 5</div>
          <div style={{position: 'absolute', left: 280, top: 250, width: 140, height: 140, borderRadius: 999, background: 'radial-gradient(circle at 35% 35%, #ffe680, #d4a017)', border: '6px solid #fff3b0',
            transform: `scale(${moeda}) rotateY(${frame * 9}deg)`, boxShadow: '0 0 40px #ffd23f', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Anton', fontSize: 80, color: '#7a5a00'}}>$</div>
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 50, textAlign: 'center', fontFamily: 'Mont', fontWeight: 800, fontSize: 40, color: '#fff', opacity: moeda}}>taxinha de hospital</div>
        </Painel>
        <Painel x={1400} y={260} w={700} h={640} cor={COR.rosa} em={T.g6}>
          <div style={{textAlign: 'center', fontFamily: 'Anton', fontSize: 130, color: COR.rosa, marginTop: 10, textShadow: neon(COR.rosa, 0.5)}}>GTA 6</div>
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 50, textAlign: 'center', fontFamily: 'Mont', fontWeight: 800, fontSize: 40, color: '#fff', opacity: useRampa(T.noite, T.noite + 0.4)}}>a noite inteira de trabalho</div>
        </Painel>
        {pilha}
      </Camera>
    </AbsoluteFill>
  );
};

// barras Pay 'n' Spray x receptador
const CHAO = 920;
const BarraV: React.FC<{x: number; h: number; m: number; cor: string; rotulo: string; valor: React.ReactNode; ap: number; topo?: boolean}> = ({x, h, m, cor, rotulo, valor, ap, topo}) => {
  const frame = useCurrentFrame();
  const hh = h * m;
  return (
    <>
      <div style={{position: 'absolute', left: x - 170, width: 340, top: CHAO - hh, height: hh, borderRadius: '24px 24px 0 0', overflow: 'hidden',
        background: `linear-gradient(180deg, ${cor}, ${cor}99)`, boxShadow: `${caixaNeon(cor, 1.1)}, 0 0 90px ${cor}55`}}>
        <div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(180deg, rgba(255,255,255,0.13) 0 3px, transparent 3px 26px)', transform: `translateY(${(frame * 3) % 26}px)`}} />
      </div>
      <div style={{position: 'absolute', left: x - 300, width: 600, top: CHAO + 22, textAlign: 'center', fontFamily: 'Anton', fontSize: 66, color: '#fff', opacity: ap, textShadow: '0 5px 0 #000'}}>{rotulo}</div>
      <div style={{position: 'absolute', left: x - 420, width: 840, top: topo ? 330 : CHAO - hh - 140, textAlign: 'center', fontFamily: 'Anton', fontSize: topo ? 124 : 104, whiteSpace: 'nowrap', color: '#fff', opacity: Math.min(1, m * 1.5),
        textShadow: `0 8px 0 #000, ${neon(cor, 0.7)}`}}>{valor}</div>
    </>
  );
};

// N3a (13,24 s): Flow Games@1.89 1500@4.36 receptador@8.33 21 mil@10.29 / 12.04
export const VendaCarro: React.FC = () => {
  const T = {fonte: 1.8, b1: 3.4, n1: 4.3, rec: 8.25, b2: 9.6, n2: 10.25, bang: 12.0};
  const m1 = useMola(T.b1, {damping: 15});
  const m2 = useMola(T.b2, {damping: 11, stiffness: 80, mass: 1.3});
  const badge = useMola(T.bang, {damping: 9, stiffness: 170});
  return (
    <AbsoluteFill>
      <Fundo tom={COR.rosa} />
      <Camera zoom={[1.0, 1.07]} impactos={[T.n2 + 0.3, T.bang]} foco={[960, 700]}>
        <div style={{position: 'absolute', left: 140, right: 140, top: CHAO, height: 6, background: '#fff', boxShadow: neon('#fff', 0.5), borderRadius: 4}} />
        <BarraV x={620} h={90} m={m1} cor={COR.ciano} rotulo="PAY 'N' SPRAY" ap={useRampa(T.b1 - 0.3, T.b1)} valor={<>~US$ <Conta de={0} ate={1500} a={T.b1} b={T.n1 + 0.6} fmt={brl} /></>} />
        <BarraV x={1300} h={1200} m={m2} cor={COR.rosa} rotulo="RECEPTADOR" ap={useRampa(T.rec, T.rec + 0.4)} topo valor={<>~US$ <Conta de={0} ate={21000} a={T.b2} b={T.n2 + 0.6} fmt={brl} /></>} />
        <div style={{position: 'absolute', left: 160, top: 300, transform: `scale(${badge}) rotate(-8deg)`, transformOrigin: 'left center', opacity: Math.min(1, badge * 2),
          padding: '14px 36px', borderRadius: 20, background: COR.laranja, boxShadow: caixaNeon(COR.laranja, 1), fontFamily: 'Anton', fontSize: 96, color: COR.roxo}}>14X MAIS</div>
      </Camera>
      <Fonte texto="FONTE: DEMONSTRAÇÃO (CANAL FLOW GAMES)" em={T.fonte} cor={COR.ciano} />
      <Flash em={[T.n2 + 0.25]} />
    </AbsoluteFill>
  );
};

// N3b (6,64 s): "não era o mesmo carro"@1.22  "mostra onde tá o dinheiro"@5.2
export const VendaCarro2: React.FC = () => {
  const frame = useCurrentFrame();
  const seta = useMola(5.1, {damping: 12});
  const apag = useRampa(1.1, 1.6);
  return (
    <AbsoluteFill>
      <Fundo tom={COR.rosa} />
      <Camera zoom={[1.0, 1.04]} foco={[960, 700]}>
        <div style={{position: 'absolute', left: 140, right: 140, top: CHAO, height: 6, background: '#fff', boxShadow: neon('#fff', 0.5), borderRadius: 4}} />
        <div style={{opacity: 1 - apag * 0.35}}>
          <BarraV x={620} h={90} m={1} cor={COR.ciano} rotulo="PAY 'N' SPRAY" ap={1} valor="~US$ 1.500" />
          <BarraV x={1300} h={1200} m={1} cor={COR.rosa} rotulo="RECEPTADOR" ap={1} topo valor="~US$ 21.000" />
        </div>
        <Carimbo em={1.2} texto="NÃO ERA O MESMO CARRO" x={760} y={230} cor={COR.ouro} tam={74} rot={-5} />
        <div style={{position: 'absolute', left: 1490, top: 600 + 14 * Math.sin(frame / 4), transform: `scale(${seta})`, transformOrigin: 'left center', opacity: Math.min(1, seta * 2), fontFamily: 'Anton', fontSize: 56, color: COR.ouro, textShadow: neon(COR.ouro, 0.5)}}>
          ← O DINHEIRO<br />TÁ AQUI
        </div>
      </Camera>
      <Fonte texto="FONTE: DEMONSTRAÇÃO (CANAL FLOW GAMES)" em={-1} cor={COR.ciano} />
    </AbsoluteFill>
  );
};

// N4 regras do receptador (10,97 s): duas regras@0.56 primeira@1.94 batida@4.94 corta@5.54 segunda@7.16 rastreador@8.2 sair@9.78
export const Regras: React.FC = () => {
  const frame = useCurrentFrame();
  const T = {tit: 0.4, r1: 1.9, bat: 4.9, r2: 7.1, rast: 8.15, sai: 9.7};
  const amassa = useRampa(T.bat, T.bat + 0.3);
  const tira = useMola(T.sai, {damping: 12});
  const pulso = frame > f(T.rast) && frame < f(T.sai) ? 0.5 + 0.5 * Math.sin(frame / 2.5) : 0;
  return (
    <AbsoluteFill>
      <Fundo img="bg_noite.png" tom={COR.rosa} />
      <Camera zoom={[1.0, 1.05]} impactos={[T.bat + 0.05, T.bat + 0.6]}>
        <Titulo texto="AS 2 REGRAS DO RECEPTADOR" cor={COR.rosa} em={T.tit} y={70} tam={88} />
        <Painel x={960} y={230} w={1500} h={330} cor={COR.ciano} em={T.r1}>
          <div style={{position: 'absolute', left: 50, top: 40, fontFamily: 'Anton', fontSize: 92, color: '#fff'}}>1. CARRO INTEIRO</div>
          <div style={{position: 'absolute', left: 54, top: 170, fontFamily: 'Mont', fontWeight: 800, fontSize: 40, color: COR.ciano}}>cada batida corta o valor</div>
          <div style={{position: 'absolute', right: 380, top: 60, transform: `skewX(${amassa * -8}deg) scaleY(${1 - amassa * 0.12})`}}><Carro cor={amassa > 0.5 ? COR.laranja : COR.ciano} w={300} vidroQuebrado={amassa} /></div>
          <div style={{position: 'absolute', right: 50, top: 70, fontFamily: 'Anton', fontSize: 84, color: amassa > 0.5 ? COR.verm : '#fff'}}>
            $<Conta de={21000} ate={13500} a={T.bat} b={T.bat + 1.2} fmt={brl} />
          </div>
        </Painel>
        <Painel x={960} y={600} w={1500} h={330} cor={COR.laranja} em={T.r2}>
          <div style={{position: 'absolute', left: 50, top: 40, fontFamily: 'Anton', fontSize: 92, color: '#fff'}}>2. SEM RASTREADOR</div>
          <div style={{position: 'absolute', left: 54, top: 170, fontFamily: 'Mont', fontWeight: 800, fontSize: 40, color: COR.laranja}}>tira antes de vender</div>
          <div style={{position: 'absolute', right: 120, top: 70, width: 190, height: 190, borderRadius: 999, border: `8px solid ${tira > 0.5 ? '#3ddc84' : COR.verm}`,
            boxShadow: caixaNeon(tira > 0.5 ? '#3ddc84' : COR.verm, 0.4 + pulso), display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Anton', fontSize: 110,
            color: tira > 0.5 ? '#3ddc84' : COR.verm, opacity: useRampa(T.rast - 0.2, T.rast)}}>{tira > 0.5 ? '✓' : '📡'}</div>
        </Painel>
      </Camera>
    </AbsoluteFill>
  );
};

// N5a a conta (11,36 s): conta@1.3 um carro da lista@2.82 21 mil@4.69 5 entregas@5.98 100 mil@10.1
export const Conta5: React.FC = () => {
  const frame = useCurrentFrame();
  const T = {tit: 1.1, um: 2.7, cinco: 5.9, cem: 10.0};
  const total = useRampa(T.cinco, T.cem, Easing.inOut(Easing.cubic));
  const cem = useMola(T.cem, {damping: 9, stiffness: 150});
  const carros = new Array(5).fill(0).map((_, i) => {
    const m = useMola(i === 0 ? T.um : T.cinco + i * 0.35, {damping: 14});
    return (
      <div key={i} style={{position: 'absolute', left: 170 + i * 330, top: 420, transform: `translateX(${(1 - m) * 1400}px)`, opacity: Math.min(1, m * 2), textAlign: 'center', width: 300}}>
        <Carro cor={i === 0 ? COR.rosa : COR.ciano} w={280} />
        <div style={{fontFamily: 'Anton', fontSize: 52, color: '#fff', marginTop: 10}}>US$ 21 MIL</div>
      </div>
    );
  });
  const conf = frame > f(T.cem) ? new Array(40).fill(0).map((_, i) => {
    const d = frame - f(T.cem); const a = random(`ca${i}`) * Math.PI * 2, v = 8 + random(`cv${i}`) * 16;
    return <Nota key={i} x={900 + Math.cos(a) * v * d} y={780 + Math.sin(a) * v * d + d * d * 0.5} r={d * 12 + i * 20} s={0.7} o={Math.max(0, 1 - d / 34)} />;
  }) : null;
  return (
    <AbsoluteFill>
      <Fundo tom={COR.ciano} />
      <Camera zoom={[1.0, 1.06]} impactos={[T.cem + 0.05]}>
        <Titulo texto="FAZ A CONTA COMIGO" em={T.tit} />
        {carros}
        <div style={{position: 'absolute', left: 0, right: 0, top: 690, textAlign: 'center', fontFamily: 'Anton', fontSize: 170 + cem * 30, color: total >= 0.999 ? COR.laranja : '#fff',
          opacity: useRampa(T.cinco, T.cinco + 0.4), textShadow: `0 10px 0 #000, ${neon(COR.laranja, 0.4 + cem * 0.6)}`}}>
          US$ {brl(21000 + 84000 * total)}
        </div>
        {conf}
      </Camera>
      <Flash em={[T.cem]} />
    </AbsoluteFill>
  );
};

// N5b 50 lojas x 5 carros (8,15 s): 50 lojas@1.44 chances de morrer@2.76 5 carros@5.46
export const Lojas: React.FC = () => {
  const frame = useCurrentFrame();
  const T = {lojas: 1.35, morte: 2.7, carros: 5.4};
  const lojas = new Array(50).fill(0).map((_, i) => {
    const ap = interpolate(frame - f(T.lojas + i * 0.022), [0, 5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    const caveira = interpolate(frame - f(T.morte + i * 0.02), [0, 4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    return (
      <div key={i} style={{position: 'absolute', left: 140 + (i % 10) * 76, top: 340 + Math.floor(i / 10) * 86, width: 64, height: 70, borderRadius: 10,
        background: caveira > 0.5 ? '#3a0a12' : '#2a1e3a', border: `2px solid ${caveira > 0.5 ? COR.verm : COR.cinza}`, transform: `scale(${ap})`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 40 * caveira}}>{caveira > 0.05 ? '💀' : ''}</div>
    );
  });
  const carros = new Array(5).fill(0).map((_, i) => {
    const m = useMola(T.carros + i * 0.18, {damping: 13});
    return <div key={i} style={{position: 'absolute', left: 1180, top: 330 + i * 92, transform: `translateX(${(1 - m) * 900}px)`, opacity: m}}><Carro cor={COR.ciano} w={190} /></div>;
  });
  return (
    <AbsoluteFill>
      <Fundo img="bg_noite.png" tom={COR.verm} />
      <Camera zoom={[1.0, 1.05]}>
        <div style={{position: 'absolute', left: 140, top: 150, fontFamily: 'Anton', fontSize: 92, color: '#fff', opacity: useRampa(T.lojas - 0.2, T.lojas + 0.2)}}>50 LOJAS</div>
        <div style={{position: 'absolute', left: 140, top: 260, fontFamily: 'Mont', fontWeight: 800, fontSize: 38, color: COR.verm, opacity: useRampa(T.morte, T.morte + 0.3)}}>50 chances de morrer</div>
        {lojas}
        <div style={{position: 'absolute', left: 945, top: 300, fontFamily: 'Anton', fontSize: 120, color: COR.ouro, opacity: useRampa(T.carros - 0.3, T.carros), textShadow: neon(COR.ouro, 0.5)}}>OU</div>
        <div style={{position: 'absolute', left: 1180, top: 150, fontFamily: 'Anton', fontSize: 92, color: COR.ciano, opacity: useRampa(T.carros, T.carros + 0.3), textShadow: neon(COR.ciano, 0.4)}}>5 CARROS</div>
        <div style={{position: 'absolute', left: 1180, top: 260, fontFamily: 'Mont', fontWeight: 800, fontSize: 38, color: '#fff', opacity: useRampa(T.carros + 1.2, T.carros + 1.6)}}>entregues com carinho 💗</div>
        {carros}
        <div style={{position: 'absolute', left: 140, bottom: 60, fontFamily: 'Mont', fontWeight: 600, fontSize: 26, color: COR.cinza}}>loja ≈ US$ 2 mil: palpite de um jornalista, não da Rockstar</div>
      </Camera>
    </AbsoluteFill>
  );
};
