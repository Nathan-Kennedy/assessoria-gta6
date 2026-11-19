"""Gera comps EffectCraft a partir de EDL, usando somente a stdlib.

Tempos do EDL (inclusive src) em segundos; stretch em porcentagem.
Uso: python -I scripts/gerar_projeto.py --edl scripts/edl_teste.json
     --saida edicao/novo.ecproj
Ou:  python -I scripts/gerar_projeto.py --teste
"""
import argparse
from copy import deepcopy
from decimal import Decimal
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TICKS = 254016000000


def nodes(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from nodes(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from nodes(value)


def ticks(seconds):
    return round(Decimal(str(seconds)) * TICKS)


def prop(obj, match):
    found = [n for n in nodes(obj) if n.get('match') == match]
    if len(found) != 1:
        raise ValueError(f'Propriedade {match}: esperado 1 resultado, obtidos {len(found)}')
    return found[0]


def transform(layer, match):
    group = next(n for n in layer['props']['children'] if n['match'] == 'transform')
    return prop(group, match)


def expression(p, text):
    p['expr'] = {'text': text, 'enabled': True}


def color(value):
    if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
        raise ValueError(f'Cor invalida: {value!r}; use #RRGGBB')
    return [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)] + [1.0]


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f'Numero invalido: {value!r}')
    return value


def validate(project):
    seen = set()
    for node in nodes(project):
        for key in ('id', 'uid'):
            value = node.get(key)
            if type(value) is int:
                if value in seen:
                    raise ValueError(f'Identificador duplicado: {value}')
                seen.add(value)
        if 'item' in node and str(node['item']) not in project['items']:
            raise ValueError(f'Item referenciado inexistente: {node["item"]}')
    for key, item in project['items'].items():
        if key != str(item['id']):
            raise ValueError(f'Chave de item inconsistente: {key}')
    if project['next_id'] <= max(seen, default=0):
        raise ValueError('next_id precisa superar todos os identificadores')


def generate(original, edl):
    p = deepcopy(original)
    used = {n[k] for n in nodes(p) for k in ('id', 'uid') if type(n.get(k)) is int}
    counter = p['next_id']

    def allocate():
        nonlocal counter
        while counter in used:
            counter += 1
        result = counter
        used.add(result)
        counter += 1
        return result

    # O arquivo-base usa uid=0 em global_light e IDs locais na render_queue.
    # Normalizar somente esses casos conhecidos, sem alterar refs de items/layers.
    for item in p['items'].values():
        for n in nodes(item['kind'].get('global_light', {})):
            if n.get('uid') == 0:
                n['uid'] = allocate()
    for entry in p.get('render_queue', []):
        entry['id'] = allocate()

    def clone(obj):
        result = deepcopy(obj)
        for n in nodes(result):
            for k in ('id', 'uid'):
                if type(n.get(k)) is int:
                    n[k] = allocate()
        result.pop('parent', None)
        result.pop('track_matte', None)
        return result

    duration = number(edl['comp']['duration'])
    if duration <= 0 or not isinstance(edl['comp']['name'], str) or not edl['comp']['name']:
        raise ValueError('Comp precisa de nome e duracao positiva')
    template = p['items']['7226']
    models = {l['name']: l for l in template['kind']['layers']}

    def layer(model, t0=0, t1=None, name=None):
        t1 = duration if t1 is None else t1
        if not 0 <= number(t0) < number(t1) <= duration:
            raise ValueError(f'Intervalo invalido: {t0}, {t1} (duracao {duration})')
        result = clone(models[model])
        result.update(name=name or model, start_time=0, in_point=ticks(t0), out_point=ticks(t1))
        return result

    clips = []
    for i, c in enumerate(edl.get('clips', []), 1):
        kind = c['tipo']
        model = {'footage': 'C04', 'still': 'C03', 'comp': 'C02'}[kind]
        item = p['items'][str(c['item'])]
        expected = 'Comp' if kind == 'comp' else 'Footage'
        if item['kind']['type'] != expected:
            raise ValueError(f'Tipo incompativel para item {c["item"]}')
        l = layer(model, c['t0'], c['t1'], f'C{i:03}')
        stretch = number(c.get('stretch', 100))
        src = number(c.get('src', 0))
        if stretch <= 0 or src < 0:
            raise ValueError('stretch deve ser positivo e src nao negativo')
        l.update(source={'type': expected, 'item': item['id']}, stretch=stretch,
                 start_time=ticks(Decimal(str(c['t0'])) - Decimal(str(src)) * Decimal(str(stretch)) / 100))
        l['switches']['audio'] = False
        blend = c.get('frameblend', False)
        if type(blend) is not bool:
            raise ValueError('frameblend deve ser booleano')
        l['switches']['frame_blend'] = 'FrameMix' if blend else 'Off'
        scale = transform(l, 'scale')
        scale.pop('expr', None)
        if c.get('escala') is not None:
            a, b = map(number, c['escala'])
            expression(scale, f's=linear(time,inPoint,outPoint,{a},{b});[s,s]')
        # ancora no centro real da fonte (o modelo vinha com a ancora de um video 1920x1080,
        # o que deslocava fontes 2560x1440 e fotos e deixava faixa preta na tela)
        kd = item['kind']
        if kind == 'comp':
            aw, ah = kd.get('width', 1920), kd.get('height', 1080)
        else:
            aw, ah = kd.get('width') or 1920, kd.get('height') or 1080
        ax, ay = c.get('anchor', [aw / 2, ah / 2])
        transform(l, 'anchor')['value']['v'][:2] = [number(ax), number(ay)]
        x, y = map(number, c.get('pos', [960, 540]))
        transform(l, 'position')['value']['v'][:2] = [x, y]
        transform(l, 'position').pop('expr', None)
        transform(l, 'anchor').pop('expr', None)
        clips.append(l)

    top = []
    for key, model, prefix in (('legendas', 'L04', 'L'), ('cards', 'K09', 'K')):
        for i, c in enumerate(edl.get(key, []), 1):
            l = layer(model, c['t0'], c['t1'], f'{prefix}{i:03}')
            text = prop(l['props'], 'sourceText')['value']['v']
            if not isinstance(c['texto'], str):
                raise ValueError('texto deve ser string')
            text['text'] = c['texto']
            transform(l, 'position')['value']['v'][1] = number(c.get('y', 1000 if key == 'cards' else 905))
            if key == 'cards':
                text.update(fill=color(c['cor']), size=number(c.get('tamanho', 160)))
            top.append(l)

    pins = []
    for i, c in enumerate(edl.get('pins', []), 1):
        w = 70 + 22 * len(c['texto'])
        bg, dot, txt = [layer(n + '1', c['t0'], c['t1'], f'{n}{i:03}')
                        for n in ('PINBG', 'PINDOT', 'PINTXT')]
        prop(bg['props'], 'size')['value']['v'][0] = w
        prop(prop(dot['props'], 'fill'), 'color')['value']['v'] = color(c['cor'])
        prop(txt['props'], 'sourceText')['value']['v']['text'] = c['texto']
        for l, ini, end, y in ((bg, -w / 2 - 20, 60 + w / 2, 95),
                               (dot, -w - 20, 95, 95), (txt, -w + 7, 122, 108)):
            position = transform(l, 'position')
            position['value']['v'][:2] = [end, y]
            expression(position, f'[easeOut(time,inPoint,inPoint+0.35,{ini},{end}), {y}]')
        pins.extend([txt, dot, bg])

    flash, whip = layer('FX_FLASH'), layer('FX_WHIP')
    for l, key in ((flash, 'flashes'), (whip, 'whips')):
        times = edl.get(key, [])
        for t in times:
            if not 0 <= number(t) <= duration:
                raise ValueError(f'Tempo de {key} fora da comp: {t}')
        exprs = [n['expr'] for n in nodes(l) if 'expr' in n and n['expr']['text'].startswith('c=[')]
        if len(exprs) != 1:
            raise ValueError(f'Expressao de {key} nao encontrada')
        exprs[0]['text'] = re.sub(r'^c=\[[^\]]*\]', 'c=' + json.dumps(times), exprs[0]['text'], count=1)

    shell = deepcopy(template)
    shell['kind']['layers'] = []
    comp = clone(shell)
    comp['name'] = edl['comp']['name']
    comp['kind'].update(duration=ticks(duration), work_area=[0, ticks(duration)],
                        display_start=0, poster_time=0)
    comp['kind']['layers'] = (top + pins + [layer(n) for n in ('Key', 'Rim', 'Amb')]
        + [flash, whip] + [layer('FX_MISTERIO', a, b, f'FX_MISTERIO{i:03}')
                          for i, (a, b) in enumerate(edl.get('misterio', []), 1)]
        + [layer('FX_ACABAMENTO')] + sorted(clips, key=lambda l: l['in_point'], reverse=True)
        + [layer('FUNDO')])
    p['items'][str(comp['id'])] = comp
    p['openComps'].append(comp['id'])
    p['activeComp'] = comp['id']
    p['next_id'] = counter
    validate(p)
    return p


def local_path(value):
    path = Path(value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f'Caminho fora da pasta do projeto: {path}')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', default=str(ROOT / 'edicao/video03_base.ecproj'))
    parser.add_argument('--edl')
    parser.add_argument('--saida')
    parser.add_argument('--teste', action='store_true')
    args = parser.parse_args()
    if args.teste:
        args.edl = args.edl or str(ROOT / 'scripts/edl_teste.json')
        args.saida = args.saida or str(ROOT / 'edicao/teste_gerador.ecproj')
    if not args.edl or not args.saida:
        parser.error('Informe --edl e --saida, ou --teste')
    try:
        source, edl_path, target = map(local_path, (args.entrada, args.edl, args.saida))
        if target in (source, edl_path, ROOT / 'edicao/video03_base.ecproj'):
            raise ValueError('A saida nao pode sobrescrever os arquivos de entrada ou o original')
        original = source.read_bytes()
        result = generate(json.loads(original), json.loads(edl_path.read_text(encoding='utf-8-sig')))
        serialized = json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2)
        validate(json.loads(serialized))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(serialized, encoding='utf-8')
        validate(json.loads(target.read_text(encoding='utf-8')))
        if source.read_bytes() != original:
            raise ValueError('Arquivo original foi alterado durante a execucao')
        comp = result['items'][str(result['activeComp'])]
        print(f'OK: {target} | {comp["name"]} | {len(comp["kind"]["layers"])} camadas; JSON, IDs e referencias validados.')
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f'Erro: {exc}\n')


if __name__ == '__main__':
    main()
