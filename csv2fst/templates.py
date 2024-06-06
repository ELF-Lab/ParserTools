from jinja2 import Environment, FileSystemLoader
import pandas as pd
from os import listdir
from os.path import join as pjoin, expanduser, basename, dirname
from math import isnan
from paradigm_slot import escape

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

def get_load_pre_element_csv(source_dir):
#    def load_pre_element_csv(csv_fn,pv_tag,next_pv_lexicon,order_filter):
    def load_pre_element_csv(sources,next_pv_lexicon,order_filter):
        entries = []
        for csv_fn, pv_tag in sources:
            df = pd.read_csv(pjoin(source_dir, csv_fn))
            for _, pv in df.iterrows():
                res = get_allomorph(pv, order_filter)
                if res != None and not "NONE" in res:
                    canonical, allomorph = res
                    canonical = pv_tag + canonical
                    # If the allomorph has a disallow changed conjunct
                    # tag, add one to the canonical form as well
                    if allomorph.find(NO_CH_CONJUNCT) != -1:
                        canonical = NO_CH_CONJUNCT + canonical
                    entries.append(
                        f"{escape(canonical)}+:{escape(allomorph)} {next_pv_lexicon} ;")
        if entries == []:
            entries = ["%<EMPTYLEX%> # ;"]
        return "\n".join(entries)
    return load_pre_element_csv

def get_generate_pre_element_sub_lexicons(source_dir):
    load_pre_element_csv = get_load_pre_element_csv(source_dir)
#    def generate_pre_element_sub_lexicons(csv_fn,pv_tag,pv_lexicon):
    def generate_pre_element_sub_lexicons(sources,pv_lexicon):
        lexicons = [(f"LEXICON {pv_lexicon}{order_filter}\n" +
#                     load_pre_element_csv(csv_fn,
#                                          pv_tag,
#                                          f"{pv_lexicon}Boundary",
#                                          order_filter))
                     load_pre_element_csv(sources,
                                          f"{pv_lexicon}Boundary",
                                          order_filter))                     
                     for order_filter in ["Any",
                                          "Independent",
                                          "PlainConjunct",
                                          "ChangedConjunct"]]
        lexicons.append(f"""LEXICON {pv_lexicon}Boundary 
{CLEAR_CH_CONJUNCT}:{CLEAR_CH_CONJUNCT}- {pv_lexicon} ;""")
        return "\n\n".join(lexicons)
    return generate_pre_element_sub_lexicons

def pretty_join(str_list):
    lines = [""]
    for s in str_list:
        if lines[-1] == "":
            lines[-1] += s
        elif len(lines[-1]) + len(s) + 1 <= 79:
            lines[-1] += f" {s}"
        else:
            lines.append(s)
    return "\n".join(lines)

def get_all_pre_element_tags(source_dir):
    def all_pre_element_tags(tag_transformation='lambda x:x'):
        pre_element_tags = set()
        tag_transformation = eval(tag_transformation)
        for fn in listdir(path=source_dir):
            if fn.endswith(".csv"):
                df = pd.read_csv(pjoin(source_dir,fn))
                df.Tag = df.Tag.transform(tag_transformation)
                pre_element_tags.update(zip(df["Tag"],df["PV"]))
        pre_element_tags = sorted(list(pre_element_tags))
        return pretty_join([f"{tag}/{pv}+" for tag, pv in pre_element_tags])
    
    return all_pre_element_tags

def get_add_lexeme_multichar_symbols(config):
    def add_lexeme_multichar_symbols():
        return pretty_join([escape(symbol) for symbol in config["multichar_symbols"]])
    return add_lexeme_multichar_symbols

def render_pre_element_lexicon(config,source_path,lexc_path):
    csv_src_path = pjoin(source_path,config['pv_source_path'])
    template_file = basename(config['template_path'])
    template_dir = pjoin(expanduser(source_path),
                         dirname(config['template_path']))
    env = Environment(loader=FileSystemLoader(template_dir))
    jinja_template = env.get_template(template_file)
    func_dict = {
        "all_pre_element_tags":
        get_all_pre_element_tags(csv_src_path),
        "load_pre_element_csv":
        get_load_pre_element_csv(csv_src_path),
        "generate_pre_element_sub_lexicons":
        get_generate_pre_element_sub_lexicons(csv_src_path),
        "add_lexeme_multichar_symbols":
        get_add_lexeme_multichar_symbols(config)
    }
    jinja_template.globals.update(func_dict)
    template_string = jinja_template.render()
    with open(pjoin(lexc_path, template_file.replace(".j2","")),"w") as f:
        print(template_string, file=f)


