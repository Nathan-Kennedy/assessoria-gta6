// Blocos 5-6: armas no corpo, HUD da polícia (ícones + estrela vazada), checklist troca/larga/separa
import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {Camera, caixaNeon, COR, f, Flash, Fonte, Fundo, neon, Revela, useMola, useRampa} from './base';

const Pistola: React.FC<{cor: string; s?: number}> = ({cor, s = 120}) => (
  <svg width={s} height={s * 0.7} viewBox="0 0 120 84" style={{filter: `drop-shadow(0 0 8px ${cor})`}}>
    <path d="M6 14 L104 14 L112 22 L112 32 L52 32 L46 40 L40 76 L18 76 L24 40 L6 32 Z" fill="none" stroke={cor} strokeWidth={6} strokeLinejoin="round" />
    <path d="M52 32 Q56 50 66 46" fill="none" stroke={cor} strokeWidth={5} />
  </svg>
);
const Fuzil: React.FC<{cor: string; s?: number}> = ({cor, s = 260}) => (
  <svg width={s} height={s * 0.32} viewBox="0 0 260 84" style={{filter: `drop-shadow(0 0 8px ${cor})`}}>
    <path d="M4 26 L60 26 L70 18 L190 18 L190 26 L254 26 L254 34 L190 34 L176 44 L120 44 L112 70 L94 70 L100 44 L70 44 L52 62 L20 62 L28 40 L4 40 Z" fill="none" stroke={cor} strokeWidth={5} strokeLinejoin="round" />
  </svg>
);
const Olho: React.FC<{cor: string; fechado?: boolean}> = ({cor, fechado}) => (
  <svg width={70} height={44} viewBox="0 0 70 44">
    <path d="M4 22 Q35 -6 66 22 Q35 50 4 22 Z" fill="none" stroke={cor} strokeWidth={5} />
    <circle cx={35} cy={22} r={8} fill={cor} />
    {fechado && <line x1={8} y1={40} x2={62} y2={4} stroke={cor} strokeWidth={6} />}
  </svg>
);

const Cartao: React.FC<{x: number; em: number; cor: string; titulo: string; status: string; olho?: 'ab' | 'fe'; children: React.ReactNode}> = ({x, em, cor, titulo, status, olho, children}) => {
  const frame = useCurrentFrame();
  const m = useMola(em, {damping: 14});
  const brilho = olho === 'ab' ? 0.6 + 0.4 * Math.sin((frame - f(em)) / 3) : 1;
  return (
    <div style={{position: 'absolute', left: x - 270, top: 300, width: 540, height: 560, borderRadius: 34, background: 'rgba(12,4,18,0.86)', border: `3px solid ${cor}`,
      boxShadow: caixaNeon(cor, brilho), transform: `translateY(${(1 - m) * 160}px) scale(${0.85 + 0.15 * m})`, opacity: Math.min(1, m * 1.5)}}>
      <div style={{height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16}}>{children}</div>
      <div style={{textAlign: 'center', fontFamily: 'Anton', fontSize: 70, color: '#fff'}}>{titulo}</div>
      <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 14, marginTop: 18}}>
        {olho && <Olho cor={cor} fechado={olho === 'fe'} />}
        <span style={{fontFamily: 'Mont', fontWeight: 900, fontSize: 40, color: cor, letterSpacing: 2}}>{status}</span>
      </div>
    </div>
  );
};

// O1 armas (11,16 s): 6@0.59 Nelson@1.61 2 pistolas@2.75 escondidas@3.41 2 armas grandes@4.71 à mostra@7.85 resto@8.77 porta-malas@9.61
export const Armas: React.FC = () => {
  const T = {tit: 0.3, nelson: 1.5, pist: 2.7, grandes: 4.65, mostra: 7.8, resto: 8.7, malas: 9.55};
  const p2 = useMola(T.pist + 0.15), g2 = useMola(T.grandes + 0.2);
  const tampa = useRampa(T.malas, T.malas + 0.6, Easing.out(Easing.back(1.6)));
  return (
    <AbsoluteFill>
      <Fundo tom={COR.laranja} />
      <Camera zoom={[1.0, 1.05]} impactos={[T.mostra + 0.1]}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 120, display: 'flex', justifyContent: 'center'}}>
          <Revela texto="QUANTO DÁ PRA CARREGAR" em={T.tit} style={{fontFamily: 'Anton', fontSize: 92, color: '#fff', textShadow: '0 7px 0 #000'}} />
        </div>
        <Cartao x={360} em={T.pist} cor={COR.ciano} titulo="2 PISTOLAS" status={'ESCONDIDAS'} olho="fe">
          <Pistola cor={COR.ciano} /><div style={{opacity: p2, transform: `scale(${p2})`}}><Pistola cor={COR.ciano} /></div>
        </Cartao>
        <Cartao x={960} em={T.grandes} cor={COR.laranja} titulo="2 ARMAS GRANDES" status={useRampa(T.mostra, T.mostra + 0.2) > 0.5 ? 'À MOSTRA' : '...'} olho={useRampa(T.mostra, T.mostra + 0.2) > 0.5 ? 'ab' : undefined}>
          <div style={{display: 'flex', flexDirection: 'column', gap: 18}}><Fuzil cor={COR.laranja} /><div style={{opacity: g2, transform: `translateX(${(1 - g2) * 200}px)`}}><Fuzil cor={COR.laranja} /></div></div>
        </Cartao>
        <Cartao x={1560} em={T.resto} cor={COR.rosa} titulo="O RESTO" status="NO PORTA-MALAS">
          <div style={{position: 'relative', width: 300, height: 200}}>
            <div style={{position: 'absolute', left: 20, right: 20, bottom: 10, height: 110, borderRadius: 16, border: `6px solid ${COR.rosa}`, boxShadow: caixaNeon(COR.rosa, 0.5)}} />
            <div style={{position: 'absolute', left: 30, bottom: 34, transform: 'scale(0.55)', transformOrigin: 'left bottom', opacity: tampa}}><Fuzil cor={COR.rosa} /></div>
            <div style={{position: 'absolute', left: 20, right: 20, bottom: 120, height: 16, borderRadius: 8, background: COR.rosa, transformOrigin: 'left bottom', transform: `rotate(${-tampa * 38}deg)`}} />
          </div>
        </Cartao>
      </Camera>
      <Fonte texto="FONTE: ROB NELSON" em={T.nelson} />
    </AbsoluteFill>
  );
};

const Estrela: React.FC<{x: number; y: number; r: number; acesa: number; vazada: number; i: number}> = ({x, y, r, acesa, vazada, i}) => {
  const pts = new Array(10).fill(0).map((_, k) => {
    const rr = k % 2 === 0 ? r : r * 0.45, a = Math.PI * k / 5;
    return `${x + rr * Math.sin(a)},${y - rr * Math.cos(a)}`;
  }).join(' ');
  return <polygon points={pts} fill={vazada > 0.5 ? 'none' : `rgba(255,255,255,${0.15 + 0.85 * acesa})`} stroke="#fff" strokeWidth={vazada > 0.5 ? 7 : 3}
    strokeDasharray={vazada > 0.5 ? '14 10' : undefined} style={{filter: `drop-shadow(0 0 ${8 + 14 * acesa}px rgba(255,255,255,0.9))`}} transform={`rotate(${0} ${x} ${y})`} key={i} />;
};

// O2 HUD da polícia (16,57 s)
export const Policia: React.FC = () => {
  const frame = useCurrentFrame();
  const T = {vem: 1.0, icones: 2.65, sabe: 5.1, ign: 7.9, vazada: 10.15, crime: 12.4, quem: 14.4, mane: 15.75};
  const sirene = frame > f(T.vem) ? Math.sin(frame / 3) : 0;
  const vazada = useRampa(T.vazada, T.vazada + 0.3);
  const icone = (k: number, t: string, cor: string) => {
    const m = useMola(T.icones + 0.35 + k * 0.3, {damping: 12});
    return (
      <div key={t} style={{width: 330, height: 130, borderRadius: 24, border: `4px solid ${cor}`, background: 'rgba(12,4,18,0.85)', boxShadow: caixaNeon(cor, 0.9),
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Anton', fontSize: 70, color: '#fff', transform: `scale(${m}) translateY(${(1 - m) * 60}px)`, opacity: Math.min(1, m * 2)}}>{t}</div>
    );
  };
  const crime = useMola(T.crime, {damping: 13}), quem = useMola(T.quem, {damping: 13}), mane = useMola(T.mane, {damping: 9});
  const sumirIcones = useRampa(T.vazada - 0.3, T.vazada);
  return (
    <AbsoluteFill>
      <Fundo img="bg_noite.png" tom={sirene > 0 ? COR.verm : '#3a6cff'} />
      <AbsoluteFill style={{background: `linear-gradient(90deg, rgba(255,30,60,${0.18 * Math.max(0, sirene)}) 0%, transparent 40%, transparent 60%, rgba(40,90,255,${0.18 * Math.max(0, -sirene)}) 100%)`}} />
      <Camera zoom={[1.0, 1.06]} impactos={[T.vem, T.vazada]}>
        <svg width="1920" height="1080" style={{position: 'absolute'}}>
          {[0, 1, 2, 3, 4].map((k) => {
            const acesa = interpolate(frame - f(T.vem + k * 0.18), [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
            return <Estrela key={k} i={k} x={560 + k * 200} y={250} r={85} acesa={acesa} vazada={vazada} />;
          })}
        </svg>
        <div style={{position: 'absolute', left: 0, right: 0, top: 410, textAlign: 'center', fontFamily: 'Anton', fontSize: 66, color: '#fff', opacity: useRampa(T.sabe, T.sabe + 0.4) * (1 - sumirIcones)}}>O QUE A POLÍCIA SABE SOBRE VOCÊ</div>
        <div style={{position: 'absolute', left: 0, right: 0, top: 530, display: 'flex', justifyContent: 'center', gap: 50, opacity: 1 - sumirIcones}}>
          {icone(0, 'ROUPA', COR.rosa)}{icone(1, 'CARRO', COR.ciano)}{icone(2, 'DUPLA', COR.laranja)}
        </div>
        <div style={{position: 'absolute', left: 0, right: 0, top: 400, textAlign: 'center', fontFamily: 'Anton', fontSize: 130, color: COR.rosa, opacity: vazada,
          transform: `scale(${0.8 + 0.2 * vazada})`, textShadow: `0 8px 0 #000, ${neon(COR.rosa, 0.7)}`}}>ESTRELA VAZADA</div>
        <div style={{position: 'absolute', left: 300, top: 620, width: 620, padding: '22px 0', textAlign: 'center', borderRadius: 24, border: `4px solid #3ddc84`, boxShadow: caixaNeon('#3ddc84', 0.7),
          background: 'rgba(12,4,18,0.85)', fontFamily: 'Anton', fontSize: 58, color: '#3ddc84', transform: `scale(${crime})`, opacity: crime}}>✓ SABEM DO CRIME</div>
        <div style={{position: 'absolute', left: 1000, top: 620, width: 620, padding: '22px 0', textAlign: 'center', borderRadius: 24, border: `4px solid ${COR.verm}`, boxShadow: caixaNeon(COR.verm, 0.7),
          background: 'rgba(12,4,18,0.85)', fontFamily: 'Anton', fontSize: 58, color: COR.verm, transform: `scale(${quem})`, opacity: quem}}>✕ NÃO SABEM QUEM</div>
        <div style={{position: 'absolute', left: 0, right: 0, top: 820, textAlign: 'center', fontFamily: 'Anton', fontSize: 84, color: COR.ouro, transform: `scale(${mane}) rotate(${-4 * mane}deg)`,
          opacity: mane, textShadow: `0 6px 0 #000, ${neon(COR.ouro, 0.5)}`}}>(O ZÉ MANÉ)</div>
      </Camera>
      <Fonte texto="FONTE: IGN" em={T.ign} />
      <Flash em={[T.vazada]} />
    </AbsoluteFill>
  );
};

// O3 checklist (12,07 s): roupa?@2.83 troca@3.93 carro?@4.75 larga@6.07 dois?@6.99 separa@9.47 Jason@10.17 Lucia@10.97
export const Checklist: React.FC = () => {
  const T = {tit: 0.3, q: [2.75, 4.7, 6.95], r: [3.9, 6.0, 9.4], jason: 10.1, lucia: 10.9};
  const linhas: [string, string][] = [['SABEM A ROUPA?', 'TROCA'], ['SABEM O CARRO?', 'LARGA'], ['ERAM DOIS?', 'SEPARA']];
  const sep = useRampa(T.jason - 0.2, T.lucia + 0.4, Easing.inOut(Easing.cubic));
  const duo = useMola(T.r[2] - 0.2);
  return (
    <AbsoluteFill>
      <Fundo img="bg_noite.png" tom={COR.ciano} />
      <Camera zoom={[1.0, 1.05]} impactos={T.r}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 90, display: 'flex', justifyContent: 'center'}}>
          <Revela texto="O JOGO TE DIZ O QUE FAZER" em={T.tit} style={{fontFamily: 'Anton', fontSize: 92, color: '#fff', textShadow: '0 7px 0 #000'}} />
        </div>
        {linhas.map(([q, r], k) => {
          const mq = useMola(T.q[k], {damping: 15});
          const frame = useCurrentFrame();
          const d = frame - f(T.r[k]);
          const sr = interpolate(d, [0, 5, 9], [2.2, 0.94, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
          const risca = interpolate(d, [2, 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const y = 290 + k * 200;
          return (
            <div key={k}>
              <div style={{position: 'absolute', left: 170, top: y, fontFamily: 'Anton', fontSize: 92, color: risca > 0.5 ? COR.cinza : '#fff', opacity: mq, transform: `translateX(${(1 - mq) * -300}px)`}}>
                {q}
                <div style={{position: 'absolute', left: -10, right: -10, top: '52%', height: 9, background: COR.verm, transformOrigin: 'left', transform: `scaleX(${risca})`, borderRadius: 4}} />
              </div>
              {d >= 0 && (
                <div style={{position: 'absolute', left: 1060, top: y - 4, width: 460, height: 130, borderRadius: 26, background: COR.ciano, boxShadow: caixaNeon(COR.ciano, 1),
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 18, fontFamily: 'Anton', fontSize: 84, color: COR.roxo, transform: `scale(${sr}) rotate(-3deg)`}}>
                  ✓ {r}
                </div>
              )}
            </div>
          );
        })}
        {/* Jason e Lucia se separando */}
        <div style={{position: 'absolute', left: 0, right: 0, top: 900, height: 120, opacity: duo}}>
          {[['JASON', COR.ciano, -1], ['LUCIA', COR.rosa, 1]].map(([n, c, s]) => (
            <div key={n as string} style={{position: 'absolute', left: 960 - 150 + (s as number) * (90 + sep * 420), top: 0, width: 300, height: 100, borderRadius: 999, border: `4px solid ${c}`,
              boxShadow: caixaNeon(c as string, 0.8), background: 'rgba(12,4,18,0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Anton', fontSize: 56, color: '#fff'}}>{n}</div>
          ))}
        </div>
      </Camera>
    </AbsoluteFill>
  );
};
