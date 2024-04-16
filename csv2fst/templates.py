from jinja2 import Environment, FileSystemLoader
import pandas as pd
from os.path import join as pjoin, expanduser
from math import isnan

""" This module should be made more general because we want to use it
to handle prenouns in addition to preverbs.  """

NO_CH_CONJUNCT="@D.ChCnj@"
CLEAR_CH_CONJUNCT="@C.ChCnj@"

def check_na(val):
    try:
        return isnan(val)
    except:
        return False

def get_plain_conjunct(plain_conjunct,changed_conjunct):
    return (plain_conjunct
            if check_na(changed_conjunct)
            else f"{NO_CH_CONJUNCT}{plain_conjunct}")

def get_allomorph(pv,order_filter):
    canonical = pv["PV"]
    if order_filter == "Any":
        allomorph = (None
                     if pv["Independent"] != pv["PlainConjunct"]
                     else pv["Independent"])
    elif order_filter == "Independent":
        allomorph = (None
                     if pv["Independent"] == pv["PlainConjunct"]
                     else pv["Independent"])
    elif order_filter == "PlainConjunct":
        allomorph = (None
                     if pv["Independent"] == pv["PlainConjunct"]
                     else get_plain_conjunct(pv["PlainConjunct"],
                                             pv["ChangedConjunct"]))
    elif order_filter == "ChangedConjunct":
        allomorph = (None
                     if check_na(pv[order_filter])
                     else pv[order_filter])
    else:
        raise ValueError(f"Unknown order filter {order_filter}")
    return None if allomorph == None else (canonical, allomorph)

def get_load_preverb_csv(source_dir):
    def load_preverb_csv(csv_fn,pv_tag,next_pv_lexicon,order_filter):
        entries = []
        df = pd.read_csv(pjoin(source_dir, csv_fn))
        for _, pv in df.iterrows():
            res = get_allomorph(pv, order_filter)
            if res != None:
                canonical, allomorph = res
                canonical = pv_tag + canonical
                # If the allomorph has a disallow changed conjunct
                # tag, add one to the canonical form as well
                if allomorph.find(NO_CH_CONJUNCT) != -1:
                    canonical = NO_CH_CONJUNCT + canonical
                entries.append(
                    f"{canonical}:{allomorph} {next_pv_lexicon} ;")
        if entries == []:
            entries = ["%<EMPTYLEX%> # ;"]
        return "\n".join(entries)
    return load_preverb_csv

def get_generate_preverb_sub_lexicons(source_dir):
    load_preverb_csv = get_load_preverb_csv(source_dir)
    def generate_preverb_sub_lexicons(csv_fn,pv_tag,pv_lexicon):
        lexicons = [(f"LEXICON {pv_lexicon}{order_filter}\n" +
                     load_preverb_csv(csv_fn,
                                      pv_tag,
                                      f"{pv_lexicon}Boundary",
                                      order_filter))
                     for order_filter in ["Any",
                                          "Independent",
                                          "PlainConjunct",
                                          "ChangedConjunct"]]
        lexicons.append(f"""LEXICON {pv_lexicon}Boundary 
{CLEAR_CH_CONJUNCT}+:{CLEAR_CH_CONJUNCT}- {pv_lexicon} ;""")
        return "\n\n".join(lexicons)
    return generate_preverb_sub_lexicons

def render_pv_lexicon(config,lexc_path):
    csv_src_path = config['pv_source_path']
    template_file = "preverbs.lexc.j2"
    template_dir = expanduser(config['template_path'])
    env = Environment(loader=FileSystemLoader(template_dir))
    print(dir(env))
    jinja_template = env.get_template(template_file)
    func_dict = {
        "load_preverb_csv":
        get_load_preverb_csv(csv_src_path),
        "generate_preverb_sub_lexicons":
        get_generate_preverb_sub_lexicons(csv_src_path)
    }
    jinja_template.globals.update(func_dict)
    template_string = jinja_template.render()
    with open(pjoin(lexc_path, "preverbs.lexc"),"w") as f:
        print(template_string, file=f)


if __name__ == "__main__":
    print(render("../PVSpreadsheets","preverbs.lexc.j2","."))
