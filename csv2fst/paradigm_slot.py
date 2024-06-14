from sys import stderr
import re
import pandas as pd
from collections import namedtuple
from log import warn

# Maximum number of alternate forms for a single analysis in the
# spreadsheets
MAXFORMS=100

PREFIX_BOUNDARY = "<<"
SUFFIX_BOUNDARY = ">>"

# LexcEntry represents a lexc sublexicon entry 
LexcEntry = namedtuple("LexcEntry",
                       ["lexicon",
                        "analysis",
                        "surface",
                        "next_lexicon"])

# SplitForm represents a form consisting of a prefix, stem and suffix
SplitForm = namedtuple("SplitForm",
                       ["prefix",
                        "stem",
                        "suffix"])

def entry2str(entry:LexcEntry) -> str:
    """ Return the string representation of a lexc lexicon entry """
    if entry.analysis == entry.surface:
        if entry.analysis == "0":
            return f"{entry.next_lexicon} ;"
        else:
            return f"{entry.analysis} {entry.next_lexicon} ;"
    else:
        return f"{entry.analysis}:{entry.surface} {entry.next_lexicon} ;"

def escape(symbol:str) -> str:
    """ Escape lexc special characters using a %-sign """
    return re.sub("(?<!%)([!%<>0/#; ])",r"%\1",symbol)

def split_form(form:str) -> SplitForm:
    """Split a form prefix<<stem>>suffix at boundaries."""
    # re.split results in a 5-element array [prefix, "<<", stem, ">>",
    # suffix]
    if not "<<" in form:
        form = "<<" + form
        warn("Invalid form: {form}. Appending morpheme boundary '<<' at the start.")    
    if not ">>" in form:
        form += ">>"
        warn("Invalid form: {form}. Aappending morpheme boundary '>>' at the end.")
    form = re.split(f"({PREFIX_BOUNDARY}|{SUFFIX_BOUNDARY})", form)
    if len(form) != 5:
        raise ValueError(f"Invalid form: {orig_form}. Split: {form}")
    return SplitForm(escape(form[0]), escape(form[2]), escape(form[4]))


class ParadigmSlot:
    # All multichar symbols (across the entire lexc file) are stored
    # in this static set
    multichar_symbols:set[str] = set()
    pre_element_tag:str = None
    
    @classmethod
    def update_multichar_symbol_set(cls, conf:dict) -> None:
        """Must be called when the first ParadigmSlot object is
           initialized."""
        cls.multichar_symbols.update(set(map(escape,conf["multichar_symbols"])))
        #cls.pre_element_tag = escape(conf["pre_element_tag"])
        cls.multichar_symbols.add(escape(PREFIX_BOUNDARY))
        cls.multichar_symbols.add(escape(SUFFIX_BOUNDARY))
        #cls.multichar_symbols.add(cls.pre_element_tag)
        
    @classmethod
    def __get_prefix_flags(cls, prefix:str) -> tuple[str]:
        """Get the P and R flags like @P.Prefi.=NI@ which determine valid
           combinations of prefixes and suffixes.

            The flag diacritics will be added to multichar symbols.
        """
        prefix = "NONE" if prefix == "" else prefix.upper()
        pflag, rflag = f"@P.Prefix.{prefix}@", f"@R.Prefix.{prefix}@"
        cls.multichar_symbols.update([pflag, rflag])
        return pflag, rflag

    @classmethod
    def __get_paradigm_flags(cls, paradigm:str) -> tuple[str]:
        pflag, rflag = f"@P.Paradigm.{paradigm}@", f"@R.Paradigm.{paradigm}@"
        cls.multichar_symbols.update([pflag, rflag])        
        return pflag, rflag
    
    def __get_order_flag(self) -> tuple[str]:
        order = "Other"
        if "+Ind" in self.tags:
            order = "Ind"
        elif "+Cnj" in self.tags:
            order = "Cnj"
        flag = f"@U.Order.{order}@"
        ParadigmSlot.multichar_symbols.update([flag])
        return order, flag

    def __init__(self, row, conf, regular:bool):
        self.root_lexicon = conf["root_lexicon"]
        self.row = row
        self.conf = conf
        self.regular = regular
        self.paradigm = row["Paradigm"]
        self.klass = row["Class"]
        self.lemma = escape(row["Lemma"])
        self.stem = escape(row["Stem"])
        self.tags = [escape(f"+{row[feat]}")
                     for feat in conf["morph_features"]
                     if (row[feat] != conf["missing_tag_marker"] and
                         row[feat] != "")]
#        if ParadigmSlot.multichar_symbols == None:
#        ParadigmSlot.__upda_multichar_symbol_set(conf)
        self.__harvest_multichar_symbols()

        try:
            self.__read_forms(row, conf)
        except ValueError as e:
            warn(e)
            
    def __harvest_multichar_symbols(self) -> None:
        """Add all multichar symbols from this entry to the multichar symbol
           set
        """
        for tag in self.tags:
            ParadigmSlot.multichar_symbols.add(tag)

    def __read_forms(self, row:pd.core.series.Series, conf:dict) -> None:
        """Read all forms on the given dataframe row."""
        self.forms = [(row[f"Form{i}Surface"], split_form(row[f"Form{i}Split"]))
                      for i in range(MAXFORMS)
                      if (f"Form{i}Surface" in row and
                          row[f"Form{i}Surface"] != conf["missing_form_marker"] and
                          row[f"Form{i}Surface"] != "")]
        if len(self.forms) == 0:
            raise ValueError(f"No surface forms given for row: {row.to_dict()}")
        
    def __get_lexc_paths(self) -> list[list[LexcEntry]]:
        """Convert this slot entry into a list of lexc lexicon paths starting
           at the ROOT lexicon (this could be VerbRoot, NounRoot etc.)
           and ending in #. Each path is a sequence of lexc sublexicon
           entries.

           There will be one path for each surface form.

           For inflected forms of regular lexemes, our paths will look
           like this (here, for the example analysis and form
           aaba'+VTA+Ind+Neg+Dub+0Pl+1Sg:aaba'wigosiinaadogenan):

              LEXICON ROOT
              VTA:Prefix ;

              LEXICON VTA:Prefix
              @P.Prefix.NI@:@P.Prefix.NI@ni VTA:PrefixBoundary ;

              LEXICON VTA:PrefixBoundary
              0:%<%< VTA:PreElement ;

              LEXICON VTA:PreElement
              [PREVERB] VTA:Stems ;

              LEXICON VTA:Stems
              aaba':aaba'w VTA:Class=VTA_C:Boundary ;

              LEXICON VTA:Class=VTA_C:Boundary
              0:%>%> VTA:Class=VTA_C:Flags ;

              LEXICON VTA:Class=VTA_C:Flags
              @R.Prefix.NI@ VTA:Class=VTA_C:Prefix=NI:Endings ;

              LEXICON VTA:Class=VTA_C:Prefix=NI:Endings
              +VTA+Ind+Neg+Dub+%0Pl+1Sg:igosiinaadogenan # ;

           For inflected forms of irregular lexemes, our pahts become
           very simple. We just enumerate the entire form as one
           chunk:

              LEXICON ROOT
              VTA:Irregular ;

              LEXICON VTA:Irregular
              izhi+VTA+Ind+Pos+Neu+%0Pl+1Sg:nindigonan # ;

        """
        paths = []
        paradigm = self.paradigm
        klass = self.klass
        pre_tag = ParadigmSlot.pre_element_tag
        for surface, parts in self.forms:
            if self.regular:
                p_prefix_flag, r_prefix_flag = ParadigmSlot.__get_prefix_flags(parts.prefix)
                _, r_paradigm_flag = ParadigmSlot.__get_paradigm_flags(paradigm)
                order, r_order_flag = self.__get_order_flag()
                prefix_id = "NONE" if parts.prefix == "" else parts.prefix.upper()
                # The following lexc sublexicon entries generate this form. 
                path = [
                    # @P.Prefix.<X>@_@P.Prefix.<X>@<x> <Paradigm>_PrefixBoundary ;
                    LexcEntry(f"{paradigm}_Prefix",
                              p_prefix_flag,
                              p_prefix_flag+parts.prefix,
                              f"{paradigm}_PrefixBoundary"),
                    # 0_%<%< <Paradigm>_PreElement ;
                    LexcEntry(f"{paradigm}_PrefixBoundary",
                              "0",
                              escape(PREFIX_BOUNDARY),
                              self.conf["prefix_root"]
                              if "prefix_root" in self.conf
                              else f"{self.conf['pos']}Stems"),
#                              f"{paradigm}_PreElement"),
                    # <PreElement> <Paradigm>_Stems ;
                    LexcEntry(f"{self.conf['pos']}Stems",
                              r_paradigm_flag,
                              r_paradigm_flag,
                              f"{paradigm}_Stems"),
                    # <lemma>_<stem> <Paradigm>_Class=<class>_Boundary ;
                    LexcEntry(f"{paradigm}_Stems",
                              self.lemma,
                              self.stem,
                              f"{paradigm}_Class={klass}_Boundary"),
                    # 0_%>%> <Paradigm>_Class=<class>_Flags ;
                    LexcEntry(f"{paradigm}_Class={klass}_Boundary",
                              "0",
                              escape(SUFFIX_BOUNDARY),
                              f"{paradigm}_Class={klass}_Flags"),
                    # @R.Prefix.<X>@ <Paradigm>_Class=<class>_Prefix=<X>_Endings ;
                    LexcEntry(f"{paradigm}_Class={klass}_Flags",
                              r_prefix_flag,
                              r_prefix_flag,
                              f"{paradigm}_Class={klass}_Prefix={prefix_id}_Order={order}"),
                    # @U.Order.<Y>@ <Paradigm>_Class=<class>_Prefix=<X>_Order=<Y>_Endings
                    LexcEntry(f"{paradigm}_Class={klass}_Prefix={prefix_id}_Order={order}",
                              r_order_flag,
                              r_order_flag,
                              f"{paradigm}_Class={klass}_Prefix={prefix_id}_Order={order}_Endings"),
                    # <tags>_<ending> # ;
                    LexcEntry(f"{paradigm}_Class={klass}_Prefix={prefix_id}_Order={order}_Endings",
                              "".join(self.tags),
                              parts.suffix,
                              "#")
                ]
                paths.append(path)
            else:
                # Irregular forms are treated as one chunk and simply enumerated.
                paths.append([LexcEntry(f"{paradigm}_Irregular",
                                        f"{self.lemma}{''.join(self.tags)}",
                                        surface,
                                        "#")])

        return paths

    def extend_lexicons(self, lexicons:dict) -> None:
        """Add the lexc paths representing this slot to lexicons."""
        def get_paradigm(s):
            return re.sub("[_].*","",s)
        for path in self.__get_lexc_paths():
            paradigm = get_paradigm(path[0].lexicon)
            p_paradigm_flag, _ = ParadigmSlot.__get_paradigm_flags(paradigm)
            lexicons[self.root_lexicon].add(LexcEntry(self.root_lexicon,
                                                      p_paradigm_flag,
                                                      p_paradigm_flag,
                                                      path[0].lexicon))
            for lexc_entry in path:
                if not lexc_entry.lexicon in lexicons:
                    lexicons[lexc_entry.lexicon] = set()
                lexicons[lexc_entry.lexicon].add(lexc_entry)
        
    def __str__(self):        
        paths = self.get_lexc_paths()
        res = ""
        for path in paths:
            for lexc_entry in path:
                res += f"{lexc_entry}\n"
            res += "----\n"
        return res

    def __hash__(self):
        return hash(str(self))
