"""Code for dealing with conversion of Jinja2 templates to lexc
   code."""

from jinja2 import Environment, FileSystemLoader
import pandas as pd
from os import listdir
from os.path import join as pjoin, expanduser, basename, dirname
from math import isnan
from .lexc_path import escape, LexcPath
from re import sub

NO_CH_CONJUNCT="@D.ChCnj@"
"""Flag diacritic which disallows any value for the changed-conjunct
   feature `ChCnj`

""" 

CLEAR_CH_CONJUNCT="@C.ChCnj@"
"""Flag diacritic which clears the value of the changed-conjunct
   feature `ChCnj`

"""

def check_na(val):
    """Safely check if a value represents NaN. Will return True if the
       value is numeric and NaN. False, otherwise.

    """    
    try:
        return isnan(val)
    except:
        return False

def get_plain_conjunct(plain_conjunct,changed_conjunct):
    """Get a lexicon entry for the plain conjunct form of a preverb. Only
       add a disallow changed-conjunct flag diacritic if we have to,
       i.e. if a separate changed-conjunct form is specified (meaning
       `changed_conjunct != None`). This keeps the lexc file from
       getting cluttered with loads of unnecessary disallow flags.

    """    
    return (plain_conjunct
            if check_na(changed_conjunct)
            else f"{NO_CH_CONJUNCT}{plain_conjunct}")

def get_allomorph(pv,order_filter):
    """Return either the plain conjunct, changed conjunct or indpendent
       form of a preverb row (= spreadsheet row) depending on
       `order_filter`. This will do into different lexc continuation
       lexicons.

       The aim is to add a minimal set of rows into the lexc file in 
       hopes of not cluttering it too badly. E.g. we only add separate 
       independent and conjunct order forms if those are not identical. 
       If they are identical, we will instead add just one form into an 
       order-neutral continuation lexicon.  

       The legal values of `order_filter` are:
    
       * `"Independent"`: return the independent form if it differs from 
          the conjunct form, otherwise `None`.
       * `"PlainConjunct"`: return the conjunct form if it differs from
         the independent form, otherwise `None`.
       * `"Any"`: return the independent form if it is identical to the
         conjunct form, otherwise `None`.
       * `"ChangedConjunct"`: return a special changed-cnjunct form if 
         one is given. Otherwise, return `None`.

    """    
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

def get_load_pre_element_database(source_dirs,prefix_database):
    """Return a function which can be used to load the preverb database
       in a jinja template file. We need a specialized function because
       information about file paths is not accessible from the template.

    """    
    def load_pre_element_database(pv_tag,next_sublex):
        res = ""
        for source_dir in source_dirs:
            paradigm = sub("/$","",pv_tag)
            if not prefix_database in ["None", None] and not source_dir in ["None", None] :
                df = pd.read_csv(pjoin(source_dir, prefix_database))
                for _, pv in df.iterrows():
                    if pv.Paradigm == paradigm:
                        if res != "":
                            res += "\n"
                        tag = escape(f"{pv_tag}{pv.Lemma}+")
                        # We need to register our preverb/prenoun tag as a multicharacter symbol
                        LexcPath.multichar_symbols.add(tag)
                        res += f"{tag}:{pv.Stem} {next_sublex} ;"
        return res    
    return load_pre_element_database
    
def get_load_pre_element_csv(source_dir):
    """Return a function which can be used to load a preverb spreadsheet
       from a jinja template file. We need a specialized function because
       information about file paths is not accessible from the template.

    """    
    def load_pre_element_csv(sources,next_pv_lexicon,order_filter):
        entries = []
        for csv_fn, pv_tag in sources:
            df = pd.read_csv(pjoin(source_dir, csv_fn))
            for _, pv in df.iterrows():
                res = get_allomorph(pv, order_filter)
                if res != None and not "NONE" in res:
                    canonical, allomorph = res
                    canonical = pv_tag + canonical
                    # We need to define preverb/prenoun tag as a multichar symbol
                    LexcPath.multichar_symbols.add(f"{escape(canonical)}+")
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
    """Return a function which will generate Any, Independent,
       PlainConjuct and ChangedConjunct preverb lexicons in a jinja
       template file. We need a specialized function because
       information about file paths is not accessible from the
       template.
    """    
    load_pre_element_csv = get_load_pre_element_csv(source_dir)
    def generate_pre_element_sub_lexicons(sources,pv_lexicon):
        lexicons = [(f"LEXICON {pv_lexicon}{order_filter}\n" +
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
    """Split a string into lines of 80 characters at white space"""    
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
    """Return a function which harvests all preverb/prenoun tags from a
       spreadsheet.  The fucntion can be called from a jinja template
       file. We need a specialized function because information about
       file paths is not accessible from the template.

    """    
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
    """Return a function which adds multichar symbols from a config file
       to a Jinja template. We need a specialized function because
       information about file paths is not accessible from the
       template.

    """
    def add_lexeme_multichar_symbols():
        return pretty_join([escape(symbol) for symbol in config["multichar_symbols"]])
    return add_lexeme_multichar_symbols

def render_pre_element_lexicon(config,source_path,lexc_path):
    """ Render a preverb or prenoun Jinja template into lexc code."""
    csv_src_path = pjoin(source_path,config['pv_source_path'])
    template_file = basename(config['template_path'])
    template_dir = pjoin(expanduser(source_path),
                         dirname(config['template_path']))
    env = Environment(loader=FileSystemLoader(template_dir))
    database_src_dirs = config["database_src_dirs"]
    prefix_database = (config["lexical_prefix_database"]
                       if "lexical_prefix_database" in config
                       else "None")
    jinja_template = env.get_template(template_file)
    func_dict = {
        "all_pre_element_tags":
        get_all_pre_element_tags(csv_src_path),
        "load_pre_element_csv":
        get_load_pre_element_csv(csv_src_path),
        "load_pre_element_database":
        get_load_pre_element_database(database_src_dirs,prefix_database),
        "generate_pre_element_sub_lexicons":
        get_generate_pre_element_sub_lexicons(csv_src_path),
        "add_lexeme_multichar_symbols":
        get_add_lexeme_multichar_symbols(config)
    }
    jinja_template.globals.update(func_dict)
    template_string = jinja_template.render()
    with open(pjoin(lexc_path, template_file.replace(".j2","")),"w") as f:
        print(template_string, file=f)

def get_add_harvested_multichar_symbols(multichar_symbols):
    """Return a function which adds multichar symbols from a set
       to a Jinja template. We need a specialized function because
       information about file paths is not accessible from the
       template.

    """    
    def add_harvested_multichar_symbols():
        return pretty_join(sorted(multichar_symbols))
    return add_harvested_multichar_symbols

def render_root_lexicon(source_path, lexc_path):
    """ Render a root lexicon Jinja template into lexc code."""
    template_dir = dirname(expanduser(source_path))
    env = Environment(loader=FileSystemLoader(template_dir))
    template_file = basename(source_path)
    jinja_template = env.get_template(template_file)
    func_dict = {
        "add_harvested_multichar_symbols":
        get_add_harvested_multichar_symbols(LexcPath.multichar_symbols)
    }
    jinja_template.globals.update(func_dict)
    template_string = jinja_template.render()
    with open(pjoin(lexc_path, template_file.replace(".j2","")), "w") as f:        
        print(template_string, file=f)
