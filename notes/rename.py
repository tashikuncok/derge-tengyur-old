from pathlib import Path
from fuzzywuzzy import fuzz
from collections import defaultdict


if __name__ == '__main__':
    pairs = Path('pairs.txt').read_text(encoding='utf-8-sig').strip().split('\n')
    cleaned = {}
    for p in pairs:
        clean = p
        clean = clean[clean.find('_')+1:]
        clean = clean.replace('_', '').replace('།', '').strip()
        cleaned[clean] = p

    rkts = {}
    for f in Path('rKTs/').glob('*.txt'):
        lines = f.read_text(encoding='utf-8-sig').strip().split('\n')
        for line in lines:
            ref, title = line.split('\t')
            rkts[ref] = title

    matches = defaultdict(dict)
    maybe = defaultdict(dict)
    for ref, title in rkts.items():
        for clean, raw in cleaned.items():
            ratio = fuzz.ratio(title, clean)
            if ratio > 90:
                matches[raw].update({ratio: [title, ref]})
            elif 90 > ratio > 80:
                maybe[raw].update({ratio: [title, ref]})

    out = ''
    for raw, potentials in matches.items():
        out += raw + '\n'
        for ratio, data in potentials.items():
            title, ref = data
            out += '\t\t' + str(ratio) + '%\t\t' + title + '\t\t' + ref + '\n'
    Path('matches.txt').write_text(out)

    out = ''
    for raw, potentials in maybe.items():
        out += raw + '\n'
        for ratio, data in potentials.items():
            title, ref = data
            out += '\t\t' + str(ratio) + '%\t\t' + title + '\t\t' + ref + '\n'
    Path('maybe.txt').write_text(out)
