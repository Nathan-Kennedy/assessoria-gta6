// M5: app do celular escaneando o carro; o rastreador fica vermelho e "te entrega" (10,26 s)
import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';
import {Camera, caixaNeon, Conta, COR, f, Flash, Fundo, neon, useMola, useRampa, Etiqueta} from './base';
import {Carro} from './Icones';

const T = {app: 0.55, scan: 1.2, alarme: 2.9, vale: 4.05, importa: 5.2, rastr: 7.4, entrega: 9.55};

const Linha: React.FC<{y: number; em: number; rotulo: string; valor: React.ReactNode; cor: string; alerta?: boolean}> = ({y, em, rotulo, valor, cor, alerta}) => {
  const frame = useCurrentFrame();
  const m = useMola(em, {damping: 16});
  const pisca = alerta && frame > f(em) ? 0.6 + 0.4 * Math.sin((frame - f(em)) / 2.2) : 1;
  return (
    <div style={{position: 'absolute', left: 40, right: 40, top: y, height: 92, borderRadius: 18, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 28px',
      background: alerta ? `rgba(255,45,45,${0.18 * pisca})` : 'rgba(255,255,255,0.05)', border: `2px solid ${alerta ? COR.verm : '#ffffff22'}`,
      boxShadow: alerta ? caixaNeon(COR.verm, pisca) : 'none', transform: `translateX(${(1 - m) * 500}px)`, opacity: m}}>
      <span style={{fontFamily: 'Mont', fontWeight: 800, fontSize: 30, color: '#fff', letterSpacing: 2}}>{rotulo}</span>
      <span style={{fontFamily: 'Anton', fontSize: 46, color: cor, textShadow: neon(cor, 0.4)}}>{valor}</span>
    </div>
  );
};

export const App: React.FC = () => {
  const frame = useCurrentFrame();
  const sobe = useMola(T.app, {damping: 15, stiffness: 110});
  const zoomImp = useRampa(T.importa, T.importa + 1.4, Easing.inOut(Easing.cubic));
  const scanP = useRampa(T.scan, T.alarme, Easing.linear);
  const varre = ((frame - f(T.scan)) % 40) / 40;
  const alerta = frame >= f(T.rastr);
  const giro = interpolate(sobe, [0, 1], [-35, -12]) + zoomImp * 10;
  const anel = (k: number) => {
    const d = (frame - f(T.rastr) - k * 12) % 36;
    return alerta && d >= 0 ? <div key={k} style={{position: 'absolute', left: 230 - d * 7, top: 300 - d * 7, width: d * 14, height: d * 14, borderRadius: 999, border: `4px solid ${COR.verm}`, opacity: 1 - d / 36}} /> : null;
  };
  const entrega = useMola(T.entrega, {damping: 10, stiffness: 170});
  return (
    <AbsoluteFill>
      <Fundo tom={alerta ? COR.verm : COR.ciano} />
      {alerta && <AbsoluteFill style={{background: `radial-gradient(ellipse at center, transparent 40%, rgba(255,0,30,${0.25 + 0.15 * Math.sin(frame / 3)}) 100%)`}} />}
      <Camera zoom={[1.0 + zoomImp * 0.08, 1.04 + zoomImp * 0.08]} impactos={[T.rastr + 0.1, T.entrega]} foco={[1000, 540]}>
        {/* texto lateral */}
        <div style={{position: 'absolute', left: 200, top: 300, width: 620, opacity: useRampa(T.app, T.app + 0.5)}}>
          <div style={{fontFamily: 'Anton', fontSize: 96, color: '#fff', lineHeight: 1, textShadow: '0 6px 0 #000'}}>APP DO</div>
          <div style={{fontFamily: 'Anton', fontSize: 96, color: COR.ciano, lineHeight: 1, textShadow: `0 6px 0 #000, ${neon(COR.ciano, 0.5)}`}}>CELULAR</div>
          <div style={{fontFamily: 'Mont', fontWeight: 700, fontSize: 32, color: COR.cinza, marginTop: 16}}>escaneia o carro antes do roubo</div>
        </div>
        {/* celular */}
        <div style={{position: 'absolute', left: 1040, top: 1080 - sobe * 990, width: 540, height: 900, perspective: 1600}}>
          <div style={{width: '100%', height: '100%', transform: `rotateY(${giro}deg) rotateX(6deg)`, transformStyle: 'preserve-3d', borderRadius: 70, background: '#07030a',
            border: `6px solid ${alerta ? COR.verm : COR.ciano}`, boxShadow: `${caixaNeon(alerta ? COR.verm : COR.ciano, 1.1)}, 30px 40px 80px rgba(0,0,0,0.7)`, overflow: 'hidden'}}>
            <div style={{position: 'absolute', left: 200, top: 20, width: 160, height: 34, borderRadius: 99, background: '#000'}} />
            <div style={{position: 'absolute', left: 0, right: 0, top: 86, textAlign: 'center', fontFamily: 'Anton', fontSize: 48, color: COR.ciano, letterSpacing: 3}}>CAR SCAN</div>
            {/* área do scan */}
            <div style={{position: 'absolute', left: 40, right: 40, top: 170, height: 260, borderRadius: 24, border: '2px solid #ffffff22', overflow: 'hidden', background: 'rgba(25,227,211,0.05)'}}>
              <div style={{position: 'absolute', left: 60, top: 70}}><Carro cor={alerta ? COR.verm : COR.ciano} w={340} /></div>
              {anel(0)}{anel(1)}{anel(2)}
              {scanP < 1 && <div style={{position: 'absolute', left: 0, right: 0, top: varre * 260, height: 6, background: COR.ciano, boxShadow: `0 0 24px 8px ${COR.ciano}`}} />}
              <div style={{position: 'absolute', left: 14, bottom: 10, fontFamily: 'Mont', fontWeight: 800, fontSize: 22, color: '#fff', opacity: 0.8}}>
                {scanP < 1 ? `ESCANEANDO ${Math.round(scanP * 100)}%` : alerta ? '⚠ SINAL DETECTADO' : 'SCAN COMPLETO'}
              </div>
            </div>
            <Linha y={470} em={T.alarme} rotulo="ALARME" valor="SIM" cor={COR.laranja} />
            <Linha y={580} em={T.vale} rotulo="VALOR" valor={<>$ <Conta de={0} ate={48500} a={T.vale} b={T.vale + 1.0} fmt={(n) => Math.round(n).toLocaleString('pt-BR')} /></>} cor={COR.ciano} />
            <Linha y={690} em={T.rastr} rotulo="RASTREADOR" valor="SIM" cor={COR.verm} alerta />
            <div style={{position: 'absolute', left: 0, right: 0, bottom: 40, textAlign: 'center', fontFamily: 'Mont', fontWeight: 600, fontSize: 22, color: COR.cinza}}>ilustração · valores fictícios</div>
          </div>
        </div>
        {/* TE ENTREGA */}
        <div style={{position: 'absolute', left: 200, top: 640, transform: `scale(${entrega}) rotate(-6deg)`, transformOrigin: 'left center', opacity: Math.min(1, entrega * 2),
          padding: '10px 34px', borderRadius: 20, background: COR.verm, boxShadow: caixaNeon(COR.verm, 1.2), fontFamily: 'Anton', fontSize: 92, color: '#fff'}}>
          ELE TE ENTREGA
        </div>
      </Camera>
      <Flash em={[T.rastr]} />
    </AbsoluteFill>
  );
};
