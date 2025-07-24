# The Lexical Source

The lexical source CSVs provide lists of **lexemes** to the FST which will then be included in its knowledge.  While other sources tell the FST how to inflect various lexemes, phonological rules that are involved, etc. the lexical source CSVs are like big wordlists that the FST will then apply that other knowledge to.  In other words, these CSVs are not *essential* for building an FST -- you can generate a minimal FST with only the materials in the [morphological source](./morphological_source.md) -- but they greatly expand its vocabulary, and thus, its utility!

The lexical source(s) for the example Ojibwe FST are subfolders in `OjibweLexicon`.  For example [`OjibweLexicon/OPD`](https://github.com/ELF-Lab/OjibweLexicon/tree/main/OPD)..

The lexical source CSVs should be split up by part of speech, yielding `VERBS.csv`, `NOUNS.csv`, etc.  Each CSV has the following columns:
- **Lemma**: the 'dictionary form'; an easily-recognizable, 'base' form that is an actual, useable word.
- **Stem**: the base which undergoes morphology to create inflected forms.  Often identical to the lemma, but needn't be.  May be more of a word 'part' than a useable word.
- **Paradigm**: the paradigm category which this lexeme belongs to.
- **Class**: the class category which this lexeme belongs to.  In simpler cases (without such elaborate classification schemes), this can be the same as the paradigm (e.g., in [`PARTICLES.csv`](https://github.com/ELF-Lab/OjibweLexicon/blob/main/OPD/PARTICLES.csv))
- **Translation**: the lexeme's meaning in English; not used by the FST and so can be `NONE`.
- **Source**: some form of attribution indicating where this entry comes from; not used by the FST and so can be `NONE`.

As an example, here is a small excerpt from [`OjibweLexicon/OPD/NOUNS.csv`](https://github.com/ELF-Lab/OjibweLexicon/blob/main/OPD/NOUNS.csv):

```
Lemma,Stem,Paradigm,Class,Translation,Source
waasigani-gizhaabikiziganens,waasigani-gizhaabikiziganens,NI,NI_C,NONE,https://ojibwe.lib.umn.edu/main-entry/waasigani-gizhaabikiziganens-ni
waasigani-biiwaabik,waasigani-biiwaabikw2,NI,NI_Cw,NONE,https://ojibwe.lib.umn.edu/main-entry/waasigani-biiwaabik-ni
```
<br>

The **lemma** is essentially the best identifier for a lexeme for speakers.  It is not used internally by the FST, but *is* used in the FST outputs: it is the form that appears in analysis outputs, in the tag set.  For example, if you ask the FST for an analysis of *waasigani-biiwaabikoon*, you get `waasigani-biiwaabik+NI+Pl`, which uses the **lemma** given in the example above (in the last row).

The **stem**, on the other hand, is very important for the FST's processes, because this is the 'base form' it uses to make sense of inflected form inputs and create inflected word outputs.

The **paradigm/class** information is used to categorize the lexeme, with different categories getting different inflection.

Multiple *sets* of lexical source CSVs can be supplied to FST generation -- they will simply be merged together as if they were a single set of longer CSVs.  For example, the example Ojibwe FST gets fed a set of CSVs (`NOUNS.csv`, `VERBS.csv`, etc.) from `OjibweLexicon/OPD`, as well as a set from `OjibweLexicon/HammerlyFieldwork`.

If the same lexemes are included in the lexical source CSVs and the [morphological source](./morphological_source.md) CSVs, the lemmas/stems should agree.

The lexical source files are used by `csv2lexc.py` in creating the FST.  Its `database-paths` command-line argument expects a directory path (or a list of directory paths, separated by commas).  Inside this directory, the CSVs should be found.  The specific CSVs to use are specified (via `lexical_database`) in the corresponding [config files (`.json`)](./morphological_source.md#configuration-files-json) in the morphological source.  For example, if `database-paths` is set to `OjibweLexicon/OPD`, and `verbs.json` has `"lexical_database": "VERBS.csv",`, then it will read verb lemmas from `OjibweLexicon/OPD/VERBS.csv`.
