from extract_pages import *


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
                l = '[' + section + ' ' + ref + '། ' + l[1:]
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


if __name__ == '__main__':
    works = extract_lines()
    works = works_in_pages(works)
    works = works_stripped(works)
    works = strip_markup(works)
    works = strip_notemark(works)
    write_works(works)