#!/usr/bin/python3

import re
import sys

pointers = [
    'prethink', 'think', 'blocked', 'touch', 'use', 'pain', 'die',
    'moveinfo_endfunc', 'monsterinfo_currentmove', 'monsterinfo_stand',
    'monsterinfo_idle', 'monsterinfo_search', 'monsterinfo_walk',
    'monsterinfo_run', 'monsterinfo_dodge', 'monsterinfo_attack',
    'monsterinfo_melee', 'monsterinfo_sight', 'monsterinfo_checkattack'
]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: genptr.py <file> [...]')
        sys.exit(1)

    exprs = '|'.join(
        p.replace('_', '\\.') for p in pointers if p != 'moveinfo_endfunc'
    )
    regex = re.compile(r'->\s*(%s)\s*=\s*&?\s*(\w+)' % exprs, re.ASCII)
    regex2 = re.compile(r'\b(?:Angle)?Move_Calc\s*\(.+,\s*(\w+)\s*\)', re.ASCII)

    types = {p: [] for p in pointers}
    for a in sys.argv[1:]:
        with open(a) as f:
            for line in f:
                if not line.lstrip().startswith('//'):
                    if match := regex.search(line):
                        t = types[match[1].replace('.', '_')]
                        p = match[2]
                        if p not in t and p != 'NULL':
                            t.append(p)
                        continue

                    if match := regex2.search(line):
                        t = types['moveinfo_endfunc']
                        p = match[1]
                        if p not in t:
                            t.append(p)


    print('// generated by genptr.py, do not modify')
    print('#include "g_ptrs.h"')

    decls = []
    for k, v in types.items():
        for p in v:
            if k == 'monsterinfo_currentmove':
                decls.append(f'extern int {p};')
            else:
                decls.append(f'extern void {p}(void);')
    for d in sorted(decls, key=str.lower):
        print(d)

    print('const save_ptr_t save_ptrs[] = {')
    for k, v in types.items():
        for p in sorted(v, key=str.lower):
            amp = '&' if k == 'monsterinfo_currentmove' else ''
            print('{ %s, %s%s },' % (f'P_{k}', amp, p))
    print('};')
    print('const int num_save_ptrs = sizeof(save_ptrs) / sizeof(save_ptrs[0]);')
