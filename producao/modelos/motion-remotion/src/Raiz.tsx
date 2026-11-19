import React from 'react';
import {Composition} from 'remotion';
import {Fontes} from './base';
import {Barras} from './Barras';
import {Fuso} from './Fuso';
import {SplitAntigo, SplitNovo} from './Split';
import {App} from './App';
import {GasolinaA, GasolinaB, GasolinaC} from './Gasolina';
import {BolsoBanco, CustoMorrer, VendaCarro, VendaCarro2, Regras, Conta5, Lojas} from './Dinheiro';
import {Garagem, Perfil} from './Noite';
import {Armas, Policia, Checklist} from './Crime';

// duração = tamanho exato do trecho na edição (scripts/edl_b1a4.json)
const M: [string, React.FC, number][] = [
  ['M1-barras', Barras, 6.6], ['M2-fuso', Fuso, 7.56], ['M3-split-antigo', SplitAntigo, 12.0], ['M4-split-novo', SplitNovo, 6.0],
  ['M5-app', App, 10.26], ['M6-gasolina-a', GasolinaA, 5.52], ['M7-gasolina-b', GasolinaB, 1.79], ['M8-gasolina-c', GasolinaC, 2.86],
  // falas 74-128 (scripts/edl_74-128.json)
  ['N1-bolso-banco', BolsoBanco, 6.465], ['N2-custo-morrer', CustoMorrer, 7.335], ['N3-venda-carro', VendaCarro, 13.242], ['N4-venda-carro2', VendaCarro2, 6.645],
  ['N5-regras', Regras, 10.97], ['N6-conta', Conta5, 11.36], ['N7-lojas', Lojas, 8.145], ['N8-garagem', Garagem, 5.08], ['N9-perfil', Perfil, 17.415],
  // falas 47-73 (scripts/edl_47-73.json)
  ['O1-armas', Armas, 11.16], ['O2-policia', Policia, 16.565], ['O3-checklist', Checklist, 12.065],
];
const ComFontes = (C: React.FC) => () => (<><Fontes /><C /></>);

export const Raiz: React.FC = () => (
  <>
    {M.map(([id, C, s]) => (
      <Composition key={id} id={id} component={ComFontes(C)} durationInFrames={Math.round(s * 30)} fps={30} width={1920} height={1080} />
    ))}
  </>
);
