# Tarefa: motions do vídeo 03 em Remotion (pasta `motion/`)

Projeto Remotion 4 já montado em `motion/`, com o `node_modules` como junção (NÃO rode `npm install`).
- Base visual pronta: `src/base.tsx` (Fundo, Camera, Revela, Conta, Fonte, Flash, useMola, useRampa, neon, caixaNeon, COR, f) e `src/Icones.tsx`.
- Os motions **aprovados** do vídeo 02 estão em `src/referencia_v02/*.tsx` (Barras, Fuso, Split, App, Gasolina, Dinheiro, Noite, Crime). **Copie o nível de acabamento deles:**
  - entrada com mola e contadores rolando;
  - linhas que se desenham (strokeDashoffset);
  - glow neon;
  - tremida de câmera e flash no impacto;
  - fundo vivo `<Fundo/>`;
  - tipografia Anton (títulos) e Mont (textos);
  - cores COR.rosa, COR.ciano, COR.laranja, COR.verm, COR.ouro.
- Resolução 1920x1080, 30 fps. A tela inteira é o motion: ele entra no vídeo como clipe de tela cheia.
- Ponto **crítico**: cada animação acontece no **tempo exato da palavra** da narração. Por isso todo componente recebe os tempos (em segundos, relativos ao início do clipe) por props, com valores padrão.

## Arquitetura
- `src/tempos.json`: lista de composições `{ "id": "C03-checklist", "comp": "Checklist", "dur": 9.0, "props": { ...beats e textos... } }`. Escreva ele com **valores padrão razoáveis**. Eu vou sobrescrever com os tempos reais depois, mantendo os mesmos nomes de props.
- `src/Raiz.tsx` lê `tempos.json` e registra uma `<Composition>` por item (`durationInFrames = round(dur*30)`, `defaultProps = props`). O componente fica envolvido com `<Fontes/>`, como em `referencia_v02/Raiz.tsx`. O `src/index.ts` já registra a `Raiz`.
- Cada componente lê só as props (nada de tempo fixo no código).

## Componentes (um arquivo por grupo, nomes livres)
1. **Relogio**: transição de bloco, ~2,6 s, reutilizada nos 14 blocos. É um relógio digital gigante neon que rola os dígitos do horário anterior (`de`) até o novo (`para`), com a data (`data`, ex. "18/11" ou "19/11"), um título curto embaixo (`titulo`, ex. "PROTEGE A SURPRESA") e um ponteiro de relógio analógico girando atrás. No fim, ele encolhe para o canto. Instâncias em tempos.json:
   - `R00`: de "--:--" para "08:00", 18/11, "A MADRUGADA DO GTA 6";
   - `R02`: 08:00 → 08:00, "PROTEGE A SURPRESA";
   - `R03`: → 12:00, "SE AS ANÁLISES SAÍREM";
   - `R04`: → 20:00, "A CHECAGEM";
   - `R05`: → 23:30, "TIRA O DEDO DO REINICIAR";
   - `R06`: → 00:00 19/11, "O CADEADO" (a data vira de 18 para 19 com flash);
   - `R07`: → 00:05, "DEIXA A INTRODUÇÃO ROLAR";
   - `R08`: → 00:40, "ESQUECE O MARCADOR";
   - `R09`: → 01:00, "ANTES DO PRIMEIRO CRIME";
   - `R10`: → 01:30, "A PRIMEIRA LOJA";
   - `R11`: → 02:00, "SE A FUGA COMEÇAR";
   - `R12`: → 03:00, "O ERRO CARO";
   - `R13`: → 04:00, "A CAMA";
   - `R14`: → 05:00, "LEONIDA FICA PRA AMANHÃ".
2. **Fuso** (C01, ~8 s; beats `nz`, `br`, `horas`): mapa-múndi estilizado com pontos acendendo. A Nova Zelândia está "JÁ JOGANDO 00:00 · 19/11" e o Brasil "08:00 · 18/11". Um arco se desenha entre os dois com o contador "16 HORAS". Pode desenhar os continentes com formas simples; não precisa ser geograficamente perfeito.
3. **Boato** (C02, ~7 s; beats `insider`, `boato`, `nota`): cartão "INSIDER: NateTheHate · análises no dia 18?", um carimbo vermelho BOATO bate com tremida, e um placar de nota com "?/10" piscando.
4. **Checklist** (C03, ~14 s; beats `espaco`, `atualizacao`, `regiao`, `cama`): quatro itens com ícone, cada um marcado ✓ com mola na sua batida:
   - ESPAÇO: até 212 GB (com uma barra de armazenamento);
   - ATUALIZAÇÃO;
   - REGIÃO DO CÓDIGO: conta BR = código BR;
   - CAMA (com um ícone de lua).
5. **Reiniciar** (C04, ~8 s; beats `botao`, `elevador`, `downloads`): um botão REINICIAR é apertado várias vezes (um contador "x20") e aparece o texto "NÃO É ELEVADOR". Depois, três aparelhos (CELULAR, PC, TV DA SALA) com o download entrando em PAUSA um por um.
6. **Cadeado** (C05, ~10 s; beats `virada`, `abre`, `erro`, `espera`): o calendário vira 18→19 e um cadeado neon abre com flash e partículas. Aparece um cartão "ERRO?" e um temporizador circular de 5:00 contando (acelerado).
7. **Keys** (C06, ~10 s; beats `keys`, `jason`, `lucia`): um mapa estilizado de Leonida (península + ilhas das Keys ao sul). A câmera dá zoom nas Keys, aparece o pin "JASON · LEONIDA KEYS" e a Lucia vem por uma linha tracejada a partir de "PENITENCIÁRIA DE LEONIDA". Cartão "FONTE: ROB NELSON À FAMITSU".
8. **Loja** (C07, ~12 s; beats `fundos`, `cameras`, `testemunha`, `ladra`): planta vista de cima de uma loja de conveniência. Uma seta entra pelos fundos, o ícone de câmera apaga (CÂMERAS OFF) e um cone de visão de testemunha aparece em vermelho. Depois entra um segundo boneco "OUTRA LADRA" e o texto "ATÉ PRA ROUBAR TEM FILA".
9. **Estrelas** (C08, ~12 s; beats `estrelas`, `seis`, `area`, `tiro`): seis estrelas acendem uma a uma, e a sexta com impacto e "6 ESTRELAS". Depois um minimapa redondo onde os pontinhos da polícia somem e aparece um círculo pulsante "ÁREA DE BUSCA", com o carrinho do jogador saindo pela borda. Por fim "TIRO PRA ASSUSTAR · FAMITSU".
10. **Caixa** (C09, ~10 s; beats `preso`, `bolso`, `caixa`, `banco`): uma rota com dois pins de loja e um pin de CAIXA ELETRÔNICO no meio. Os contadores BOLSO e BANCO aparecem. No `preso` aparece o carimbo BUSTED e o BOLSO zera com notas voando, enquanto o BANCO fica (use valores ilustrativos e escreva "valores ilustrativos").
11. **Cama** (C10, ~7 s; beats `cama`, `dormir`): o checklist das 20:00 volta com só o item CAMA destacado, e o relógio marca 04:00 com Z-Z-Z subindo. Texto "DORME QUE O JOGO NÃO FOGE".
12. **Mapa** (C11, ~8 s; beats `afasta`, `amanha`): um mapa estilizado se afasta, uma rota curta da madrugada aparece pequenininha num canto e muitos caminhos escuros ficam por explorar. Um pin "AMANHÃ" pulsa.
13. **Fecho** (C12, ~9 s; beats `comenta`, `inscreve`, `video`): um balão de comentário "QUAL A 1ª COISA QUE VOCÊ VAI FAZER?", um botão INSCREVER-SE pulsando que vira "INSCRITO ✓" com clique, e um card do vídeo de ontem com a imagem `public/thumb_v02.jpg` e o título "O PRIMEIRO DIA PERFEITO".

## Entrega
- Escreva os componentes, o `tempos.json` e a `Raiz.tsx`.
- Rode `npx remotion bundle src/index.ts --out-dir=build --log=error` e corrija erros de TypeScript ou bundle até passar.
- Depois renderize um quadro de prévia de cada composição, no meio do clipe: `npx remotion still build <id> out/previa/<id>.png --frame=<meio>`. Olhe os PNG para conferir se não tem texto encavalado ou cortado e corrija.
- NÃO renderize os vídeos inteiros.
- No fim, imprima a lista de ids e um resumo curto.
