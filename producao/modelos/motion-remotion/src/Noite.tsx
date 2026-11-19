// Blocos 9-10: garagem de 3 vagas, perfil criminal
import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {Camera, caixaNeon, COR, f, Flash, Fonte, Fundo, neon, Revela, useMola, useRampa} from './base';

// carro visto de cima
const CarroCima: React.FC<{cor: string}> = ({cor}) => (
  <div style={{width: 170, height: 300, borderRadius: 50, background: `linear-gradient(180deg, ${cor}, ${cor}AA)`, boxShadow: caixaNeon(cor, 0.8), position: 'relative'}}>
    <div style={{position: 'absolute', left: 22, right: 22, top: 60, height: 70, borderRadius: 18, background: '#0c0410cc'}} />
    <div style={{position: 'absolute', left: 22, right: 22, bottom: 50, height: 55, borderRadius: 16, background: '#0c0410cc'}} />
  </div>
);

// N6 garagem (5,08 s): prévias@0.2 começa@1.62 3 carros@3.42 só@4.53
export const Garagem: React.FC = () => {
  const frame = useCurrentFrame();
  const T = {ap: 0.2, v: 1.5, c: 3.0, so: 4.45};
  const vaga = (i: number) => {
    const m = useMola(T.v + i * 0.12);
    const c = useMola(T.c + i * 0.15, {damping: 15});
    const x = 330 + i * 420;
    return (
      <div key={i}>
        <div style={{position: 'absolute', left: x - 140, top: 300, width: 280, height: 470, border: `5px dashed ${COR.ciano}`, borderBottom: 'none', borderRadius: '16px 16px 0 0', opacity: m, boxShadow: `inset 0 0 30px ${COR.ciano}33`}} />
        <div style={{position: 'absolute', left: x - 85, top: 380 + (1 - c) * 700, opacity: c}}><CarroCima cor={COR.rosa} /></div>
      </div>
    );
  };
  const quarto = useMola(T.so, {damping: 10});
  const buzina = frame > f(T.so + 0.3) && Math.floor(frame / 4) % 2 === 0;
  return (
    <AbsoluteFill>
      <Fundo img="bg_noite.png" tom={COR.ciano} grade={false} />
      <Camera zoom={[1.0, 1.05]} impactos={[T.so + 0.3]}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 150, display: 'flex', justifyContent: 'center'}}>
          <Revela texto="SUA GARAGEM NO COMEÇO" em={T.ap} style={{fontFamily: 'Anton', fontSize: 92, color: '#fff', textShadow: '0 7px 0 #000'}} />
        </div>
        {[0, 1, 2].map(vaga)}
        <div style={{position: 'absolute', left: 1590 - 85, top: 420 + (1 - quarto) * 600, opacity: quarto, transform: `rotate(${(1 - quarto) * 10}deg)`}}><CarroCima cor={COR.verm} /></div>
        {buzina && <div style={{position: 'absolute', left: 1500, top: 340, fontFamily: 'Anton', fontSize: 60, color: COR.ouro}}>BI-BI!</div>}
        <div style={{position: 'absolute', left: 1590 - 200, top: 790, width: 400, textAlign: 'center', fontFamily: 'Anton', fontSize: 80, color: COR.verm, opacity: quarto, textShadow: neon(COR.verm, 0.5)}}>NÃO CABE</div>
        <div style={{position: 'absolute', left: 330 - 140, top: 800, width: 1120, textAlign: 'center', fontFamily: 'Anton', fontSize: 80, color: COR.ciano, opacity: useRampa(T.c + 0.4, T.c + 0.8), textShadow: neon(COR.ciano, 0.4)}}>≈ 3 VAGAS</div>
      </Camera>
      <Fonte texto="FONTE: PRÉVIAS DA IMPRENSA" em={T.ap} cor={COR.ciano} />
    </AbsoluteFill>
  );
};

// N7 perfil criminal (17,42 s): perfil@2.74 honra RDR2@5.66 serviço limpo@10.0 profissional@12.16 sai matando@13.48 outra coisa@16.6
export const Perfil: React.FC = () => {
  const frame = useCurrentFrame();
  const T = {perfil: 2.6, honra: 5.5, limpo: 9.9, prof: 12.1, mata: 13.4, outra: 16.5};
  const ap = useMola(T.perfil - 0.2, {damping: 15});
  const vaiDir = useRampa(T.limpo, T.prof, Easing.inOut(Easing.cubic));
  const vaiEsq = useRampa(T.mata, T.mata + 1.6, Easing.inOut(Easing.cubic));
  const pos = 0.5 + 0.38 * vaiDir - 0.75 * vaiEsq + 0.008 * Math.sin(frame / 3);
  const prof = useMola(T.prof, {damping: 10});
  const outra = useMola(T.outra, {damping: 9});
  const glitch = frame > f(T.outra) && frame < f(T.outra + 0.5) ? (frame % 3) * 6 - 6 : 0;
  const x0 = 260, W = 1400;
  return (
    <AbsoluteFill>
      <Fundo tom={vaiEsq > 0.5 ? COR.verm : COR.ciano} />
      <Camera zoom={[1.0, 1.06]} impactos={[T.outra]}>
        <div style={{position: 'absolute', left: 0, right: 0, top: 120, display: 'flex', justifyContent: 'center'}}>
          <Revela texto="PERFIL CRIMINAL" em={T.perfil - 0.3} style={{fontFamily: 'Anton', fontSize: 130, color: '#fff', textShadow: '0 8px 0 #000'}} />
        </div>
        <div style={{position: 'absolute', left: 0, right: 0, top: 290, textAlign: 'center', fontFamily: 'Mont', fontWeight: 800, fontSize: 40, color: COR.ouro, opacity: useRampa(T.honra, T.honra + 0.4)}}>
          tipo a honra do Red Dead 2
        </div>
        <div style={{position: 'absolute', left: x0, top: 480, width: W, height: 90, borderRadius: 50, border: '6px solid #fff', boxShadow: neon('#fff', 0.3), opacity: ap, transform: `scaleX(${ap})`, overflow: 'hidden',
          background: `linear-gradient(90deg, ${COR.verm}, #8a2a6a 50%, ${COR.ciano})`}}>
          <div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(90deg, rgba(0,0,0,0.35) 0 4px, transparent 4px 36px)'}} />
        </div>
        <div style={{position: 'absolute', left: x0 + W * pos - 40, top: 380, width: 80, height: 0, borderLeft: '40px solid transparent', borderRight: '40px solid transparent',
          borderTop: '70px solid #fff', opacity: ap, filter: 'drop-shadow(0 0 12px #fff)'}} />
        <div style={{position: 'absolute', left: x0, top: 600, fontFamily: 'Anton', fontSize: 56, color: COR.verm, opacity: ap}}>SAI MATANDO</div>
        <div style={{position: 'absolute', left: x0 + W - 420, width: 420, textAlign: 'right', top: 600, fontFamily: 'Anton', fontSize: 56, color: COR.ciano, opacity: ap}}>SERVIÇO LIMPO</div>
        <div style={{position: 'absolute', left: 0, right: 0, top: 740, textAlign: 'center', fontFamily: 'Anton', fontSize: 150, color: COR.ciano, opacity: prof * (1 - vaiEsq),
          transform: `scale(${prof})`, textShadow: `0 8px 0 #000, ${neon(COR.ciano, 0.7)}`}}>PROFISSIONAL</div>
        <div style={{position: 'absolute', left: glitch, right: -glitch, top: 740, textAlign: 'center', fontFamily: 'Anton', fontSize: 150, color: COR.verm, opacity: outra,
          transform: `scale(${outra})`, textShadow: `${glitch}px 0 0 ${COR.ciano}, 0 8px 0 #000, ${neon(COR.verm, 0.7)}`}}>OUTRA COISA</div>
      </Camera>
      <Flash em={[T.outra]} />
    </AbsoluteFill>
  );
};
