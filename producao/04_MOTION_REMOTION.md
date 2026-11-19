# 4. Motion graphics no Remotion

Tudo que **explica** algo vira motion: comparação de números, mapa, linha do tempo, checklist, dinheiro, HUD de polícia, notícia. Arte parada (PNG) foi reprovada. O motion tem entrada com mola, contador rolando, linha se desenhando, tremida no impacto e fundo vivo.

Modelo pronto: `modelos/motion-remotion/` (projeto do vídeo 02, estilo "Vice Neon Doc").

## Começar

```
cp -r producao/modelos/motion-remotion  <pasta_do_video>/motion
cd <pasta_do_video>/motion
npm install
# coloque em public/ dois frames de fundo: bg_neon.png e bg_noite.png
# (um frame do trailer em 1920x1080; o componente Fundo desfoca e escurece)
npx remotion studio            # pré-visualizar
npx remotion render M1-barras out/M1-barras.mov --codec=prores --prores-profile=4444   # com transparência
npx remotion render M1-barras out/M1-barras.mp4 --crf=16                               # sem transparência
```

## O que tem no modelo

- `src/base.tsx`: a base visual, que **deve ser reaproveitada**:
  - `COR`: paleta do canal (rosa `#FF3D8B`, ciano `#19E3D3`, laranja, roxo escuro, ouro);
  - fontes Anton (títulos) e Montserrat (texto), em `public/fonts/` (licença OFL);
  - `f(s)`: segundos → frames (30 fps);
  - `useMola(s)`: mola que começa no segundo `s`;
  - `useRampa(a, b)`: transição suave;
  - `useTremor([s...])`: tremida de câmera no impacto;
  - `Fundo`: frame do trailer desfocado + grade synthwave + partículas + grão.
- `Barras.tsx` (GTA 5 × GTA 6 em GB), `Fuso.tsx` (mapa-múndi com fuso), `Split.tsx` (antes × depois, fluxograma), `Dinheiro.tsx` (contadores, bolso × banco, venda de carro), `Crime.tsx` (estrelas, área de busca, checklist), `Gasolina.tsx`, `Noite.tsx`, `App.tsx` (mockup de celular), `Icones.tsx`.
- `src/Raiz.tsx`: registra as composições. A **duração de cada uma é o tamanho exato do trecho na edição**.

## Sincronizar com a fala (o mais importante)

Cada beat da animação cai **na palavra** da narração, nunca dividindo o trecho em partes iguais.

1. A voz já tem `palavras.json` (etapa 2).
2. O `build_edl.py` (etapa 5) acha a fala de cada `ANIMAÇÃO:` e escreve `motion/src/tempos.json` com a duração do trecho e o tempo de cada beat, relativo ao início do motion. Exemplo: `{"C01": {"dur": 8.1, "nz": 0.4, "br": 2.9, "horas": 5.2}}`.
3. O componente lê esses tempos: `useMola(T.C01.horas)`.
4. Se a narração mudar, rode o `build_edl.py` de novo e re-renderize só os motions que mudaram.

## Regras de qualidade

- 1920×1080, 30 fps. Texto grande (Anton ≥ 90 px no título), no máximo 6 palavras por cartão.
- A fonte do dado aparece pequena embaixo ("Fonte: IGN, entrevista com Rob Nelson"). Boato leva o selo "BOATO".
- Variar o formato: barras num bloco, mapa no outro, contador no outro. Repetir o mesmo cartão o vídeo inteiro cansa.
- Antes de importar, confira 3 quadros de cada motion (`npx remotion still <id> out/x.png --frame=N`).
- Para pedir motions ao Codex, use `modelos/roteiro/BRIEF_MOTION.md` como exemplo de brief. O bundle e o render ficam com o agente principal, porque o sandbox do Codex não abre o Chrome.
