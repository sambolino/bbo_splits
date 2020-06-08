import os
import re
import glob
from itertools import groupby
from bs4 import BeautifulSoup

def count_freq(list_of_single_appearances): 
 
    #aggregate list elements with same values into a dict
    freq = {} 
    for item in list_of_single_appearances: 
        if (item in freq): 
            freq[item] += 1
        else: 
            freq[item] = 1
 
    #print (freq)
    breaks_as_keys = [
            [(0,0)],
            [(1,0)],
            [(1,1),(2,0)],
            [(2,1),(3,0)],
            [(2,2),(3,1),(4,0)],
            [(3,2),(4,1),(5,0)],
            [(4,2),(3,3),(5,1),(6,0)]
            ]

    #fill in zeros for breaks that didn't happen so we don't run into trouble
    for i in breaks_as_keys:
        for j in i:
            if j not in freq.keys():
                freq[j]=0

    #split dicts so that same number of missing cards belong to same dicts
    return map(lambda keys: {x: freq[x] for x in keys}, breaks_as_keys)

def main():
    path = 'data'
    links = []

    for filename in glob.glob(os.path.join(path, '*.html')):
        with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
            soup = BeautifulSoup(f.read(), 'lxml')
            links.extend(soup.find_all(name='a', onclick=True))
            f.close()

    print("%d total hands" %len(links))

    #ensure uniqueness
    deals = set()
    for l in links:
        onclick_content = l['onclick']
        index1 = onclick_content.find("%7Cmd%7C")
        index2 = onclick_content.find("%7CBoard")
        deals.add(onclick_content[index1:index2])    

    print("%d unique hands" %len(deals))

    breaks = []
    for d in deals:
        try:
            #regexp for finding values between S and H characters
            #most LIN's have s,w,n sets of cards, sometimes s,w,n,e
            spades = re.findall("(?<=S).*?(?=H)", d)
            if len(spades)==3: 
                s,w,n = spades
            elif len(spades)==4: 
                s,w,n,e=spades 
            else: raise ValueError
            slen = len(s)
            wlen = len(w)
            nlen = len(n)
            elen = 13-(slen+wlen+nlen)
            if elen == -30: print(spades)
            #append tuples (of breaks) to a list
            if slen+nlen<7:
                if slen>nlen:
                    breaks.append((slen, nlen))
                else: breaks.append((nlen, slen))
            else:
                if wlen>elen:
                    breaks.append((wlen, elen))
                else: breaks.append((elen, wlen))
        except ValueError:
            #if a corrupted value occurs
            continue

    print("%d valid hands" %len(breaks))
    all_breaks = list(count_freq(breaks))

    #double check hand count
    double_chk = 0
    for d in all_breaks:
        double_chk += sum(d.values())

    if double_chk != len(breaks):
        print("warning: if you are seeing this there is a bug and few deals are missing but it won't affect odds")

    #print header
    print("\n")
    print("%-*s %-*s %-*s %-*s" % (8, "break", 8, "sum", 8, "rel %", 6, "abs %" )) 
    print("---------------------------------")

    #triple check for the total and print data 
    triple_chk = 0
    for d in all_breaks:
        for k, v in d.items():
            d_sum = sum(d.values())
            if d_sum > 0:
                triple_chk += v
                print ("%s : %-*s %-*.2f %.2f" % (k, 8, v, 8,
                    v*100/sum(d.values()), v*100/double_chk))
            else:
                print (k)
        print("---------------------------------")
    print("total  : %s" % triple_chk)

if __name__ == '__main__':
    main()
