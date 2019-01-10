from pathlib import Path
import re


def extract_lines():
    """
    parses the files line per line and returns the following structure

    return:
        {toh1: [(vol_id, line1), (vol_id, line2), ...], toh2: ...}
    """
    in_path = Path('../../derge-tengyur-tags')
    files = sorted(list(in_path.glob('*.txt')))
    missing_inc = 1

    works = []
    prev_toh = ''
    current_work = []
    for file in files:
        prefix = file.stem
        lines = [line.strip().strip('\ufeff') for line in file.open().readlines()]
        for line in lines:
            toh = re.findall(r'\{(D[0-9]+a?)\}', line)
            if toh:
                toh = toh[0]
                if prev_toh != '':
                    current_work.append((prefix, line))

                    if prev_toh == 'X0000':
                        prev_toh += str(missing_inc)
                        missing_inc += 1

                    works.append((prev_toh, current_work))

                # initialize new work
                current_work = [(prefix, line)]
                prev_toh = toh
            else:
                current_work.append((prefix, line))
    return works


def works_in_pages(works_in_lines):
    """
    nput:
        {toh1: [(vol_id, line1), (vol_id, line2), ...], toh2: ...}

    action:
        removes vol_id except for the first line of the work and for any volume change
    """
    works = []
    for work, lines in works_in_lines:
        vol_id = ''
        current_work = []
        for line in lines:
            vol, l = line
            if vol_id != vol:
                current_work.append(line)
                vol_id = vol
            else:
                current_work.append(l)
        works.append((work, current_work))
    return works


def works_stripped(works_in_lines):
    works = []
    for work, lines in works_in_lines:
        current_work = []
        is_beginning = True
        for line in lines:
            # clean beginning line
            if is_beginning:
                if isinstance(line, tuple):
                    is_beginning = False
                    vol, l = line

                    # clean line
                    l = l
                    end_pagemark = l.find(']')
                    start_toh = l.find('{')
                    if end_pagemark + 1 < start_toh:
                        l = l[:end_pagemark+1] + l[start_toh:]
                    line = (vol, l)

            # clean ending line
            if line == lines[-1]:
                if isinstance(line, tuple):
                    line = line[1]
                new_toh_start = line.find('{')
                line = line[:new_toh_start]  # cut off new work
                end_pagemark = line.find(']')
                if end_pagemark == len(line) - 1:
                    continue

            # escapes preceding lines
            if not is_beginning:
                current_work.append(line)

        empty_line = True
        while empty_line:
            to_check = current_work[-1]
            if isinstance(to_check, tuple):
                to_check = to_check[1]
            if to_check.find(']') == len(to_check) - 1:
                del current_work[-1]
            else:
                empty_line = False

        works.append((work, current_work))
    return works


def flatten_for_output(works):
    for name, work in works:
        i = 0
        while i < len(work):
            if isinstance(work[i], tuple):
                work[i] = '[{}]{}'.format(work[i][0], work[i][1])
            i += 1


def write_works(works):
    out_path = Path('export')
    if not out_path.is_dir():
        out_path.mkdir(exist_ok=True)

    for f in out_path.glob('*.*'):
        f.unlink()

    for work, lines in works:
        out_file = out_path / str(work + '.txt')
        out_file.write_text('\n'.join(lines))


def strip_markup(works_stripped):
    works = []
    for work, lines in works_stripped:
        # 1. strip toh
        start, end = lines[0][1].find('{'), lines[0][1].find('}')
        lines[0] = (lines[0][0], lines[0][1][:start] + lines[0][1][end+1:])

        current_work = []
        for num, line in enumerate(lines):
            vol, l = None, None
            if isinstance(line, tuple):
                vol, l = line
            else:
                l = line

            if not l:  # hack to avoid tripping over empty files
                continue

        # 2. strip pagemarks except for page changes and the beginning of works
            end = l.find(']')
            if l[end-1] != '1' and num:
                l = l[end+1:]

            l = re.sub('\.[0-7]', '', l)

            # pass inter-page lines
            if not l:
                continue

        # 3. strip volume reference
            if vol:
                _, section, ref = vol.replace(' ', '_').split('_')
                l = '[' + section + '_' + ref + '།_' + l[1:]
                current_work.append(l)
            elif l:
                current_work.append(l)

        works.append((work, current_work))
    return works


def strip_notemark(works):
    out = []
    for work, lines in works:
        lines = [line.replace('#', '') for line in lines]
        out.append((work, lines))
    return out


def strip_in_spaces(works):
    out = []
    for name, work in works:
        content = ''.join(work)
        chunks = [c.replace('_', ' ') for c in content.split(' ')]
        out.append((name, chunks))
    return out


if __name__ == '__main__':
    works = extract_lines()
    works = works_in_pages(works)
    works = works_stripped(works)
    works = strip_markup(works)
    works = strip_notemark(works)
    works = strip_in_spaces(works)
    write_works(works)
