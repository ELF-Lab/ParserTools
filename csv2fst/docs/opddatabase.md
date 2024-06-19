# [OPDDatabase](https://github.com/ELF-Lab/OPDDatabase/)

## Lexical database format

An example entry from our json OPD database:

```
{
    "url":"https:\/\/ojibwe.lib.umn.edu\/main-entry\/gwiinawaabam-vta",
    "lemma":"gwiinawaabam",
    "pos_type":"vta",
    "speaker":"es",
    "audio_link":"https:\/\/s3.amazonaws.com\/ojibwe-audio-transcoded\/gwiinawaabam__ta_ex__sp67049_0.mp4",
    "definition":"fail to see h\/, be unable to see h\/",
    "section_inflection_forms":[
        {
            "word":"ingwiinawaabamaa",
            "desc":"1s - 3s ind"
        },
        {
            "word":"ningwiinawaabamaa",
            "desc":"1s - 3s ind"
        },
        ...
       {
            "stem":"gwiinawaabam-"
       }
    ],
    "section_audio_forms":"",
    "section_additional_audio":"",
    "section_sentence_examples":[
        {
            "sent_oj":"Ogwiinawaabamaan aana-wii-anoonaad ji-nibinaadinid.",
            "sent_en":"He couldn't see him when he wanted him to go after water.",
            "speaker":"es",
            "audio_link":"https:\/\/s3.amazonaws.com\/ojibwe-audio-transcoded\/gwiinawaabam__ta_ex__sp67049_0.mp4"
        }
    ],
    "section_reduplication":"",
    "word_parts":{
        "plain_text":"gwiinawaabam \/gwiinawaabam-\/: \/gwiinaw-\/ lacking knowledge; \/-aabam\/ look at h\/",
        "word_parts":[{
            "word_part":"gwiinaw",
            "text":"lacking knowledge",
            "url":"https:\/\/ojibwe.lib.umn.edu\/word-part\/gwiinaw-initial"
        }
        ,{
            "word_part":"aabam",
            "text":"look at h\/",
            "url":"https:\/\/ojibwe.lib.umn.edu\/word-part\/aabam-final"
        }
    ]},
    "note":""}
```

For building the lexeme lists which can be incorporated into the FST, we currently use the following fields:

* `"lemma"`: Base form of the lexeme.
* `"pos_type"`: Paradigm i.e. word class + some extra information, e.g. `"vta"`, `"vti1"`, `"pron dem"`. This broadly corresponds to our paradigm labels like `VTA`, `VTI`, `PRONDem`.
* `"section_inflection_forms"`: A list of example inflected forms for this lexeme. These are used to classify noun lexemes into [inflection classes]("section_inflection_forms"). In addition to inflected forms, this list also contains the `"stem"` which is central for classifying verbs into their inflection classes.

## Paradigm maps

We broadly classify lexemes into similar paradigms as the OPD (VTA, VAI, NA, ADVDir, etc.), however, we need to classify lexems further into inflection classes which specify the endings that lexemes take when inflected. For example, VTAs in the `VTA_n` class take the ending `-igosiinaawaadogenan` when inflected in the Ind+Dub+Neg+0PlSubj+2PlObj form while VTAs in the `VAT_aw` class take the ending `-gosiinaawaadogenan`.

For verbs, the inflection class is completely determined by the baseform of the verb and its stem, while for nouns, we also need to examine the plural and sometimes the locative forms to determine the inflection class. In both cases, we can use a regular expression to match the end of the form. To classify the forms, we use special paradigm maps implemented as CSV files. We have one of these map files for each word class (nouns, verbs, pronouns, particles, adverbs and numerals). Each row in the paradigm map can be though of as a set of tests corresponding to the columns in the map file:

* `Paradigm`: The output paradigm of this row (e.g. `"VAI"`, `"PRONDem"`). This is the FST paradigm we'll assign to the lexeme if it passes all tests for this row. 
* `Class`: The output inflection class of this row (e.g. `"VAI_VV"`, `"PRONDem"`). This is the inflection class we'll assign to the lexeme if it passes all tests for this row.
* `OPDClass`: To pass all tests for this row, the OPD paradigm of the lexeme has to match this entry (e.g. `"vai"`, `"pron dem"`)
* `StemPattern`: To pass all tests for this row, the stem has to match this python regular expression (can be `"NONE"` is there is no stem test).
* `LemmaPattern`: To pass all tests for this row, the baseform has to match this python regular expression (can be `"NONE"` is there is no lemma test).
* `Tag1` (and `Tag2`, `Tag3`, ...): The OPD morphological features related to the regex in `Tag1Pattern` (can be `"NONE"` or missing if there is no test for inflected form test).  
* `Tag1Pattern` (and `Tag2Pattern`, `Tag3Pattern`, ...): The regex which needs to match the inflected form specified by `Tag1` (can be `"NONE"` or missing if there is no test for inflected form test).
  
For a given entry in our OPD database, we loop through the lines in the paradigm map **in order**. We find **the first row** where all tests pass and assign this lexeme the paradigm (`Paradigm`) and inflection class (`Class`) specified on that row. 

A few lines from `OPDDatabase/assets/VERBS_paradigm_map.csv`:

| Paradigm | Class | OPDClass | StemPattern | LemmaPattern | Tag1 | Tag1Pattern | Tag2 | Tag2Pattern |
|----------|-------|----------|-------------|--------------|------|-------------|------|-------------|
| `"VAI"` | `"VAI_rcp"` | `"vai"` | `"NONE"` | `"^.*diwag$"` |  |  |  |  |
| `"VAIPL"` | `"VAIPL_VV"` | `"vai"` | `"^.*(aa\|ii\|oo\|e)$"` | `"^.*wag$"` |  |  |  |  |
| `"VAIPL"` | `"VAIPL_V"` | `"vai"` | `"^.*[^iou][iou]$"` | `"^.*wag$"` |  |  |  |  |

A few lines from `OPDDatabase/assets/NOUNS_paradigm_map.csv`:

| Paradigm | Class | OPDClass | StemPattern | LemmaPattern | Tag1 | Tag1Pattern | Tag2 | Tag2Pattern |
|----------|-------|----------|-------------|--------------|------|-------------|------|-------------|
| `"NA"`  | `"NA_VVw"`  | `"na"`  | `"^.*(aa\|ii\|oo\|e)w$"`  | `"NONE"`  | `"pl"`  | `"^.*wag$"`  | `"loc"`  | `"NONE"`  |
| `"NI"`  | `"NI_aa"`  | `"ni"`  | `"^.*[bcdfghjklmnpstwyz']$"`  | `"NONE"`  | `"pl"`  | `"NONE"`  | `"loc"`  | `"^.*aang$"`  |


## The `OPDDatabase/generate_data_for_parser_tools.py` script

### Special characters in OPD
