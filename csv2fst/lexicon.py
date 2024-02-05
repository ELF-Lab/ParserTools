from paradigm_slot import ParadigmSlot, entry2str
import json
import pandas as pd
from sys import stderr
import os

class Lexicon:
    def __init__(self, conf:dict, regular:bool):
        self.conf = conf
        self.regular = regular
        self.lexicons = {"Root":set()}
        for fn in conf["csv_files" if regular else "irregular_csv_files"]:
            path = os.path.join(conf["path"],f"{fn}.csv")
            print(f"Reading lexicon entries from {path}", file=stderr)
            table = pd.read_csv(path, keep_default_na=False)
            for _, row in table.iterrows():
                paradigm_slot = ParadigmSlot(row, conf, regular)
                paradigm_slot.extend_lexicons(self.lexicons)
            
    def print_lexc(self):
        lexc_file = open(self.conf["lexc_file" if self.regular else "irregular_lexc_file"],"w")
        print("Multichar_Symbols",file=lexc_file)
        multichar_symbols = sorted(list(ParadigmSlot.multichar_symbols))
        print(" ".join(multichar_symbols), file=lexc_file)
        print("", file=lexc_file)
        print(f"Writing {len(self.lexicons)} sublexicons:", file=stderr)
        for lexicon in self.lexicons:            
            lexc_rows = sorted(list(self.lexicons[lexicon]))
            print(f"  {lexicon} ({len(lexc_rows)} entries)", file=stderr)
            print(f"LEXICON {lexicon}", file=lexc_file)
            for row in lexc_rows:
                print(entry2str(row), file=lexc_file)
            print("", file=lexc_file)

if __name__=="__main__":
    conf = json.load(open("conf.json"))
    lexicon = Lexicon(conf)
    lexicon.print_lexc()
