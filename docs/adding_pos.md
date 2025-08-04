# Illustrative Examples: Modifying the FST
Though the docs hopefully provide a detailed account of how all the different pieces come together to create the FST, it may still be a bit intimidating to try to put things together to create an FST for a particular language.  This section provides an account of how we added a new part-of-speech (POS), namely proper nouns, to our Ojibwe FST, thus listing all the components that have to be modified to support each POS you add.

Additionally, though we have tried to make FSTmorph flexible and covering a wide range of morphology, users creating an FST for a particular language may want to make some more serious changes to better represent the language at hand.  In order to assist with this process, we have also provided an account of adding a new *kind* of morpheme to the FST, namely enclitics.  This is more challenging than the addition of proper nouns because it is not just adding another kind of POS that behaves in basically the same way as many existing ones (nouns, verbs, etc.), but rather requires support for a whole new genre of morpheme (i.e., one that behaves something like a preverb, but can attach to *any* host word).
## Simpler: Adding Proper Nouns
The following outlines how to add support for a new POS to the FST, using the example of proper nouns being added to the Ojibwe FST.
1. Create a config file in the morphological source.
    - For example: create `proper_nouns.json` in `OjibweMorph/config/`.
    - You also need to make sure this config file is being given as a command-line argument to `csv2lexc.py`, but this was taken care of automatically by the `Makefile` in `OjibweMorph` which generates the list of config files based on the contents of `config/`.
    - Check out [the docs](morphological_source.md#configuration-files-json) for more info on what the config values mean.  Not all are necessary for basic functioning.
        - The following *must* be set and their values must be *correct*
            - `morphology_source_path`
            -`regular_csv_files`
            - `lexical_database`
            - `morph_features` (assuming you want the analysis to contain any info!)
        - The following *must* be set, but their value can really be anything -- just choose something specific to this POS:
            - `pos`
            - `root_lexicon`
            - `regular_lexc_file`
        - The following *must* be set, but you can just use the default/null value (described in the config docs):
            - `irregular_csv_files`
            - `irregular_lexc_file`
            - `missing_tag_marker`
            - `missing_form_marker`
            - `multichar_symbols`
            - `template_path`
2. Add the root name to the template for building `root.lexc`.
    - For example: add `ProperNounRoot` to the end of `OjibweMorph/templates/root.lexc.j2`.
3. Create a paradigm spreadsheet in the morphological source.
    - For example: create `PROPER_NOUN.csv` in one of the `OtherSpreadsheets/` folders in `OjibweMorph`.
    - There's more info in [the docs](morphological_source.md#morphological-paradigms-csv), but basically there are six mandatory columns for this spreadsheet: `Paradigm`, `Class`, `Lemma`, `Stem`, `Form1Surface`, and `Form1Split`.
    - There has to be at least one row for every possible paradigm and class value.
        - For example, there are two possibilities for proper nouns: paradigm and class being `PersonName`, or paradigm and class being `PlaceName`.  Therefore, there are two rows in `PROPER_NOUN.csv`.
4. Not required, but if you want the FST to handle more than a few cases, you'll need a spreadsheet in the lexical source.
    - For example: add `PROPER_NOUNS.csv` to `OjibweLexicon/OPD/`.
    - As outlined in [the docs](lexical_source.md), the six columns are mandatory (`Lemma`, `Stem`, `Paradigm`, `Class`, `Translation`, and `Source`), but only four require real values; `Translation` and `Source` can be `NONE`.

## Harder: Adding Enclitics
Adding enclitic support is more challenging because they are not standalone words -- we need to include new support for handling the way enclitics attach to other words (somewhat akin to preverbs).

The steps below recount the process for adding enclitic support, but not all the steps ultimately ended up being useful.  That is, we added enclitics in a way that tried to get a very simple, incomplete version *working* first, and from there we gradually made the necessary changes to get it to behave as desired.  This was done because trying to get all aspects of it working perfectly in one fell swoop would have likely been more difficult.  For example, we first add enclitics as *pre-elements*, even though ultimately they were meant to be *post-elements*, because there was already support for pre-elements, so it was easier to get them up and running this way.

The numbering mirrors the numbered steps used above for adding proper nouns, which was used as a kind of guide.

1. Config file: no config file needed!
    - They're not a standalone element, so they will get added to the config files of *other* POS, not get their own config file.
        - Using verbs as our example host, we should add info to `verbs.config` so it knows to expect them.
            - Actually, an easier thing would be to use a POS that doesn't already take a pre-element, like proper nouns.  That way we can just use the built-in pre-element support without worrying whether it can handle 2x pre-elements.
            - Can skip `pre_element_tag`! It's not used.
    - Without their own config file, we'll need to create a template to generate `enclitics.lexc` from: `enclitics.lexc.j2`
        - This can be very simple -- let's use the preadverbs one as a template.
        - For now, it is being treated as a "pre-element". We'll have to add support in `csv2lexc.py` for post-elements instead.
2. Adding to `root.lexc`: not necessary.
    - Enclitics are going to be add-ons, not the main part of any word, so they are never going to be the root (i.e., the *starting point* of a word).  The same goes for preverbs, prenouns, etc.
3. Creating a paradigm spreadsheet in the morphological source: created `OtherSpreadsheets/ENCLITICS.csv`
    - The six mandatory columns don't apply here... so what should this look like?
        - Based on PV spreadsheets, let's try just PV and Tag.
        - Nope, need `Independent,PlainConjunct,ChangedConjunct` also. Must be hardcoded somewhere. Let's add them for now.
4. Adding a spreadsheet to the lexical source: no need, though see the incorporation of `LEXICAL_PREVERBS.csv` etc. in OjibweLexicon if you did want to do this.

Yay! This achieved a very simple working example -- *sh-Waashtanong* now gets analyzed as `enCL/sh+Waashtanong+NamePlace`.

Next up: let's make it so *Waashtanong-sh* gets recognized!

5. This was accomplished just by changing the `.lexc` files, but this requires some understanding of how the `.lexc` files work! Basically, I had to "re-route" things so that the proper nouns lead to the enclitics, rather than the enclitics being an intermediate step between prefixes and the stem (as for preverbs etc.)
    - Rather than figuring out the inner workings of `csv2lexc.py` and template files, you can first make the changes to the generated `.lexc` files directly to confirm you know the right changes to accomplish your goal.  Just remember to recompile `all.lexc` and run `compile_fst.xfst` only *after* doing so, so that your `.lexc` edits are reflected in the FST (both these steps are found in the OjibweMorph makefile).
    - I edited `load_pre_element_csv` in `templates.py` to handle post_elements - specifically the template `.lexc.j2` file (when calling this function) can identify itself as a post-element and then the analysis tag will be written in the `.lexc` like +tag rather than tag+. (This change to `load_pre_element_csv` ended up being unnecessary after the rest of the changes in this section were made, so you won't see this intermediate step in the code.)

Next up: add support for other word types, not just proper nouns.
- Could either:
    - Add enclitics as post-elements to POS config files individually.
    - Make it so that clitics are a unique item class, that get automatically added to the `.lexc` files of *all* POS.
6. Gone with the latter option.
    - Hardcoded `enclitics.lexc.j2` into `templates.py` as a template that gets converted to a lexc file 1x, à la `root.lexc.j2`.  Just like for `root.lexc`, the generation of this file gets called from `csv2lexc.py` via `render_enclitic_lexicon`.
    - Then in `lexc_path.py`, all endings are set to Enclitic Root.  This ensures that all POS can have enclitics added to their end.  In part this involved adding a reference to `EncliticRoot` to `lexc_path.py`, which acts as a link to the generated `enclitics.lexc` content.

You can check out these changes in commit [d32a257906dbed1a65726ff8249212c6ef6252ac](https://github.com/ELF-Lab/FSTmorph/commit/d32a257906dbed1a65726ff8249212c6ef6252ac#diff-ae95ce97dce96a9751d98399f939489fafbae1091f2b0e0a2adcf62331916bd7).  Though many edits were made in the process of figuring out how to add these (as described above), in the end, not too many changes were needed to add support for enclitics.