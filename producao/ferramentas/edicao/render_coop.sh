#!/bin/bash
# Render cooperativo PC + notebook. Partes de 125 s. O PC vai de 1 para a frente, o notebook de N para trás.
# Trava = entrega/v03_parteN.lock (quem pegou). Resultado = entrega/v03_parteN.mp4 (de quem renderizou).
set -e
cd "C:/Projetos Dev/Videos/2026-11-18_video03-madrugada-gta6"
if powershell -NoProfile -c "Get-CimInstance Win32_Process -Filter \"Name='effectcraft-cli.exe'\" | ? { \$_.CommandLine -match 'video03' -and \$_.CommandLine -match ' render ' } | select -First 1" | grep -q .; then
  echo "JA TEM RENDER DO VIDEO 03 RODANDO: saindo"; exit 1
fi
ENT="C:/Projetos Dev/Videos/_pacote_notebook/entrega"; mkdir -p "$ENT"
CLI="/c/deps/effectcraft/0.16.0/effectcraft-0.16.0-windows-x64-portable/effectcraft-cli.exe"
DUR=$(python -c "import json;print(json.load(open('scripts/tempos.json'))['dur'])"); NP=$(python -c "import math;print(math.ceil($DUR/125-0.01))")
ok(){ [ -f "$1" ] && ffprobe -v error "$1" >/dev/null 2>&1; }
for n in $(seq 1 $NP); do
  out="render/v03_parte$n.mp4"
  if ok "$ENT/v03_parte$n.mp4"; then cp "$ENT/v03_parte$n.mp4" "$out"; echo "parte$n veio da entrega"; continue; fi
  if [ -f "$ENT/v03_parte$n.lock" ] && ! grep -q PC "$ENT/v03_parte$n.lock"; then
    echo "parte$n está com o notebook: esperando"; until ok "$ENT/v03_parte$n.mp4"; do sleep 20; done; cp "$ENT/v03_parte$n.mp4" "$out"; continue
  fi
  echo PC > "$ENT/v03_parte$n.lock"
  ini=$(( (n-1)*125 )); fim=$(( n*125 )); END=""; [ $n -lt $NP ] && END="--end $fim"
  for t in 1 2 3; do
    "$CLI" render --project edicao/video03.ecproj --comp VIDEO03 --start $ini $END --out "$out" --format h264 --bitrate 16000 --audio off --progress 2> "render/v03_parte${n}_progress.txt" && break
    rm -f "$out"
  done
  cp "$out" "$ENT/v03_parte$n.tmp" && mv "$ENT/v03_parte$n.tmp" "$ENT/v03_parte$n.mp4"; echo "OK parte$n (PC) $(date +%H:%M)"
done
: > render/v03_lista.txt; for n in $(seq 1 $NP); do echo "file 'v03_parte$n.mp4'" >> render/v03_lista.txt; done
ffmpeg -y -v error -f concat -safe 0 -i render/v03_lista.txt -c copy render/v03_video.mp4
ffmpeg -y -v error -i render/v03_video.mp4 -i render/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart render/GTA6_video03_FINAL.mp4
echo "PRONTO $(ffprobe -v error -show_entries format=duration -of csv=p=0 render/GTA6_video03_FINAL.mp4)"
