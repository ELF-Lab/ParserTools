# A CS-oriented introduction to Algonquian (though really just Ojibwe) morphology

## A bit of terminology

Morphological FST analyzers translate an input **word form** like *walked* into an **analysis** `walk+V+Past`. 

The word form *walked* can be split into two **morphemes**: 

* The **stem** *walk* and
* the **affix** *ed* (sometimes denoted as *-ed* to mark that it is bound to the stem).

The stem is the **unchanging** part of all inflected forms of *walk*, namely, *walk*, *walks*, *walking*, *walked*. The set of all inflected forms of *walk* is called the **lexeme** /walk/. The lexeme is denoted using one of the inflected forms of *walk* which is called the **base form** or **lemma** of the /walk/ lexeme. In the case of English verbs, this is the infinitive form.   

Inflectional affixes that occur before the stem are called **prefixes** and affixes that occur after the stem are called **suffixes**.

The morphological analysis `walk+V+Past` consists of the lemma `walk` and a number of **morphological features** like `+V` and `+Past` which here mark part of speech and tense, respectively.

Some word forms like *walks* are **ambiguous** in the sense that they correspond to more than one analysis. The form *walks* can be analyzed either as `walk+V+3Sg+Pres` (the 3rd singular present tense form of the verb walk) or `walk+N+Pl` (the plural form of the noun walk). This is called **morphological ambiguity**. An FST morphological analyzer should return all of the possible analyses given an input form like *walk*. 

## Word classes, paradigms and Inflection classes

Our Ojibwe FST can analyze word forms in the following **word classes**:
* averbs
* nouns
* numerals
* particles
* pronouns
* verbs

Of these classes only nouns and verbs are inflected, i.e. we see different realizations of the lexeme in different contexts. The other word classes are unchanging. 

We further split nouns into four **paradigms**:

* dependent animate nouns (NAD)
* depdendent inanimate nouns (NID)
* indepedendent animate nouns (NA)
* independent inanimate nouns (NI)

We further split verbs into the following paradigms:

*  VAI
*  VAIO
*  VAIPL (VAI verbs which only take plural subjects)
*  VII
*  VIIPL (VII verbs which only take plural subjects)
*  VTI
*  VTA

For each noun and verb paradigm, there may be a number of inflection classes. The inflection class determines the inflectional ending for a particular combination of morphological features like `+VTA+Cnj+Pos+Neu+3PlObvSubj+3SgProxObj`. For this analysis, VTA verbs in inflection class `VTA_aw` take the ending `god`, while verbs in all other VTA classes (`VTA_n`, `VTA_s`, `VTA_C` and `VTA_Cw`) take the ending `igod`. In our spreadsheets, each unique combination of paradigm, inflection class and morphological features corresponds to its own row. As stated, the inflectional class determines the shape of the inflectional ending (modulo some regular phonological alternations which are handled using xfst rules).  

## Ojibwe verbs

Ojibwe verb forms split into three segments:

1. Prefix
2. Stem
3. Suffix

The following example illustrates this division:

![Ojibwe verb](img/word.png)

### Verb prefix

The prefix can be empty or consist of several elements falling into two categories. The prefix starts with a **person prefix** which is followed by zero or more **preverbs**.

The person prefix denotes the subject of the verb. It is exclusively present in the independent order (see below) and only for the VAIO, VTI and VTA paradigms (see below). In the illustration above, the verb prefix contains the person prefix *ni* and a preverb *gii-*

Preverbs are separated from the stem (and other preverbs) by a hyphen `-`. In the verb analysis, they are marked by a preverb tag like *PVTense/gii+*. There are five types preverb markers:

1. `PVSub/xyz` & `ChCnj+` (subordinate preverb and changed conjunct marker)
2. `PVTense/xyz` (tense preverb)
3. `PVDir/xyz` (directional preverb)
4. `PVQnt/xyz` (quantifier preverb)
5. `PVLex/xyz` (lexical preverb)

Where `xyz` is the canonical form of the preverb followed by `+`, e.g. `PVTense/gii+`, `PVTense/ga+` and `PVSub/a+`. In the example above, we can see that the analysis contains the tag `PVTense/gii+` which in the word form is realized as the prefix `gii-`. The changed conjunct marker differs from the other preverbs in the sense that it is not realized as a prefix. Rather, it causes a *phonological alternation* in the first vowel of the verb form (this vowel can occur in another preverb or in the stem if the preverb is missing).  

Preverbs are mostly independent of other verb morphology, however, in certain cases they interact with other morphological features. Subordinate preverbs and the changed conjunct marker can only occur in conjunct forms. Additionally, tense preverbs often have a different surface realization in conjunct and independent forms. Furthermore, some preverbs do not follow the regular changed-conjunct rules and are instead realized in an idiosyncratic manner in changed-conjunct forms.  

### The verb stem and lexeme

The verb stem in the example above is `waabam`. It marks *nigii-waabamaabaniig* as an inflected form of the lexeme /waabam/. We can also see that the analysis contains the lemma `waabam`. Unlike tags, e.g. `+1SgSubj` which are represented as one symbol, the stem internally consists of individual characters: `w a a b a m`. This can be important when we write foma regular expressions to match verb forms.  

To match the analysis of the example form in the illustration, we can use one of the following foma regular expressions:

```
regex "PVTense/gii+" w a a b a m "+VTA" "+Ind+" "+Pos" "+Prt" "+1SgSubj" "+3PlProxObj"
regex "PVTense/gii+" {waabam} "+VTA" "+Ind+" "+Pos" "+Prt" "+1SgSubj" "+3PlProxObj"
```

The `"..."` syntax tells foma to treat the sequence as one symbol ignoring all special characters like `+`. The syntax `{...}` tells foma to split the sequence into individual utf-8 characters, once again ignoring all special characters.

### The verb suffix

The suffix encodes most of the inflectional information in the verb form. We have chosen to treat the verb suffix as a morpheme chunk like *aabaniig* in the example above. This chunk encodes information about the order, mode, polarity (positive vs. negative form), subject and object of the verb form. In reality, the chunk internally consists of several shorter suffixes with complex phonological dependencies. The dependencies could be modeled but this would unnecessarily complicate the rule-set of the FST so we don't do this. 

## Ojibwe nouns

TBD

## Other word classes (adverbs, pronouns, ...)

TBD

## Ambiguity in Ojibwe

Ambuiguity happens in two directions in Ojibwe. A word form can have multiple analyses:

```
foma[1]: up nimaajiibatoo
PVDir/ni+maajiibatoo+VAI+Ind+Pos+Neu+3SgProxSubj
maajiibatoo+VAI+Ind+Pos+Neu+1SgSubj
```
An analysis can also correspond to multiple inflected word forms:

```
foma[1]: down oyoosi+VAI+Ind+Pos+Dub+3SgProxSubj
oyoosidog
oyoosiwidog
```
The different inflected forms can belong to different dialects. Sometimes, there can be variation from one speaker to another and in some cases even in the speech of a single speaker. 
