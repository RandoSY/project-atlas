"""Analyze exported Atlas Echo CSV. Python 3 standard library only."""
import csv, statistics, sys
from collections import defaultdict
groups=defaultdict(list)
for filename in sys.argv[1:]:
    with open(filename,newline='') as f:
        for r in csv.DictReader(f):
            if not r.get('echo_us') or float(r['echo_us'])<=0: continue
            key=(r['mode'],float(r['reference_mm']),float(r['temp_c']),float(r['quant_us']))
            groups[key].append(float(r['error_mm']))
for key, errors in sorted(groups.items()):
    sd=statistics.stdev(errors) if len(errors)>1 else float('nan')
    print(f'{key}: n={len(errors)} bias={statistics.mean(errors):.3f} mm SD={sd:.3f} mm')
