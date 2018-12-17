from pathlib import Path

kunme = []
kunme_lines = Path('kunsel-melong.csv').read_text().strip().split('\n')[1:]
for line in kunme_lines:
    parts = line.split('\t')
    rkts = parts[1].strip()
    new = []
    if ' ' in rkts:
        new = rkts.split(' ')
    else:
        new.append(rkts)

    kunme.extend(new)

files = []
for f in Path('canon_notes_input').glob('*.txt'):
    name = f.stem
    if name in files:
        print(name)
    else:
        files.append(name)

kunme_only = [k for k in kunme if k not in files]
files_only = [f for f in files if f not in kunme]

print('kunme only')
print('\n'.join(kunme_only))
print('files only')
print('\n'.join(files_only))
print('ok')