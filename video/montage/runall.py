import json, sys
from multiprocessing import Pool
import analyse
if __name__ == '__main__':
    ids = json.load(open('used.json'))
    with Pool(8) as p:
        for r in p.imap_unordered(analyse.run, ids): print(r, flush=True)
