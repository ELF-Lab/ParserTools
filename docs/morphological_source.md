# The Morphological Source
The morphological source provides information about the morphology of the target language needed to create the FST.  The illustrative example of this source is [OjibweMorph](https://github.com/ELF-Lab/OjibweMorph).

The morphological source includes four key components used to build the FST.  The remainder of this document outlines the purpose and requirements of each of these components:
- [morphological info files (`.csv`)](#morphological-paradigms-csv)
- [config files (`.json`)](#configuration-files-json)
- [template files (`.lexc.j2`)](#templates-lexcj2)
- [phonological rule files (`.xfst`)](#phonological-rules-xfst)

## Morphological paradigms (`.csv`)
These spreadsheets provide the core morphological information used by the FST.

The spreadsheets are used by `csv2lexc.py`.  It gets the location/name of the spreadsheets from the config files.  Each config file specifies the relevant spreadsheets for its POS through the values of `morphology_source_path`, `regular_csv_files` and (optionally) `irregular_csv_files`.

Words should be split into different spreadsheets by **part of speech (POS)** (e.g., ADVERBS.csv).  Further splitting works, too.  For example, in `OjibweMorph`, the noun and verb spreadsheets (which have many, many more forms than the other POS) are further split by **class** for nouns (e.g., NA_VVw.csv) and by **paradigm** and **order** for verbs (e.g., VTI_CNJ.csv).

Though these spreadsheets are primarily used for their morphological inflection, while the external lexical database provides most lemmas, the FST *does* also learn the lemmas given in these spreadsheets.  This is why you can make a small working FST with no external lexical database specified -- the FST will just know the lemmas used in these morphological spreadsheets.

The organization of word forms into **paradigms** and **classes** in the `.lexc` files comes from the specifications in these files (?).

Here is a small extract from `VTA_IND.csv`:
| Paradigm | Order | Class | Lemma | Stem | Subject | Object | Mode | Negation | Form1Surface | Form1Split | Form1Source | Form2Surface | Form2Split | Form2Source | 
|----------|-------|-------|-------|------|---------|--------|------|----------|--------------|------------|-------------|--------------|------------|-------------|
| `VTA` | `Ind` | `VTA_C` | `waabam` | `waabam` | `0PlSubj` | `3SgObvObj` | `Neu`  | `Pos` | `owaabamigonan` | `o<<waabam>>igonan` | `NJ-ngs-2023-Aug19` | `owaabamigonini` | `o<<waabam>>igoniniw1` | `JRV-Web-ANISH` |
| `VTA` | `Ind` | `VTA_Cw` | `mizho` | `mizhw1` | `0PlSubj` | `3SgObvObj` | `Neu` | `Pos` | `omizhogonan` | `o<<mizho>>igonan` | `NJ-ngs-2023-Aug19` |  | |  |	

Each row in the spreadsheet corresponds to a specific combination of lemma and morphological features.  In other words, there is *at least* one inflected form per row -- and often more than one, in cases with multiple possible surface forms. For example, the first row above specifies the inflected forms *owaabamigonan* and *owaabamigonini*, both corresponding to the analysis `waabam+VAT+Ind+Pos+Neu+0PlSubj+3SgObvObj`.

Six of the columns are obligatory:
* **Paradigm** gives the general category of the form (e.g.,`NA`, `NAD`, `NI`, `NID` for Ojibwe nouns; `VAI`, `VII`, `VTA`, `VTI` for Ojibwe verbs; others include `ADVConj`, `PRONDem`, `NUM`, `PCInterj`).
* **Class** gives the inflectional class of the form.
    - E.g., the class `VTA_C` represents `VTA` verbs where the stem ends in a consonant (like *waabam*), whereas the class `VTA_Cw` represents `VTA` verbs ending in a consonant followed by *w* (like *mizhw*).
- **Lemma** gives the 'dictionary form'; an easily-recognizable, 'base' form that is an actual, useable word.
- **Stem** givesthe base which undergoes morphology to create inflected forms.  Often identical to the lemma, but needn't be.  May be more of a word 'part' than a useable word.
* **Form1Surface** gives the inflected word form itself.
* **Form1Split** gives a split of the form into `prefix<<stem>>suffix`.
    - Note that the `stem` here doesn't need to correspond to the **Stem** column because the stem might vary due to phonolgical factors based on the prefix and suffix (this is the case for the inflected form *omizhogonan*, where the default stem *mizhw* is realized as *mizho* in this specific form). The`xfst` replace rules transform the stem given in the **Stem** column into its various realizations.
    - Note that the stem and affixes can sometimes contain special characters like *w1* in `o<<waabam>>igoniniw1`. These need to be listed in a configuration file as specified [below](#configuration-files-json). Otherwise, `lexc` won't know to compile them into multi-character symbols.

Additional columns are optional:
- **Form1Source** can give information about the given form (e.g., which elder it comes from, which dialect, etc.).
- **Form2Surface**, **Form2Split**, **Form3Surface**, **Form3Split**, etc. can give additional forms. When there are no additional forms, the fields can be left empty.

Finally, columns specificying morphological features (e.g., **Order**, **Mode**, **Negation**, **Subject**, and **Object**) can vary by paradigm (e.g., they are different for nouns and verbs).  The set of these columns being used in a given spreadsheet should be specified in the corresponding config file, as specified [below](#configuration-files-json).

Sometimes the value of a particular morphological feature is missing. For example, VII verbs don't take an object. In such cases, we can use a `NONE` value to indicate the missing field.  For example:

| Paradigm | Order | Class | Lemma | Stem | Subject | Object | Mode | Negation | Form1Surface | Form1Split | Form1Source | Form2Surface | Form2Split | Form2Source | 
|----------|-------|-------|-------|------|---------|--------|------|----------|--------------|------------|-------------|--------------|------------|-------------|
| `VII`    | `Ind` | `VII_VV` | `ate` | `ate` | `0PlObvSubj` | `NONE` | `Dub` | `Neg` | `atesininiwidogen` | `<<ate>>sininiwidogen` | `JDN-2010-MS-VII-p9` |

The spreadsheets can include other columns as well. For example, **Notes** could be a useful one in some cases.

### Preverb (and prenoun) spreadsheets
These spreadsheets, though similar in spirit to the general morphological ones described above, differ in usage and format.

The preverb spreadsheets are further split up by category: dir(ectional), lex(ical), qnt (quantitative), rel(ative), sub(ordinator), tns (tense/modal).
The same five columns are used in all PV spreadsheets.  Here are some example rows from `PV_dir.csv`:

| PV | Tag | Independent | PlainConjunct | ChangedConjunct | 
|-|-|-|-|-|
| ni | PVDir | ni | ni | eni |
| o | PVDir | o | o | NONE |

These five columns are mandatory across all preverb spreadsheets:
- **PV** (preverb) gives the form itself.
- **Tag** gives a category of preverbs, similar to **Paradigm** or **Class** used in the regular spreadsheets.  It corresponds to the way the preverbs are split into spreadsheets, so each spreadsheet should have only one value used in this column (e.g., `PV_dir.csv` has only `PVDir`).
- The remaining three columns relate to the nature of the verb being attached to (largely, its **Order** value).  Basically these capture allomorphy in the preverb's form based on the verb -- more details [here](https://github.com/ELF-Lab/OjibweMorph/PVSpreadsheets).
    - **Independent** gives the preverb's form with Independent verbs (essentially the default).
    - **PlainConjunct** gives the preverb's form with Conjunct form verbs (can be the same as the form in the **Independent** column).
    - **ChangedConjunct** gives the preverb's form with Changed Conjunct form verbs (often `NONE`).

<mark>More info to be added. Ultimately something should be said about how to make something similar for other languages, as this is quite Ojibwe-specific.</mark>

## Configuration files (`.json`)
Configuration files are used by `csv2lexc.py` to control the compilation of `lexc` files for a particular word class (nouns, verbs, pronouns, etc.). The configuration file contains all of the central information related to compilation: which spreadsheets to use as source, what the morphological features are, whether to include prenouns/preverbs, etc.

A `lexc` file will be generated for each config file.  An additional, irregular `lexc` can also be generated.  For example, `verbs.json` leads to `ojibwe_verbs.lexc` and `ojibwe_irregular_verbs.lexc`.


Below, you can see a description of all the features.  The example values come from [OjibweMorph/config/verbs.json](https://github.com/ELF-Lab/OjibweMorph/config/verbs.json).

| Feature | Description | Example Value | Notes |
|---------|-------------|-------|-------|
| `"pos"` | Word class  | `"Verb"`, `"Noun"`, ... | This determines the name of `XStems` in the relevant `.lexc` files (e.g., if this is `Verb`, you will get `VerbStems`).  <mark>If you make this some nonsense, the FST compiles but doesn't work for the relevant POS.  So this is important, I'm just not sure *exactly* what that `XStems` piece has to be the same as. Update: I found proper nouns still work if you change their value to nonsense (whereas verbs didn't). So maybe it was just about matching `VerbStems` in preverbs.lexc.j2?</mark>|
| `"root_lexicon"` | Root lexicon name | `"VerbRoot"`, `"NounRoot"`, ...| Word class specific root lexicon. This could be automatically deduced.  Also appears (for all POS) in `templates/root.lexc.js`. |
| `"morphology_source_path"` | Path to directory containing paradigm spreadsheets for this word class | `"./VerbSpreadsheets/"` | Since the names of the relevant files in this dir is given in the next value, there *can* be other files in this directory. Note this directory is expected to be within the **morphology source directory** (e.g., OjibweMorph) which is provided as a command-line argument to `csv2lexc.py` (and this path should be relative to that dir). |
| `"regular_csv_files"` | List of spreadsheets to include when compiling **regular** lexemes | `["VTA_IND", "VTI_CNJ", ... ]` | Spreadsheets listed here will undergo regular phonological rules.  <br>Give this value as a list even if it only contains one element (i.e., one spreadsheet).  Please omit the `.csv` suffix. |
| `"irregular_csv_files"` | List of spreadsheets to include when compiling **irregular** lexemes | `[]` | Spreadsheets listed here will not undergo any phonological rules. This category is meant for lexemes which do not belong to a larger inflection class, and where we simply list every single inflected form in verbatim.  <br>This functionality is not currently used in generating the Ojibwe FST.  <br>Please omit the `.csv` suffix. |
| `"lexical_database"` | Path to lexical database | `VERBS.csv` | Note this directory is expected to be within a **external lexical source** (e.g., `OjibweLexicon/OPD`) which is provided as a command-line argument to `csv2lexc.py` (and this path should be relative to that dir). |
| `"lexical_prefix_database"` | Path to preverb/prenoun database | `"LEXICAL_PREVERBS.csv"` | Note this directory is expected to be within a **external lexical source** (e.g., `OjibweLexicon/OPD`) which is provided as a command-line argument to `csv2lexc.py` (and this path should be relative to that dir).  <mark>This value is straight up missing from some .jsons -- should maybe be present and just NONE?</mark> |
| `"regular_lexc_file"` | File where compiled `.lexc` code for *regular* paradigms will be stored | `"ojibwe_verbs.lexc"` | Note that an output directory, where all `.lexc` code is stored (among other generated files), is given as a command-line argument to `csv2lexc.py`. |
| `"irregular_lexc_file"` | File where compiled `.lexc` code for *irregular* paradigms will be stored | `"ojibwe_irregular_verbs.lexc"` | Note that an output directory, where all `.lexc` code is stored (among other generated files), is given as a command-line argument to `csv2lexc.py`. Can be `None`.  If specified but there are no irregular forms, an (almost-) empty file will still be generated. |
| `"morph_features"` | List specifying the columns in the paradigm spreadsheets to be used as morphological features | `[ "Paradigm", "Order", "Negation",  ... ]` | This list determines both which columns to use from a spreadsheet like `VTA_IND.csv` and the order in which the features appear in the analysis (e.g., `VTA+Ind+Pos...`).  This list is also used by `tests/create_yaml.py` to generate analyses of the same format to be tested against.  Because this list specifies which columns to use, you can have additional, unused columns in the spreadsheet with no effect. |
| `"missing_tag_marker"` | Symbol used to mark tags which are 'missing' in the paradigm spreadsheets | `"NONE"` | For example, VII verbs do not have grammatical objects, so they do not have a meaningful value to go in the `Object` column in the spreadsheets.  Setting this value to `NONE` in the config tells us that this lack-of-value will be indicated in the spreadsheets with `NONE` (but it could just as easily be `any_word_you_want`) |
| `"missing_form_marker"` | Symbol used to mark morphological gaps, where an analysis has no surface realizations | `"MISSING"` | This marks cases where there's nothing to put for the form -- maybe we know the form doesn't exist, or aren't sure if it exists, or just don't know what it looks like. For example, this happens with dubitative preterite forms in Ojibwe, which currently are poorly documented and understood. In other cases, we know that the surface realization is impossible due to a logical contradiction. |
| `"multichar_symbols"` | List of multi-character symbols (i.e., mu.tiple characters that should be parsed as a single unit) | `["i1", "s1", "n1", ...]` | Rules often reference special multi-character symbols like `"w1"`. These are included in spreadsheets (sometimes also the lexical database) and need to be declared so that they can be added to the `.lexc` `Multichar_Symbols` section. |
| `"pre_element_tag"` | | `"[PREVERB]"` | Can be set to "". <mark> Not sure this is being used anywhere? But also not sure any PV forms are passing, so hard to assess.</mark>|
| `"prefix_root"` | Custom root lexicon for preverbs/prenouns/whatever is specified by `pre_element_tag` | `"PreverbRoot"` | <mark>Can be omitted. Presumably must match with the root val specified in the pre-element's `.lexc.j2` file (but doesn't go in `root.lexc.j2`).</mark> |
| `"template_path"` | Path to jinja lexc template file (`./lexc.2`) for preverbs/prenouns/whatever is specified by `pre_element_tag` | `"./templates/preverbs.lexc.j2"` | Note this directory is expected to be within the **morphology source directory** (e.g., OjibweMorph) which is provided as a command-line argument to `csv2lexc.py` (and this path should be relative to that dir). Can be omitted.  Note that (for some reason) this path cannot include a tilde symbol.  <mark>These all need to be renamed to use the same keyword for prefix/pv/preelement.</mark> |
| `"pv_source_path"` | Path to preverb/prenoun spreadsheets | `"./PVSpreadsheets"` | Note this directory is expected to be within the **morphology source directory** (e.g., OjibweMorph) which is provided as a command-line argument to `csv2lexc.py` (and this path should be relative to that dir). Can be `None`. |
| `"derivational_csv_file"` | Path to the derivational morphology CSV | `"./DerivationalSpreadsheets/DerivationalMorphology.csv"` | Note this directory is expected to be within the **morphology source directory** (e.g., OjibweMorph) which is provided as a command-line argument to `csv2lexc.py` (and this path should be relative to that dir).  Can be omitted. |

## Templates (`.lexc.j2`)
Compiling the FST involves generating many `.lexc` files.  The simplest of these can be generated directly from [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) templates files (`.lexc.j2`). 

For example, the Ojibwe FST generates many `.lexc` files: one for each part of speech (e.g., `ojibwe_nouns.lexc`), one for each pre-element (e.g., `prenouns.lexc`), `root.lexc`, and `all.lexc`.  The simplest of these files (namely the pre-element ones and `root.lexc`) are compiled from templates found in [the templates folder](https://github.com/ELF-Lab/OjibweMorph/templates) in OjibweMorph. These very closely resemble `.lexc` code but also contain python function calls, which dynamically generate required content, in a special format as shown in the example below (`OjibweMorph/templates/root.lexc.j2`):

```
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
ProperNounRoot ;
VerbRoot ;
VerbRootIrregular ;                              
```

In the above example, `{# ... #}` defines a Jinja comment and `{{ add_harvested_multichar_symbols() }}` represents a call to the python function `add_harvested_multichar_symbols()`. This specific function call adds all multi-character symbols found in spreadsheets and the lexical database into the `Multicharacter_Symbols` section of the `root.lexc` file. All template functions are found in `FSTmorph/src/templates.py`.

Processing this template file using the code in FSTmorph will create a `root.lexc` file, shown below (abbreviated in parts with `...`).  Most of the multi-character symbols (in addition to things like `V1`, `a1`, etc.) are lexical preverb and prenoun tags like `PNLex/aabitaa+`:

```


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
%<%< %<T%> %>%> +%0PlHead +%0PlObj +%0PlObvHead +%0PlObvSubj +%0PlSubj
+%0SgHead +%0SgObj +%0SgObvHead +%0SgObvSubj +%0SgSubj +1SgObj +1SgPoss
+1SgSubj +2PlObj +2PlPoss +2PlSubj +2SgObj +2SgPoss +2SgSubj +3PlObvHead
+3PlObvObj +3PlObvPoss +3PlObvSubj +3PlProx +3PlProxHead +3PlProxObj
+3PlProxPoss +3PlProxSubj +3SgObvHead +3SgObvObj +3SgObvPoss +3SgObvSubj
+3SgProx +3SgProxHead +3SgProxObj +3SgProxPoss +3SgProxSubj +ADVConj +ADVDeg
+ADVDisc +ADVDub +ADVGram +ADVInter +ADVLoc +ADVMan +ADVNeg +ADVPred +ADVQnt
+ADVTmp +Alt +Aug/magad +Cnj +Del +Der/magad +Dim +Dub +DubPrt +ExclObj
+ExclPoss +ExclSubj +Imp +InclObj +InclPoss +InclSubj +Ind +Loc +LocDist +NA
+NAD +NI +NID +NUM +NamePerson +NamePlace +Neg +Neu +ObvPl +ObvSg +PCAsp
+PCDisc +PCEmph +PCInterj +PRONDem+NA+ObvPl +PRONDem+NA+ObvSg
+PRONDem+NA+ProxPl +PRONDem+NA+ProxSg +PRONDem+NI+Pl +PRONDem+NI+Sg
+PRONDub+NA+ObvPl +PRONDub+NA+ObvSg +PRONDub+NA+ProxPl +PRONDub+NA+ProxSg
+PRONDub+NI+Pl +PRONDub+NI+Sg +PRONIndf+NA +PRONIndf+NA+ProxPl +PRONIndf+NI
+PRONInter+NA +PRONInter+NA+ObvPl +PRONInter+NA+ObvSg +PRONInter+NA+ProxPl
+PRONInter+NA+ProxSg +PRONInter+NI+Pl +PRONInter+NI+Sg +PRONPer+NA+1Sg
+PRONPer+NA+2Pl +PRONPer+NA+2Sg +PRONPer+NA+3Pl +PRONPer+NA+3Sg
+PRONPer+NA+Excl +PRONPer+NA+Incl +PRONPret+NA +PRONSim+NA+ObvPl
+PRONSim+NA+ObvSg +PRONSim+NA+ProxPl +PRONSim+NA+ProxSg +PRONSim+NI+Pl
+PRONSim+NI+Sg +Pcp +Pej +Pl +Pos +Poss +Prb +Pret +ProxPl +ProxSg +Prt
+Recip/di +Reflex/dizo +Sg +Sim +VAI +VAIO +VAIPL +VII +VIIPL +VTA +VTI +Voc
+XObj +XSubj @P.Paradigm.ADVConj@ @P.Paradigm.ADVDeg@ @P.Paradigm.ADVDisc@
@P.Paradigm.ADVDub@ @P.Paradigm.ADVGram@ @P.Paradigm.ADVInter@
@P.Paradigm.ADVLoc@ @P.Paradigm.ADVMan@ @P.Paradigm.ADVNeg@
...
@R.Paradigm.PRONSim+NA+ObvSg@ @R.Paradigm.PRONSim+NA+ProxPl@
@R.Paradigm.PRONSim+NA+ProxSg@ @R.Paradigm.PRONSim+NI+Pl@
@R.Paradigm.PRONSim+NI+Sg@ @R.Paradigm.VAI@ @R.Paradigm.VAIO@
@R.Paradigm.VAIPL@ @R.Paradigm.VII@ @R.Paradigm.VIIPL@ @R.Paradigm.VTA@
@R.Paradigm.VTI@ @R.Prefix.%<CHCNJ%>@ @R.Prefix.G@ @R.Prefix.GI@
@R.Prefix.GIDW@ @R.Prefix.N@ @R.Prefix.NI@ @R.Prefix.NONE@ @R.Prefix.O@
@R.Prefix.W@ @U.Order.Cnj@ @U.Order.Ind@ @U.Order.Other@ PNLex%/aabiji+
PNLex%/aabitaa+ PNLex%/aako+ PNLex%/aanji+ PNLex%/aazhawi+ PNLex%/agaami+
PNLex%/agaasi+ PNLex%/agiji+ PNLex%/anaami+ PNLex%/anama'e+ PNLex%/ando+
PNLex%/ashki+ PNLex%/asho+ PNLex%/awasi+ PNLex%/ayaangwaami+ PNLex%/azhe+
PNLex%/baashki+ PNLex%/baate+ PNLex%/bagaki+ PNLex%/bagami+ PNLex%/bagwaji+
PNLex%/bakobii+ PNLex%/besho+ PNLex%/bibine+ PNLex%/bichi+ PNLex%/bigii+
...
PVQnt%/niizhwaaso+ PVQnt%/ningo+ PVQnt%/ningodwaaso+ PVQnt%/nishwaaso+
PVQnt%/niso+ PVQnt%/zhaangaso+ PVRel%/ako+ PVRel%/apiichi+ PVRel%/daso+
PVRel%/dazhi+ PVRel%/izhi+ PVRel%/onji+ PVSub%/a+ PVSub%/e+ PVSub%/gaa+
PVTense%/aana+ PVTense%/aano+ PVTense%/daa+ PVTense%/ga+ PVTense%/gii'+
PVTense%/gii+ PVTense%/jibwaa+ PVTense%/wii'+ PVTense%/wii+ V1 a1 i1 i2 n1 s1
w1 w2 y1 y2

LEXICON Root
AdverbRoot ;
NounRoot ;
NumeralRoot ;
ParticleRoot ;
PronounRoot ;
ProperNounRoot ;
VerbRoot ;
VerbRootIrregular ;

```

These template files are used by `csv2lexc.py` in generating `.lexc` files.  For the pre-element templates, their filepath is given by the relevant config file (e.g., `config/verbs.json` has `template_path` set to `"./templates/preverbs.lexc.j2"`).  Meanwhile, the root template file is expected by `csv2lexc.py` to be found within the given morphological source dir, as `templates/root.lexc.j2`.

## Phonological Rules (`.xfst`)
`phonology.xfst` includes the phonological rules that will be incorporated into the FST to produce inflected forms.

Specifically, `FSTmorph/assets/compile_fst.xfst` ultimately creates the actual FST files from the combination of `all.lexc` (one of the generated `.lexc` files) and `phonology.xfst`.  Both of these are hardcoded into `compile_fst.xfst`.  In `OjibweMorph`, the [Makefile](https://github.com/ELF-Lab/OjibweMorph/Makefile) copies both `.xfst` files into the output directory along with all the generated `.lexc` files, so that all these files are in the same place. `compile_fst.xfst` is a language-general way of combining these two files containing language-specific information.

Here is an example phonological rule from [OjibweMorph/xfst/phonology.xfst](https://github.com/ELF-Lab/OjibweMorph/xfst/phonology.xfst):
```
! d-deletion: Delete stem-final "d" 
! 	when the suffix complex starts with a consonant.
define dDeletion d -> 0 || _ SUFBD Cons ;
```

The first two lines are comments, marked with the initial `!`.  The rule (named `dDeletion`) says to delete the character d (`d -> 0`) in contexts where (`||`) the d (`_`) is followed by a suffix boundary (`SUFBD`; this is defined earlier in the file) and then a consonant (`Cons`; this is defined earlier in the file).

Here is one more example rule:
```
! glottaloMetathesis: -ii'o becomes -iiw' at the end of a word.
! VAI stems with ending in -ii'o show a variant where rather than deleting the short o word-finally, it gets turned to a w and metathesized to iiw'
! Probably a rule specific to GJ or Lac La Croix more generally.
define glottaloMetathesis ' o (->) w ' || i i _ SUFBD ;
```

Again there are several lines of comments.  The rule (named `glottaloMetathesis`) says to *optionally* replace 'o with w' (`' o (->) w ' `) in contexts where (`||`) the 'o is preceded by two i's (`i i _`) and is the last character in the stem (`_ SUFBD`).  This rule differs from the previous example in that it is optional (indicated by the arrow being in parentheses), meaning that it will just generate a variant rather than outright replacing the original form.

<mark>More info needed about the specifics of what this file should look like -- asking Miikka!</mark>