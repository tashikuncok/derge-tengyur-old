from pathlib import Path
import re

content = Path('processed/tanjurd.txt').read_text().strip().split('\n')
eq = {}
for line in content:
    ref, toh = line.split('\t')[:2]
    ref = 'K' + ref.rjust(4, '0')
    toh = toh.replace('D', 'T')
    eq[toh] = ref

missing = []
old = Path('../../derge-tengyur-tags').glob('*.txt')
for f in old:
    content = f.read_text()
    chunks = re.split(r'({.*?})', content)
    i = 0
    while i < len(chunks):
        if '{T' in chunks[i] or re.findall(r'{.*[0-9]', chunks[i]):
            toh = chunks[i][1:-1]
            if toh in eq.keys():
                new_ref = eq[toh]
                chunks[i] = '{' + new_ref + '}'
            else:
                missing.append((f.stem, chunks[i] + chunks[i+1][:150].replace('\n', ' ')))

        i += 1
    out_file = Path('../../derge-tengyur-tags-rkts') / f.name
    out_file.write_text(''.join(chunks))

Path('missing_rkts.txt').write_text('\n'.join(['{}\n\t{}'.format(a, b) for a, b in missing]))
print('ok')
