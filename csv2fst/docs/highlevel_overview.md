## Overvivew of the compilation process

The FST analyzer is built using three source repositories:

* OjibweMorph houses morphological paradigms, skeleton lexc code and the xfst phonological rewrite rules (this repository either is already freely available or will short be made freely available for under a non-commerical license)
* OPDDatabase houses a lexical database from the Ojibwe People's Dictionary (this repository will not be made publicly available)
* ParserTools houses the code for compiling lexc files from the source data in OjibweMorph and OPDDatabase (this repository is publicly available and licensed under CC Deed)

We split the code into three different repositories mainly due to licensing issues. We want everyone to be able to use OjibweMorph and ParserTools together with their own lexical database for Ojibwe or a different Algonquian language.

<img src="img/flow_chart.png" align="center" width="500"/>

The spreadhsheets, configuration files and xfst rules in OjibweMorph can be used to compile a very minimal FST which can analyze and generate the forms for twenty odd Ojibwe model lexemes. For a full-scale morphological analyzer which can analyze most Ojibwe words in running text, we need to add a lexical database. We currently use OPDDatabase, but it would be possible to swap a different database in its place. For example, one which allows for commercial use.     

## [OjibweMorph](https://github.com/ELF-Lab/OjibweMorph/)

The following directories are included in the OjibweMorph repository:

| Directory | Description |
|-----------|-------------|
| `NounSpreadsheets` | Morphological paradigms for nouns (CSV spredsheets) | 
| `OtherSpreadsheets` | Morphological paradigms for uninflecting classes (CSV spreadsheets) |
| `PVSpreadsheets` | Preverbs spreadsheets (CSV spreadsheets) |
| `VerbSpreadsheets` | Morphological paradigms for verbs (CSV spreadsheets)
| `config` | Configuration files for compiling lexc files from spreadsheets for different word classes (json code) |
| `lexc` | Legacy lexc files (currently not used) |   
| `templates` | Jinja templates for lexc files (j2 files). Used by ParserTools during compilation. |
| `xfst` | Xfst phonological rewrite rules. Used by foma during compilation. |

### Morphological paradigm spreadsheets

We have spreadsheets both for nouns and verbs. Both follow this overall structure:

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

Additionally **Form1Source** can be used to indicate information about the given form, which elder it comes from, which dialect etc. Additional forms are given by specifying `Form2Surface`, `Form2Split`, `Form3Surface`, `Form3Split`, etc. When these forms are missing, the fields can be left empty.

Note that the stem and affixes can sometimes contain special charcters like `w1` in `o<<waabam>>igoniniw1`. These need to be listed in a configuration file as specified below. Otherwise, lexc won't know to compile them into multi-character symbols (Note to self: maybe introduce a special format instead so these can be identified automatically?).

Morphological features (here: **Order**, **Mode**, **Negation**, **Subject**, **Object**) can vary by paradigm (e.g. they are different for nouns and verbs) and the set is customizable using a configuation file.

Sometimes the value of a particular morphological feature is missing. For example, VII verbs don't take an object. In such cases, we can use a `NONE` value to indicate the missing field:

| Paradigm | Order | Class | Lemma | Stem | Subject | Object | Mode | Negation | Form1Surface | Form1Split | Form1Source | Form2Surface | Form2Split | Form2Source | 
|----------|-------|-------|-------|------|---------|--------|------|----------|--------------|------------|-------------|--------------|------------|-------------|
| `VII`    | `Ind` | `VII_VV` | `ate` | `ate` | `0PlObvSubj` | `NONE` | `Dub` | `Neg` | `atesininiwidogen` | `<<ate>>sininiwidogen` | `JDN-2010-MS-VII-p9` |

### Preverb (and prenoun) spreadsheets

### Configuration files

### Jinja lexc templates

### Xfst phonological replace rules 

## [OPDDatabase](https://github.com/ELF-Lab/OPDDatabase/)

## [ParserTools](https://github.com/ELF-Lab/ParserTools/)
