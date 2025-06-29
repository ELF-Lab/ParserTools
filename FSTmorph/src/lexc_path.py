"""Functions and classes for converting a morphological paradigm
   spreadsheet row into one or more paths in a lexc file.

"""

import re
import pandas as pd
from collections import namedtuple
from .log import warn
from copy import deepcopy

MAXFORMS=100
"""Maximum number of alternate forms for a single analysis in the
    spreadsheets.

"""

PREFIX_BOUNDARY = "<<"
"""Morpheme boundary between prefix and stem."""

SUFFIX_BOUNDARY = ">>"
"""Morpheme boundary between stem and suffix."""

ALT_TAG = "+Alt"
""" Tag which indicates alternative or non-standard analyses. """

LexcEntry = namedtuple("LexcEntry",
                       ["lexicon",
                        "analysis",
                        "surface",
                        "next_lexicon"])
LexcEntry.__doc__ = \
"""LexcEntry represents a Lexc sublexicon entry like:

    ```
    LEXICON Lex
       upper:lower NextLex ;
    ```

    which corresponds to: 

    ```
    entry = LexcEntry("Lex", "upper", "lower", "NextLex")
    ```

    Access features as:

    ```
    entry.lexicon, entry.analysis, entry.surface, entry.next_lexicon
    ```
"""

SplitForm = namedtuple("SplitForm",
                       ["prefix",
                        "stem",
                        "suffix"])
SplitForm.__doc__ = \
"""SplitForm represents an inflected word form consisting of a
    prefix, stem and suffix:

    ```
    "pre<<st>>suf"
    ```

    corresponds to:

    ```
    split_form = SplitForm("pre","st","suf")
    ```

    Access features as:

    ```
    split_form.prefix, split_form.stem, split_form.suffix
    ```

"""


def entry2str(entry:LexcEntry) -> str:
    """Return the string representation of a LexcEntry object. When the
        upper and lower string are identical, the function will
        collapse them into one entry. If the upper and lower string
        are empty, only the continuation lexicon is retained.  This
        enhances readability of the lexc file.

    """
    if entry.analysis == entry.surface:
        if entry.analysis == "0":
            return f"{entry.next_lexicon} ;"
        else:
            return f"{entry.analysis} {entry.next_lexicon} ;"
    else:
        return f"{entry.analysis}:{entry.surface} {entry.next_lexicon} ;"

def escape(symbol:str) -> str:
    """Escape lexc special characters using a `%`. If the character is
        already escaped using `%`, don't add a second escape
        symbol. This function will escape symbols in the range
        `[!%<>0/#; ]`

    """
    return re.sub("(?<!%)([!%<>0/#; ])",r"%\1",symbol)

def split_form(form:str) -> SplitForm:
    """Split a form `prefix<<stem>>suffix` (e.g. found in the column
        `Form1Split` in paradigm spreadsheets) at morpheme boundaries
        (`<<` and `>>`). If either boundary is missing, the function
        will add one at the start and end and issue a warning. A
        SplitForm object is returned.

    """
    # re.split results in a 5-element array [prefix, "<<", stem, ">>",
    # suffix]
    if not PREFIX_BOUNDARY in form:
        form = PREFIX_BOUNDARY + form
        warn(f"Invalid segmented form: {form}. Appending morpheme boundary '{PREFIX_BOUNDARY}' at the start.")    
    if not SUFFIX_BOUNDARY in form:
        form += SUFFIX_BOUNDARY
        warn(f"Invalid segmented form: {form}. Appending morpheme boundary '{SUFFIX_BOUNDARY}' at the end.")
    form = re.split(f"({PREFIX_BOUNDARY}|{SUFFIX_BOUNDARY})", form)
    if len(form) != 5:
        raise ValueError(f"Invalid form: {orig_form}. Split: {form}")
    return SplitForm(escape(form[0]), escape(form[2]), escape(form[4]))

class LexcPath:
    """The LexcPath class represents a path in a lexc file from a root
       lexicon like `VerbRoot` or `NounRoot` to the terminal lexicon
       `#`. This path corresponds to a list of LexcEntry objects: 

       ``` [entry_1, entry_2, ..., entry_n] ``` 

       where `entry_1.lexicon` is the root lexicon, 
       `entry_i+1.lexicon = entry_i.next_lexicon` and
       `entry_n.next_lexicon = "#"`

       A lexc file can be thought of as a union of this type of paths.

       A LexcPath object encodes all the information on one spreadsheet
       row (e.g. a row in VTA_IND.csv in the OjibweMorph repo). Thus
       the path can contain multiple surface forms (Surface1Form,
       Surface2Form, ...). LexcPath can therefore encode multiple
       sub-lexicon entries e.g. corresponding to alternative endings of
       an inflected form.
    """

    multichar_symbols:set[str] = set()
    """Multichar symbols (across all lexc files) are stored in this static
       set

    """

    @classmethod
    def update_multichar_symbol_set(cls, conf:dict) -> None:
        """This function adds all multicharacter symbols speficied in a
           configuration file + morpheme boundaries into the
           `multichar_symbols` set.

        """
        cls.multichar_symbols.update(map(escape,conf["multichar_symbols"]))
        cls.multichar_symbols.add(escape(PREFIX_BOUNDARY))
        cls.multichar_symbols.add(escape(SUFFIX_BOUNDARY))
        cls.multichar_symbols.add(escape(ALT_TAG))
        
    @classmethod
    def get_prefix_flags(cls, prefix:str) -> tuple[str]:
        """Get P and R flag diacritics like @P.Prefix.NI@ which
           determine valid combinations of prefixes and suffixes.

           The flag diacritics will be added to `multichar_symbols`.

        """
        prefix = "NONE" if prefix == "" else prefix.upper()
        pflag, rflag = f"@P.Prefix.{prefix}@", f"@R.Prefix.{prefix}@"
        cls.multichar_symbols.update([pflag, rflag])
        return pflag, rflag

    @classmethod
    def get_paradigm_flags(cls, paradigm:str) -> tuple[str]:
        """Get P and R flag diacritics for a given paradigm like VTA.

           The flag diacritics will be added to `multichar_symbols`.

        """        
        pflag, rflag = f"@P.Paradigm.{paradigm}@", f"@R.Paradigm.{paradigm}@"
        cls.multichar_symbols.update([pflag, rflag])        
        return pflag, rflag
    
    def get_order_flag(self) -> tuple[str]:
        """Get a U flag matching the order of this LexcPath: Ind, Cnj or
           Other (in case of imperative or other unspecified order).

           The flag diacritic will be added to `multichar_symbols`.
        """
        order = "Other"
        if "+Ind" in self.tags:
            order = "Ind"
        elif "+Cnj" in self.tags:
            order = "Cnj"
        flag = f"@U.Order.{order}@"
        LexcPath.multichar_symbols.update([flag])
        return order, flag

    def __init__(self, row:pd.core.series.Series, conf:dict, regular:bool):
        """Initialize this LexcPath using the configuration file conf and a
        spreadsheet row. The boolean parameter regular determines whether this
        is treated as a regular form (which should have morpheme boundaries
        and undergo phonological rules) or an irregular form which is stored
        in the lexc file in verbatim.

        All morphological features like "+VTA", "+Ind" and "+1SgSubj"
        apperaing on the spreadsheet row will be added to
        multichar_symbols.

        """
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
        self.harvest_multichar_symbols()

        try:
            self.read_forms(row, conf)
        except ValueError as e:
            warn(e, force=False)
            
    def harvest_multichar_symbols(self) -> None:
        """Add all morphological features like "+VTA", "+Ind" and "+1SgSubj"
           from this path to the multichar_symbols set

        """
        for tag in self.tags:
            LexcPath.multichar_symbols.add(tag)

    def read_forms(self, row:pd.core.series.Series, conf:dict) -> None:
        """Read all forms on the given dataframe row. Store both the plain
           surface form and segmented form.

        """
        def get_form_indices() -> list[int]:
            # Return all indices i which are associated with a surface
            # form on this row, i.e. i where Form{i}Surface is a
            # column on the row and the form in that column is
            # non-empty.
            missing = conf["missing_form_marker"]
            return [i for i in range(MAXFORMS) if f"Form{i}Surface" in row and
                                                  not row[f"Form{i}Surface"] in [missing, ""]]
        
        self.forms = [(row[f"Form{i}Surface"], split_form(row[f"Form{i}Split"]))
                      for i in get_form_indices()]
        if len(self.forms) == 0:
            raise ValueError(f"No surface forms given for row: {row.to_dict()}")
        
    def get_lexc_paths(self) -> list[list[LexcEntry]]:
        """Convert this path into a list of lexc lexicon paths starting
           at a person prefix lexicon (this could be VTA_Prefix, NA_Prefix, 
           etc.) and ending in the terminal lexicon #. Each path is a 
           sequence of lexc sublexicon entries.

           There will be one list-element for each surface form (note that 
           there may be several surface forms Form1Surface, Form2Surface, 
           ...).

           For inflected forms of regular lexemes, our paths will look
           like this (here, for the example analysis and intermediate form
           `aaba'+VTA+Ind+Neg+Dub+0Pl+1Sg:ni<<aaba'w>>igosiinaadogenan`):

           ```
              ! Person prefix lexicon for nouns and verbs. For all other 
              ! word classes the prefix is always empty (@P.Prefix.NONE@)
              LEXICON VTA_Prefix
              @P.Prefix.NI@:@P.Prefix.NI@ni VTA_PrefixBoundary ;

              ! Morpheme boundary for person prefix. Note that we can jump
              ! to a preverb lexicon here. For all word classes apart from
              ! nouns and verbs, we jump directly to the a stem lexicon.
              LEXICON VTA_PrefixBoundary
              0:%<%< PreverbRoot ;
        
              ! After adding preverbs, we return to this lexicon. Need to
              ! match the correct paradigm here
              LEXICON VerbStems
              @R.Paradigm.VTA@ VTA_Stems ;

              ! Stem lexicon. aaba' belongs to the VTA_C inflection class,
              ! so we continue to the VTA_C suffix boundary lexicon.
              LEXICON VTA_Stems
              aaba':aaba'w VTA_Class=VTA_C_Boundary ;

              ! Suffix boundary
              LEXICON VTA_Class=VTA_C_Boundary
              0:%>%> VTA_Class=VTA_C_Flags ;

              ! This sublexicon makes sure that we get the correct 
              ! combination of person prefix ("ni-" in this case) and ending.
              ! The combinatorics is handled by matching the value of the 
              ! feature Prefix (NI in this case).
              LEXICON VTA_Class=VTA_C_Flags
              @R.Prefix.NI@ VTA_Class=VTA_C_Flags_Prefix=NI ;

              ! We need to match the correct order here
              LEXICON VTA_Class=VTA_C_Flags_Prefix=NI ;
              @U.Order.Ind@ VTA_Class=VTA_C_Prefix=NI_Order=Ind_Endings ;

              ! This lexicon enumerates endings for the inflection class
              ! VAT_C which correspond to person prefix "ni-" and order Ind.
              LEXICON VTA_Class=VTA_C_Prefix=NI_Order=Ind_Endings
              +VTA+Ind+Neg+Dub+%0PlSubj+1SgObj:igosiinaadogenan # ;
           ```

           For inflected forms of irregular lexemes, our paths become
           very simple. We just enumerate the entire form as one
           chunk without morpheme boundaries. This effectively prevents any
           phonological rules from applying, which is exactly what we want
           for irregular lexemes:

           ```
              LEXICON ROOT
              VTA_Irregular ;

              LEXICON VTA_Irregular
              izhi+VTA+Ind+Pos+Neu+%0Pl+1Sg:nindigonan # ;
           ```
        """
        paths = []
        paradigm = self.paradigm
        klass = self.klass
        for i, (surface, parts) in enumerate(self.forms):
            tags = deepcopy(self.tags)
            # Possibly append a +Alt tag to all analyses except the
            # first one.
            if i > 0 and self.conf["append_alt_tag"]:
                tags.append(ALT_TAG)
            if self.regular:
                # Initialize flag diacritics which:
                # (1) control combinations of person prefix and inflectional ending,
                # (2) check that we've got the correct paradigm (this is needed to
                #     make sure that return to the correct paradigm after adding
                #     preverbs), and
                # (3) check the order (we track this because subordinate preverbs
                #     and the changed-conjunct marker require conjunct order and some
                #     preverbs have distinct independent and conjunct order surface
                #     forms) 
                set_prefix_flag, check_prefix_flag = LexcPath.get_prefix_flags(parts.prefix)
                _, check_paradigm_flag = LexcPath.get_paradigm_flags(paradigm)
                order, check_order_flag = self.get_order_flag()

                # Initialize the person prefix for this form
                prefix = "NONE" if parts.prefix == "" else parts.prefix.upper()

                # Initialize continuation lexicons needed on this path
                person_prefix_lexicon = f"{paradigm}_Prefix"
                morpheme_boundary_lexicon = f"{paradigm}_PrefixBoundary"
                preverb_lexicon = (self.conf["prefix_root"] # This can also be the prenoun lexicon depending on paradigm
                                   if "prefix_root" in self.conf
                                   else None)
                pos_stem_lexicon = f"{self.conf['pos']}Stems" # E.g. VerbStems
                paradigm_stem_lexicon = f"{paradigm}_Stems" # E.g. VTA_Stems
                inflection_class_lexicon = f"{paradigm}_Class={klass}_Boundary"
                check_prefix_lexicon = f"{paradigm}_Class={klass}_Flags"
                check_order_lexicon = f"{paradigm}_Class={klass}_Flags_Prefix={prefix}"
                ending_lexicon = f"{paradigm}_Class={klass}_Prefix={prefix}_Order={order}_Endings"
                
                path = [
                    LexcEntry(person_prefix_lexicon,
                              set_prefix_flag,
                              set_prefix_flag+parts.prefix,
                              morpheme_boundary_lexicon),
                    LexcEntry(morpheme_boundary_lexicon,
                              "0",
                              escape(PREFIX_BOUNDARY),
                              preverb_lexicon or pos_stem_lexicon),
                    LexcEntry(pos_stem_lexicon,
                              check_paradigm_flag,
                              check_paradigm_flag,
                              paradigm_stem_lexicon),
                    LexcEntry(paradigm_stem_lexicon,
                              self.lemma,
                              self.stem,
                              inflection_class_lexicon),
                    LexcEntry(inflection_class_lexicon,
                              "0",
                              escape(SUFFIX_BOUNDARY),
                              check_prefix_lexicon),
                    LexcEntry(check_prefix_lexicon,
                              check_prefix_flag,
                              check_prefix_flag,
                              check_order_lexicon),
                    LexcEntry(check_order_lexicon,
                              check_order_flag,
                              check_order_flag,
                              ending_lexicon),
                    LexcEntry(ending_lexicon,
                              "".join(tags),
                              parts.suffix,
                              "#")
                ]
                paths.append(path)
            else:
                # Irregular forms are treated as one chunk and simply enumerated.
                paths.append([LexcEntry(f"{paradigm}_Irregular",
                                        f"{self.lemma}{''.join(tags)}",
                                        surface,
                                        "#")])

        return paths

    def extend_lexicons(self, lexicons:dict) -> None:
        """Add the all lexicon entries on this path to lexicons. The parameter
           lexicons represents all sublexicons in the lexc file and their lexicon
           entries.

        """
        def get_paradigm(s):
            return re.sub("[_].*","",s)
        for path in self.get_lexc_paths():
            paradigm = get_paradigm(path[0].lexicon)
            p_paradigm_flag, _ = LexcPath.get_paradigm_flags(paradigm)
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

class DerivationPath:
    def __init__(self, row:pd.core.series.Series, conf:dict):
        self.conf = conf
        self.form = row.Form
        self.tag = f"+{row.Tag}"
        self.input_paradigm = row.InputParadigm
        self.input_class = row.InputClass
        self.output_paradigm = row.OutputParadigm
        self.output_class = row.OutputClass
        LexcPath.multichar_symbols.update([self.tag])
        
    def extend_lexicons(self, lexicons:dict) -> None:
        input_boundary_lexicon = f"{self.input_paradigm}_Class={self.input_class}_Boundary"
        analysis = f"+{self.input_paradigm}{self.tag}"
        surface = f"0{escape(SUFFIX_BOUNDARY)}{self.form}"
        output_boundary_lexicon = f"{self.output_paradigm}_Class={self.output_class}_Boundary"
        if not input_boundary_lexicon in lexicons:
            lexicons[input_boundary_lexicon] = set()
        lexicons[input_boundary_lexicon].add(LexcEntry(input_boundary_lexicon,
                                                       analysis,
                                                       surface,
                                                       output_boundary_lexicon))
        
