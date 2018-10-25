from pathlib import Path
import shutil


def parse_mistakes():
    parsed = []
    content = Path('with_mistakes.txt').read_text(encoding='utf-8-sig').strip().split('\n')
    for line in content:
        stem = line.replace('.txt', '').replace('.csv', '')
        parsed.append(stem)
    return sorted(list(set(parsed)))


def parse_input_dir():
    total = Path('canon_notes_input').glob('*.txt')
    pairs = {}
    for txt in total:
        if txt.stem not in pairs.keys():
            csv = txt.parent / Path(txt.stem + '.csv')
            # checking that both exist
            if txt.is_file() and csv.is_file():
                pairs[txt.stem] = (txt, csv)
    return pairs


def copy_good_pairs():
    out_dir = Path('cleaned_pairs')
    out_dir.mkdir(exist_ok=True)

    to_avoid = parse_mistakes()
    input_pairs = parse_input_dir()
    for name, pair in input_pairs.items():
        if name not in to_avoid:
            txt, csv = pair
            out_txt = out_dir / txt.name
            out_csv = out_dir / csv.name
            shutil.copy(str(txt), str(out_txt))
            shutil.copy(str(csv), str(out_csv))


if __name__ == '__main__':
    copy_good_pairs()
