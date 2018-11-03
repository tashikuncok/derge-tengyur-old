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
    # files = [in_path / '001_བསྟོད་ཚོགས།_ཀ.txt']
    missing_inc = 1

    works = []
    prev_toh = ''
    current_work = []
    for file in files:
        prefix = file.stem
        lines = [line.strip().strip('\ufeff') for line in file.open().readlines()]
        for line in lines:
            toh = re.findall(r'\{(T[0-9]+)\}', line)
            if toh:
                toh = toh[0]
                if prev_toh != '':
                    current_work.append((prefix, line))

                    if prev_toh == 'T00':
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
        works.append((work, current_work))
    return works


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
                _, _, ref = vol.replace(' ', '_').split('_')
                l = '[' + ref + '།' + l[1:]
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


def write_works(works):
    out_path =Path('works')
    if not out_path.is_dir():
        out_path.mkdir(exist_ok=True)

    for work, lines in works:
        out_file = out_path / str(work + '.txt')
        out_file.write_text('\n'.join(lines))


if __name__ == '__main__':
    works = extract_lines()
    works = works_in_pages(works)
    works = works_stripped(works)
    works = strip_markup(works)
    works = strip_notemark(works)
    write_works(works)
