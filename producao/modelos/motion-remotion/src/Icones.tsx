import React from 'react';

export const Carro: React.FC<{cor: string; w?: number; vidroQuebrado?: number}> = ({cor, w = 300, vidroQuebrado = 0}) => (
  <svg width={w} height={w * 0.42} viewBox="0 0 300 126" style={{filter: `drop-shadow(0 0 10px ${cor})`}}>
    <path d="M18 92 L30 64 Q36 54 50 52 L92 48 L122 22 Q130 16 142 16 L196 16 Q210 16 220 26 L246 50 L272 56 Q288 60 290 74 L292 92 Z" fill="none" stroke={cor} strokeWidth={6} strokeLinejoin="round" />
    <path d="M104 48 L128 26 L168 26 L168 48 Z M178 48 L178 26 L206 26 L230 48 Z" fill={`${cor}33`} stroke={cor} strokeWidth={4} />
    {vidroQuebrado > 0 && <path d="M150 30 L140 40 M150 30 L160 44 M150 30 L156 22 M150 30 L136 28" stroke="#fff" strokeWidth={3} opacity={vidroQuebrado} />}
    <circle cx={78} cy={96} r={20} fill="#120614" stroke={cor} strokeWidth={6} />
    <circle cx={236} cy={96} r={20} fill="#120614" stroke={cor} strokeWidth={6} />
  </svg>
);

export const Chave: React.FC<{cor: string; s?: number; eletronica?: boolean}> = ({cor, s = 120, eletronica}) => (
  <svg width={s} height={s} viewBox="0 0 100 100" style={{filter: `drop-shadow(0 0 8px ${cor})`}}>
    {eletronica ? (
      <>
        <rect x={30} y={10} width={40} height={64} rx={14} fill="none" stroke={cor} strokeWidth={6} />
        <circle cx={50} cy={32} r={7} fill={cor} />
        <rect x={42} y={48} width={16} height={10} rx={3} fill={cor} />
        <path d="M76 20 Q88 32 76 44 M84 12 Q102 32 84 52" fill="none" stroke={cor} strokeWidth={4} strokeLinecap="round" />
      </>
    ) : (
      <>
        <circle cx={30} cy={50} r={18} fill="none" stroke={cor} strokeWidth={7} />
        <path d="M48 50 L92 50 M80 50 L80 64 M68 50 L68 60" stroke={cor} strokeWidth={7} strokeLinecap="round" />
      </>
    )}
  </svg>
);

export const Raio: React.FC<{cor: string; s?: number}> = ({cor, s = 110}) => (
  <svg width={s} height={s} viewBox="0 0 100 100" style={{filter: `drop-shadow(0 0 10px ${cor})`}}>
    <path d="M58 6 L22 56 L48 56 L40 94 L80 40 L54 40 Z" fill={cor} />
  </svg>
);

export const Lamina: React.FC<{cor: string; s?: number}> = ({cor, s = 110}) => (
  <svg width={s} height={s} viewBox="0 0 100 100" style={{filter: `drop-shadow(0 0 8px ${cor})`}}>
    <path d="M10 80 L80 10 L90 20 L20 90 Z" fill="none" stroke={cor} strokeWidth={6} strokeLinejoin="round" />
    <path d="M14 76 L24 86" stroke={cor} strokeWidth={10} />
  </svg>
);

export const Bomba: React.FC<{cor: string; s?: number}> = ({cor, s = 80}) => (
  <svg width={s} height={s} viewBox="0 0 100 100" style={{filter: `drop-shadow(0 0 8px ${cor})`}}>
    <rect x={18} y={14} width={44} height={76} rx={6} fill="none" stroke={cor} strokeWidth={7} />
    <rect x={26} y={24} width={28} height={20} rx={3} fill={cor} />
    <path d="M62 34 L76 44 L76 76 Q76 84 84 84 Q90 84 90 76 L90 40 L80 30" fill="none" stroke={cor} strokeWidth={6} strokeLinejoin="round" />
  </svg>
);
