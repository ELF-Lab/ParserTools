# [OPDDatabase](https://github.com/ELF-Lab/OPDDatabase/)

TBD 

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

## The `OPDDatabase/generate_data_for_parser_tools.py` script

### Special characters in OPD
