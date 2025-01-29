# [OjibweMorph](https://github.com/ELF-Lab/OjibweMorph/)

The following directories are included in the OjibweMorph repository:

| Directory | Description |
|-----------|-------------|
| `NounSpreadsheets` | Morphological paradigms for nouns (CSV spredsheets) | 
| `OtherSpreadsheets` | Morphological paradigms for uninflecting classes (CSV spreadsheets) |
| `PVSpreadsheets` | Preverbs spreadsheets (CSV spreadsheets) |
| `VerbSpreadsheets` | Morphological paradigms for verbs (CSV spreadsheets)
| `config` | Configuration files for compiling lexc files from spreadsheets for different word classes (json code) |
| `lexc` | Legacy lexc files (not used) |   
| `templates` | Jinja templates for lexc files (j2 files). Used by ParserTools during compilation. |
| `xfst` | Xfst phonological rewrite rules. Used by foma during compilation. |

## Morphological paradigm spreadsheets

We have spreadsheets both for nouns and verbs. All lexical spreadsheets follow this overall structure:

| Paradigm | Order | Class | Lemma | Stem | Subject | Object | Mode | Negation | Form1Surface | Form1Split | Form1Source | Form2Surface | Form2Split | Form2Source | 
|----------|-------|-------|-------|------|---------|--------|------|----------|--------------|------------|-------------|--------------|------------|-------------|
| `VTA` | `Ind` | `VTA_C` | `waabam` | `waabam` | `0PlSubj` | `3SgObvObj` | `Neu`  | `Pos` | `owaabamigonan` | `o<<waabam>>igonan` | `NJ-ngs-2023-Aug19` | `owaabamigonini` | `o<<waabam>>igoniniw1` | `JRV-Web-ANISH` |
| `VTA` | `Ind` | `VTA_Cw` | `mizho` | `mizhw` | `0PlSubj` | `3SgObvObj` | `Neu` | `Pos` | `omizhogonan` | `o<<mizho>>igonan` | `NJ-ngs-2023-Aug19` |  | |  |	

Each row in the spreadsheets corresponds to a specific combination of lemma and morphological features. It will always specify at least one inflected surface realization like `owaabamigonan`, here corresponding to the analysis `waabam+VAT+Ind+Pos+Neu+0PlSubj+3SgObvObj`. However, there will frequently be more than one possible surface forms. In this example both `owaabamigonan` and `owaabamigonini` correspond to the same analysis.

Seven of the columns are obligatory:

* **Paradigm** gives the general category of the form (nouns: `NA`, `NAD`, `NI`, `NID`; verbs: `VAI`, `VII`, `VTA`, `VTI`; others: e.g. `ADVConj`, `PRONDem`, `NUM`, `PCInterj`)
* **Class** gives the inflectional class of the form. E.g. `VTA_C` represents `VTA` verbs where the stem ends in a consonant like `waabam`, `VTA_Cw` represents `VTA` verbs ending in a consonant followed by `w`.
* **Lemma** is the baseform of the lexeme
* **Stem** is default the stem of this lexeme
* **Form1Surface** gives the word form itself
* **Form1Split** gives a split of the form into `prefix<<stem>>suffix`. Note that the `stem` here doesn't need to correspond to the **Stem** colum because the stem might vary due to phonolgical factors based on the prefix and suffix (this is the case for the form `omizhogonan`, where the default stem `mizhw` is realized as `mizho` in this specific form). We have xfst replace rules which transform the stem in the **Stem** column into its various realizations.

Additionally **Form1Source** can be used to indicate information about the given form, which elder it comes from, which dialect etc. Additional forms are given by specifying **Form2Surface**, **Form2Split**, **Form3Surface**, **Form3Split**, etc. When these forms are missing, the fields can be left empty.

Note that the stem and affixes can sometimes contain special charcters like `w1` in `o<<waabam>>igoniniw1`. These need to be listed in a configuration file as specified below. Otherwise, lexc won't know to compile them into multi-character symbols (Note to self: maybe introduce a special format instead so these can be identified automatically?).

Morphological features (here: **Order**, **Mode**, **Negation**, **Subject**, **Object**) can vary by paradigm (e.g. they are different for nouns and verbs) and the set is customizable using a configuation file.

Sometimes the value of a particular morphological feature is missing. For example, VII verbs don't take an object. In such cases, we can use a `NONE` value to indicate the missing field:

| Paradigm | Order | Class | Lemma | Stem | Subject | Object | Mode | Negation | Form1Surface | Form1Split | Form1Source | Form2Surface | Form2Split | Form2Source | 
|----------|-------|-------|-------|------|---------|--------|------|----------|--------------|------------|-------------|--------------|------------|-------------|
| `VII`    | `Ind` | `VII_VV` | `ate` | `ate` | `0PlObvSubj` | `NONE` | `Dub` | `Neg` | `atesininiwidogen` | `<<ate>>sininiwidogen` | `JDN-2010-MS-VII-p9` |

In addition to the aforementioned columns, the spreadsheet can include other columns as well. For example **Notes**, could be a useful one in some cases.

## Preverb (and prenoun) spreadsheets

## Configuration files

Configuration files are used to control the compilation of lexc files for a particular word class (nouns, verbs, pronouns, numerals, adverbs and particles). The configuration file all if the central ifformation related to compilation: which spreadsheets to use as source, what the morphological features are, whether to include prenouns/preverbs etc. Below, you can see a description of all the features which can be specified along with an example configuration file for Ojibwe verbs: 

| Feature | Description | Value | Notes |
|---------|-------------|-------|-------|
| `"pos"` | Word class  | `"Verb"`, `"Noun"`, ... | |
| `"root_lexicon"` | Root lexicon name | `"VerbRoot"`, `"NounRoot"`, ...| Word class specific root lexicon  | This could be automatically deduced |
| `"morphology_source_path"` | Path to paradigm spreadsheets for this word class | "VerbSreadsheets" | This would usually be a directory in `OjibweMorph`. Note that the parent morphology directory (e.g. the path to OjibweMorph) is provided as a command-line argument to `csv2lexc.py`. |
| `"regular_csv_files"` | List of spreadsheets to include when compiling **regular** lexemes | `["VTA_IND"`, "VTI_CNJ", ... ]` | Spreadhseets listed here will undergo regular phonological rules. |
| `"irregular_csv_files"` | List of spreadsheets to include when compiling **irregular** lexemes | `["VTA_IRR"]` | Spreadsheets listed here will not undergo any phonological rules. This is catgory is meant for lexemes which do not belong to a larger inflection class, and where we simply list every single inflected form in verbatim. In Ojibwe, the only irregular verb is `izhi`. |
| `"lexical_database"` | Path to lexical database | `VERBS.csv` | This would typically be a file in `OPDDatabase`. Note that the parent lexical database directory (e.g. the path to OPDDatabase) is provided as a command-line argument to `csv2lexc.py`. |
| `"lexical_prefix_database"` | Path to preverb/prenoun database | `"LEXICAL_PREVERBS.csv"` | This would typically be a file in `OPDDatabase`. Note that the parent lexical database directory (e.g. the path to OPDDatabase) is provided as a command-line argument to `csv2lexc.py`. |
| `"regular_lexc_file"` | Store compiled lexc code for regular paradigms in this file | `"ojibwe_verbs.lexc"` | Note that a target directory, where all lexc code is stored, is given as a commandline argument to `csv2fst.py` |
| `"irregular_lexc_file"` | Store compiled lexc code for irregular paradigms in this file | `"ojibwe_irregular_verbs.lexc"` | Note that a target directory, where all lexc code is stored, is given as a commandline argument to `csv2fst.py` |
| `"morph_features"` | This list specifies the columns in the paradigm spreadsheets which are used as morphological features. | `[ "Paradigm", "Order", "Negation",  ... ]` | This list specifies both which columns to use from a spreasheet like `VTA_IND.csv` and the order in which the features appear in the analysis. E.g. `VTA+Ind+Pos...` |
| `"missing_tag_marker"` | This symbol is used to mark tags like grammatical object for VIIs which might be missing from the spreadsheet. | `"NONE"` | |
| `"missing_form_marker"` | This symbol is used to mark morphological gaps, where an analysis has no surface realizations. | `"MISSING"` | Sometimes we might simply not know what the form looks like. We might also not know if a form even exists. This happens e.g. with dubitative preterite forms in Ojibwe, which currently are poorly documented and understood. Sometimes, we know that the sureface realization is impossible due to a logical contradiction. |
| `"multichar_symbols"` | List of multi-character symbols | `["w1", "y1", "y2", ...]` | Rules often reference special multi-character symbols like `"w1"`. These are included in spreadsheets (sometimes also the lexical database) and need to be declared so that they can be added to the lexc `Multichar_Symbols` section. |
| `"prefix_root"` | Custom root lexicon for prenouns/preverbs | `"PreverbRoot"` | Can be omitted when there are no prenouns/preverbs and for all other word classes except nouns and verbs. |
| `"template_path"` | Path to jinja lexc template file for prenouns/preverbs | `"templates/preverbs.lexc.j2"` | This would typically be a file in `OjibweMorph`. Note that the parent morphology directory (e.g. the path to OjibweMorph) is provided as a command-line argument to `csv2lexc.py`. Can be omitted when no preverbs/prenouns are included and for all word classes apart from nouns and verbs. |
| `"pv_source_path"` | Path to preverb/prenoun spreadsheets | `"PVSpreadsheets"` | This would typically be a file in `OjibweMorph`. Note that the parent morphology directory (e.g. the path to OjibweMorph) is provided as a command-line argument to `csv2lexc.py`. Can be omitted when no preverbs/prenouns are included and for all word classes apart from nouns and verbs. |
```
OjibweMorph/config/ojibwe_verbs.json:

{
    "pos":"Verb",
    "root_lexicon":"VerbRoot",
    "morphology_source_path": "VerbSpreadsheets/",
    "regular_csv_files": [
        "VAIO_CNJ",
        "VAIO_IMP",
        "VAIO_IND",
        "VAI_CNJ",
        "VAI_IMP",
        "VAI_IND",
        "VAIPL",
        "VAI_Reflex_Recip",
        "VII_CNJ",
        "VII_IND",
        "VIIPL",      
        "VTA_CNJ",
        "VTA_IMP",
        "VTA_IND",
        "VTI_CNJ",
        "VTI_IMP",
        "VTI_IND"
    ],
    "irregular_csv_files": [
        "VTA_IRR"
    ],
    "lexical_database": "VERBS.csv",
    "lexical_prefix_database": "LEXICAL_PREVERBS.csv",
    "regular_lexc_file": "ojibwe_verbs.lexc",
    "irregular_lexc_file": "ojibwe_irregular_verbs.lexc",
    "morph_features": [
        "Paradigm",
        "Order",
        "Negation",
        "Mode",
        "Subject",
        "Object"
    ],
    "missing_tag_marker": "NONE",
    "missing_form_marker": "MISSING",
    "multichar_symbols": [
        "i1",
        "s1",
        "n1",
        "w1",
        "V1",
        "w2",
        "<T>"
    ],
    "prefix_root":"PreverbRoot",
    "template_path":"templates/preverbs.lexc.j2",
    "pv_source_path":"PVSpreadsheets"  
}
```

## Jinja lexc templates

Prenoun and preverb lexc files as well as `root.lexc` file (which contains the common root sub-lexicon for all generated lexc-files) are simpler than verba and noun lexc files and are, therefore, compiled from [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) templates in `OjibweMorph/templates`. These very closely resemble lexc-code but also contain python function calls, which dynamically generate required content, in a special format as shows in the example below:

```
OjibweMorph/templates/root.lexc.j2:

{#
   This jinja2 template should be processed using a python script
   to generate root.lexc.
#}

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!                         !!
!!   Symbol declarations   !!
!!                         !!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Multichar_Symbols

%<ChCnj%> %<%<

! Flag diacritics for preverbs and prenouns
@U.Order.Cnj@
@U.Order.Ind@
@U.ChCnj.On@
@R.ChCnj.On@
@D.ChCnj@
@C.ChCnj@

! We sometimes end up with empty sub-lexicons. This can cause
! artificial ambiguity (and even epsilon loops) due to sequences of
! flag diacritics, which slows down analysis. Therefore, we mark empty
! entries with an <EMPTYLEX> tag and filter them out using a
! post-processing rule in phonology.xfst.
%<EMPTYLEX%>

! Add multichar symbols harvested from noun spreadsheets, verb
! spreadsheets, pronoun spreadsheets, etc.
{{ add_harvested_multichar_symbols() }}

LEXICON Root
AdverbRoot ;
NounRoot ;
NumeralRoot ;
ParticleRoot ;
PronounRoot ;
VerbRoot ;
VerbRootIrregular ;%                               
```

Here `{# ... #}` defines a Jinja comment and `{{ add_harvested_multichar_symbols() }}` represents a call to the python function `add_harvested_multichar_symbols()`. This sprecific function call adds all multi-character symbols found in spreadsheets and the lexical database into the `Multicharacter_Symbols` section of the `root.lexc` file. All template functions are found in `ParserTools/csv2fst/templates.py`.

Processing the template using the code in ParserTools, will create a `root.lexc` file. Most of the multi-character symbols below are lexical preverb and prenoun tags like `PNLex/aabitaa+`:

```
root.lexc:

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!                         !!
!!   Symbol declarations   !!
!!                         !!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Multichar_Symbols

%<ChCnj%> %<%<

! Flag diacritics for preverbs and prenouns
@U.Order.Cnj@
@U.Order.Ind@
@U.ChCnj.On@
@R.ChCnj.On@
@D.ChCnj@
@C.ChCnj@

! We sometimes end up with empty sub-lexicons. This can cause
! artificial ambiguity (and even epsilon loops) due to sequences of
! flag diacritics, which slows down analysis. Therefore, we mark empty
! entries with an <EMPTYLEX> tag and filter them out using a
! post-processing rule in phonology.xfst.
%<EMPTYLEX%>

! Add multichar symbols harvested from noun spreadsheets, verb
! spreadsheets, pronoun spreadsheets, etc.
%<%< %<T%> %>%> +%0PlObj +%0PlObvSubj +%0PlSubj +%0SgObj +%0SgObvSubj +%0SgSubj
+1SgObj +1SgPoss +1SgSubj +2PlObj +2PlPoss +2PlSubj +2SgObj +2SgPoss +2SgSubj
+3PlObvObj +3PlObvPoss +3PlObvSubj +3PlProxObj +3PlProxPoss +3PlProxSubj
+3SgObvObj +3SgObvPoss +3SgObvSubj +3SgProxObj +3SgProxPoss +3SgProxSubj
+ADVConj +ADVDisc +ADVDub +ADVGram +ADVInter +ADVLoc +ADVMan +ADVNeg +ADVPred
+ADVQnt +ADVTmp +AVDDeg +Cnj +Del +Dim +Dub +DubPrt +ExclObj +ExclPoss
+ExclSubj +Imp +InclObj +InclPoss +InclSubj +Ind +Loc +NA +NAD +NI +NID +NUM
+Neg +Neu +ObvPl +ObvSg +PCAsp +PCDisc +PCEmph +PCInterj +PRONDem +PRONDub
+PRONIndf +PRONInter +PRONPer +PRONPret +PRONPsl +PRONSim +Pej +Pl +Pos +Poss
+Prb +Pret +ProxPl +ProxSg +Prt +Sg +Sim +VAI +VAIO +VAIPL +VII +VIIPL +VTA
+VTI +Voc +XSubj @P.Paradigm.ADVConj@ @P.Paradigm.ADVDisc@ @P.Paradigm.ADVDub@
@P.Paradigm.ADVGram@ @P.Paradigm.ADVInter@ @P.Paradigm.ADVLoc@
@P.Paradigm.ADVMan@ @P.Paradigm.ADVNeg@ @P.Paradigm.ADVPred@
@P.Paradigm.ADVQnt@ @P.Paradigm.ADVTmp@ @P.Paradigm.AVDDeg@ @P.Paradigm.NA@
@P.Paradigm.NAD@ @P.Paradigm.NI@ @P.Paradigm.NID@ @P.Paradigm.NUM@
@P.Paradigm.PCAsp@ @P.Paradigm.PCDisc@ @P.Paradigm.PCEmph@
@P.Paradigm.PCInterj@ @P.Paradigm.PRONDem@ @P.Paradigm.PRONDub@
@P.Paradigm.PRONIndf@ @P.Paradigm.PRONInter@ @P.Paradigm.PRONPer@
@P.Paradigm.PRONPret@ @P.Paradigm.PRONPsl@ @P.Paradigm.PRONSim@
@P.Paradigm.VAI@ @P.Paradigm.VAIO@ @P.Paradigm.VAIPL@ @P.Paradigm.VII@
@P.Paradigm.VIIPL@ @P.Paradigm.VTA@ @P.Paradigm.VTI@ @P.Prefix.G@ @P.Prefix.GI@
@P.Prefix.GIDW@ @P.Prefix.N@ @P.Prefix.NI@ @P.Prefix.NONE@ @P.Prefix.O@
@P.Prefix.W@ @R.Paradigm.ADVConj@ @R.Paradigm.ADVDisc@ @R.Paradigm.ADVDub@
@R.Paradigm.ADVGram@ @R.Paradigm.ADVInter@ @R.Paradigm.ADVLoc@
@R.Paradigm.ADVMan@ @R.Paradigm.ADVNeg@ @R.Paradigm.ADVPred@
@R.Paradigm.ADVQnt@ @R.Paradigm.ADVTmp@ @R.Paradigm.AVDDeg@ @R.Paradigm.NA@
@R.Paradigm.NAD@ @R.Paradigm.NI@ @R.Paradigm.NID@ @R.Paradigm.NUM@
@R.Paradigm.PCAsp@ @R.Paradigm.PCDisc@ @R.Paradigm.PCEmph@
@R.Paradigm.PCInterj@ @R.Paradigm.PRONDem@ @R.Paradigm.PRONDub@
@R.Paradigm.PRONIndf@ @R.Paradigm.PRONInter@ @R.Paradigm.PRONPer@
@R.Paradigm.PRONPret@ @R.Paradigm.PRONPsl@ @R.Paradigm.PRONSim@
@R.Paradigm.VAI@ @R.Paradigm.VAIO@ @R.Paradigm.VAIPL@ @R.Paradigm.VII@
@R.Paradigm.VIIPL@ @R.Paradigm.VTA@ @R.Paradigm.VTI@ @R.Prefix.G@ @R.Prefix.GI@
@R.Prefix.GIDW@ @R.Prefix.N@ @R.Prefix.NI@ @R.Prefix.NONE@ @R.Prefix.O@
@R.Prefix.W@ @U.Order.Cnj@ @U.Order.Ind@ @U.Order.Other@ PNLex%/aabiji+
PNLex%/aabitaa+ PNLex%/aako+ PNLex%/aanji+ PNLex%/aazhawi+ PNLex%/agaami+
PNLex%/agaasi+ PNLex%/agiji+ PNLex%/anaami+ PNLex%/anama'e+ PNLex%/ando+
PNLex%/ashki+ PNLex%/asho+ PNLex%/awasi+ PNLex%/ayaangwaami+ PNLex%/azhe+
PNLex%/baashki+ PNLex%/baate+ PNLex%/bagaki+ PNLex%/bagami+ PNLex%/bagwaji+
PNLex%/bakobii+ PNLex%/besho+ PNLex%/bibine+ PNLex%/bichi+ PNLex%/bigii+
PNLex%/bigishki+ PNLex%/biichi+ PNLex%/biimasko+ PNLex%/biini+ PNLex%/biinji+
PNLex%/biisaawangi+ PNLex%/biisadaawangi+ PNLex%/biisi+ PNLex%/biitoo+
PNLex%/bizaani+ PNLex%/chi+ PNLex%/dago+ PNLex%/daki+ PNLex%/de+ PNLex%/desi+
PNLex%/dibi+ PNLex%/dibiki+ PNLex%/ditibi+ PNLex%/enda+ PNLex%/eyedawi+
PNLex%/eyiidawi+ PNLex%/gaagige+ PNLex%/gabe+ PNLex%/gagaanwaabiigi+
PNLex%/gagwe+ PNLex%/gakaki+ PNLex%/gashkii+ PNLex%/gete+ PNLex%/gichi+
PNLex%/gigizhebaa+ PNLex%/giimooji+ PNLex%/giiwe+ PNLex%/giiwitaa+
PNLex%/giiwitaawi+ PNLex%/giizhi+ PNLex%/gijigi+ PNLex%/gimooji+ PNLex%/ginibi+
PNLex%/ginwaako+ PNLex%/ginwaakojii+ PNLex%/goji+ PNLex%/goshko+
PNLex%/gwayako+ PNLex%/gwiinawi+ PNLex%/ishkwaa+ PNLex%/ishkwe+ PNLex%/ishpi+
PNLex%/jiigewe+ PNLex%/jiigi+ PNLex%/maajii+ PNLex%/maamawoo+ PNLex%/maazhi+
PNLex%/madwe+ PNLex%/maji+ PNLex%/makade+ PNLex%/mangi+ PNLex%/mayagi+
PNLex%/megwaa+ PNLex%/megwe+ PNLex%/michi+ PNLex%/miigwechiwi+ PNLex%/mino+
PNLex%/mishi+ PNLex%/misko+ PNLex%/naabe+ PNLex%/naawi+ PNLex%/nabagi+
PNLex%/nanda+ PNLex%/niibaa+ PNLex%/niigaani+ PNLex%/niiji+ PNLex%/niisi+
PNLex%/nisawi+ PNLex%/nishkaaji+ PNLex%/nitaa+ PNLex%/noonde+ PNLex%/noosooki+
PNLex%/noozhe+ PNLex%/ogiji+ PNLex%/ojaanimi+ PNLex%/oke+ PNLex%/oko+
PNLex%/ondami+ PNLex%/onzaami+ PNLex%/opime+ PNLex%/oshki+ PNLex%/ozaawi+
PNLex%/ozhaashi+ PNLex%/ozhaawashko+ PNLex%/waabani+ PNLex%/waabanoo+
PNLex%/waabi+ PNLex%/waabijii+ PNLex%/waabishki+ PNLex%/wagiji+ PNLex%/wake+
PNLex%/wani+ PNLex%/wenda+ PNLex%/wiiji+ PNLex%/wiimaa+ PNLex%/wiisagi+
PNLex%/wiishkobi+ PNLex%/zazegaa+ PNLex%/zhaawani+ PNLex%/zhiibaa+
PNLex%/zhiiwi+ PNLex%/ziiwiski+ PNQnt%/aabita+ PNQnt%/ashi-bezhigo+
PNQnt%/ashi-ingodwaaso+ PNQnt%/ashi-ishwaaso+ PNQnt%/ashi-naano+
PNQnt%/ashi-niiwo+ PNQnt%/ashi-niiyo+ PNQnt%/ashi-niizho+
PNQnt%/ashi-niizhwaaso+ PNQnt%/ashi-ningodwaaso+ PNQnt%/ashi-nishwaaso+
PNQnt%/ashi-niso+ PNQnt%/ashi-zhaangaso+ PNQnt%/bezhigo+ PNQnt%/ingo+
PNQnt%/ingodwaaso+ PNQnt%/ishwaaso+ PNQnt%/midaaso+ PNQnt%/naano+
PNQnt%/nenishwaaswi+ PNQnt%/niiwo+ PNQnt%/niiyo+ PNQnt%/niizho+
PNQnt%/niizhwaaso+ PNQnt%/ningo+ PNQnt%/ningodwaaso+ PNQnt%/nishwaaso+
PNQnt%/niso+ PNQnt%/zhaangaso+ PVDir%/ani+ PVDir%/awi+ PVDir%/baa+
PVDir%/babaa+ PVDir%/bi+ PVDir%/bibaa+ PVDir%/biiji+ PVDir%/bimi+ PVDir%/ni+
PVDir%/o+ PVDir%/ombi+ PVDir%/wi+ PVDir%/zaagiji+ PVLex%/aabiji+
PVLex%/aabitaa+ PVLex%/aako+ PVLex%/aanji+ PVLex%/aazhawi+ PVLex%/agaami+
PVLex%/agaasi+ PVLex%/agiji+ PVLex%/anaami+ PVLex%/anama'e+ PVLex%/ando+
PVLex%/ashki+ PVLex%/asho+ PVLex%/awasi+ PVLex%/ayaangwaami+ PVLex%/azhe+
PVLex%/baashki+ PVLex%/baate+ PVLex%/bagaki+ PVLex%/bagami+ PVLex%/bagwaji+
PVLex%/bakobii+ PVLex%/besho+ PVLex%/bibine+ PVLex%/bichi+ PVLex%/bigii+
PVLex%/bigishki+ PVLex%/biichi+ PVLex%/biimasko+ PVLex%/biini+ PVLex%/biinji+
PVLex%/biisaawangi+ PVLex%/biisadaawangi+ PVLex%/biisi+ PVLex%/biitoo+
PVLex%/bizaani+ PVLex%/chi+ PVLex%/dago+ PVLex%/daki+ PVLex%/de+ PVLex%/desi+
PVLex%/dibi+ PVLex%/dibiki+ PVLex%/ditibi+ PVLex%/enda+ PVLex%/eyedawi+
PVLex%/eyiidawi+ PVLex%/gaagige+ PVLex%/gabe+ PVLex%/gagaanwaabiigi+
PVLex%/gagwe+ PVLex%/gakaki+ PVLex%/gashkii+ PVLex%/gete+ PVLex%/gichi+
PVLex%/gigizhebaa+ PVLex%/giimooji+ PVLex%/giiwe+ PVLex%/giiwitaa+
PVLex%/giiwitaawi+ PVLex%/giizhi+ PVLex%/gijigi+ PVLex%/gimooji+ PVLex%/ginibi+
PVLex%/ginwaako+ PVLex%/ginwaakojii+ PVLex%/goji+ PVLex%/goshko+
PVLex%/gwayako+ PVLex%/gwiinawi+ PVLex%/ishkwaa+ PVLex%/ishkwe+ PVLex%/ishpi+
PVLex%/jiigewe+ PVLex%/jiigi+ PVLex%/maajii+ PVLex%/maamawoo+ PVLex%/maazhi+
PVLex%/madwe+ PVLex%/maji+ PVLex%/makade+ PVLex%/mangi+ PVLex%/mayagi+
PVLex%/megwaa+ PVLex%/megwe+ PVLex%/michi+ PVLex%/miigwechiwi+ PVLex%/mino+
PVLex%/mishi+ PVLex%/misko+ PVLex%/naabe+ PVLex%/naawi+ PVLex%/nabagi+
PVLex%/nanda+ PVLex%/niibaa+ PVLex%/niigaani+ PVLex%/niiji+ PVLex%/niisi+
PVLex%/nisawi+ PVLex%/nishkaaji+ PVLex%/nitaa+ PVLex%/noonde+ PVLex%/noosooki+
PVLex%/noozhe+ PVLex%/ogiji+ PVLex%/ojaanimi+ PVLex%/oke+ PVLex%/oko+
PVLex%/ondami+ PVLex%/onzaami+ PVLex%/opime+ PVLex%/oshki+ PVLex%/ozaawi+
PVLex%/ozhaashi+ PVLex%/ozhaawashko+ PVLex%/waabani+ PVLex%/waabanoo+
PVLex%/waabi+ PVLex%/waabijii+ PVLex%/waabishki+ PVLex%/wagiji+ PVLex%/wake+
PVLex%/wani+ PVLex%/wenda+ PVLex%/wiiji+ PVLex%/wiimaa+ PVLex%/wiisagi+
PVLex%/wiishkobi+ PVLex%/zazegaa+ PVLex%/zhaawani+ PVLex%/zhiibaa+
PVLex%/zhiiwi+ PVLex%/ziiwiski+ PVQnt%/aabita+ PVQnt%/ashi-bezhigo+
PVQnt%/ashi-ingodwaaso+ PVQnt%/ashi-ishwaaso+ PVQnt%/ashi-naano+
PVQnt%/ashi-niiwo+ PVQnt%/ashi-niiyo+ PVQnt%/ashi-niizho+
PVQnt%/ashi-niizhwaaso+ PVQnt%/ashi-ningodwaaso+ PVQnt%/ashi-nishwaaso+
PVQnt%/ashi-niso+ PVQnt%/ashi-zhaangaso+ PVQnt%/bezhigo+ PVQnt%/ingo+
PVQnt%/ingodwaaso+ PVQnt%/ishwaaso+ PVQnt%/midaaso+ PVQnt%/naano+
PVQnt%/nenishwaaswi+ PVQnt%/niiwo+ PVQnt%/niiyo+ PVQnt%/niizho+
PVQnt%/niizhwaaso+ PVQnt%/ningo+ PVQnt%/ningodwaaso+ PVQnt%/nishwaaso+
PVQnt%/niso+ PVQnt%/zhaangaso+ PVRel%/ako+ PVRel%/apiichi+ PVRel%/daso+
PVRel%/dazhi+ PVRel%/izhi+ PVRel%/onji+ PVSub%/a+ PVSub%/e+ PVSub%/gaa+
PVTense%/daa+ PVTense%/ga+ PVTense%/gii'+ PVTense%/gii+ PVTense%/wii'+
PVTense%/wii+ V1 a1 i1 i2 n1 s1 w1 w2 y1 y2

LEXICON Root
AdverbRoot ;
NounRoot ;
NumeralRoot ;
ParticleRoot ;
PronounRoot ;
VerbRoot ;
VerbRootIrregular ;
```

## Xfst phonological replace rules 

TBD
