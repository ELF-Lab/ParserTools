from sys import stderr
import re
import pandas as pd
from collections import namedtuple
from log import warn

# Maximum number of alternate forms for a single analysis in the
# spreadsheets
MAXFORMS=5

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
    form = re.split(f"({PREFIX_BOUNDARY}|{SUFFIX_BOUNDARY})", form)
    if len(form) != 5:
        raise ValueError(f"Invald form: {form.to_dict()}")
    return SplitForm(form[0], form[2], form[4])


class ParadigmSlot:
    # All multichar symbols (across the entire lexc file) are stored
    # in this static set
    multichar_symbols:set[str] = None
    pre_element_tag:str = None
    
    @classmethod
    def __init_multichar_symbol_set(cls, conf:dict) -> None:
        """Must be called before any ParadigmSlot objects are initialized."""
        cls.multichar_symbols = set(map(escape,conf["multichar_symbols"]))
        cls.pre_element_tag = escape(conf["pre_element_tag"])
        cls.multichar_symbols.add(escape(PREFIX_BOUNDARY))
        cls.multichar_symbols.add(escape(SUFFIX_BOUNDARY))
        cls.multichar_symbols.add(cls.pre_element_tag)
        
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

    def __init__(self, row, conf, regular:bool):
        self.row = row
        self.conf = conf
        self.regular = regular
        self.paradigm = row["Paradigm"]
        self.klass = row["Class"]
        self.lemma = escape(row["Lemma"])
        self.stem = escape(row["Stem"])
        self.tags = [escape(f"+{row[feat]}")
                     for feat in conf["morph_features"]
                     if row[feat] != conf["missing_tag_marker"]]
        if ParadigmSlot.multichar_symbols == None:
            ParadigmSlot.__init_multichar_symbol_set(conf)
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
        """Convert this slot entry into a list of lexc lexicon paths
           starting at the Root lexicon and ending in #.

           There will be one path for each surface form.
        """
        paths = []
        paradigm = self.paradigm
        klass = self.klass
        pre_tag = ParadigmSlot.pre_element_tag
        for surface, parts in self.forms:
            if self.regular:
                pflag, rflag = ParadigmSlot.__get_prefix_flags(parts.prefix)
                prefix_id = "NONE" if parts.prefix == "" else parts.prefix.upper()
                # The following lexc sublexicon entries generate this form. 
                path = [
                    # @P.Prefix.<X>@:@P.Prefix.<X>@<x> <Paradigm>:PrefixBoundary ;
                    LexcEntry(f"{paradigm}:Prefix",
                              pflag,
                              pflag+parts.prefix,
                              f"{paradigm}:PrefixBoundary"),
                    # 0:%<%< <Paradigm>:PreElement ;
                    LexcEntry(f"{paradigm}:PrefixBoundary",
                              "0",
                              escape(PREFIX_BOUNDARY),
                              f"{paradigm}:PreElement"),
                    # <PreElement> <Paradigm>:Stems ;
                    LexcEntry(f"{paradigm}:PreElement",
                              pre_tag,
                              pre_tag,
                              f"{paradigm}:Stems"),
                    # <lemma>:<stem> <Paradigm>:Class=<class>:Boundary ;
                    LexcEntry(f"{paradigm}:Stems",
                              self.lemma,
                              self.stem,
                              f"{paradigm}:Class={klass}:Boundary"),
                    # 0:%>%> <Paradigm>:Class=<class>:Flags ;
                    LexcEntry(f"{paradigm}:Class={klass}:Boundary",
                              "0",
                              escape(SUFFIX_BOUNDARY),
                              f"{paradigm}:Class={klass}:Flags"),
                    # @R.Prefix.<X>@ <Paradigm>:Class=<class>:Prefix=<X>:Endings ;
                    LexcEntry(f"{paradigm}:Class={klass}:Flags",
                              rflag,
                              rflag,
                              f"{paradigm}:Class={klass}:Prefix={prefix_id}:Endings"),
                    # <tags>:<ending> # ;
                    LexcEntry(f"{paradigm}:Class={klass}:Prefix={prefix_id}:Endings",
                              "".join(self.tags),
                              parts.suffix,
                              "#")
                ]
                paths.append(path)
            else:
                # Irregular forms are treated as one chunk and simply enumerated.
                paths.append([LexcEntry(f"{paradigm}:Irregular",
                                        f"{self.lemma}{''.join(self.tags)}",
                                        surface,
                                        "#")])

        return paths

    def extend_lexicons(self, lexicons:dict) -> None:
        """Add the lexc path representing this slot to lexicons."""
        for entry in self.__get_lexc_paths():
            lexicons["Root"].add(LexcEntry("Root","0","0",entry[0].lexicon))
            for line in entry:
                if not line.lexicon in lexicons:
                    lexicons[line.lexicon] = set()
                lexicons[line.lexicon].add(line)
        
    def __str__(self):        
        entries = self.get_lexc_paths()
        res = ""
        for entry in entries:
            for sublex_entry in entry:
                res += f"{sublex_entry}\n"
            res += "----\n"
        return res

    def __hash__(self):
        return hash(str(self))
