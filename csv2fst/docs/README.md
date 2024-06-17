# A CS oriented introduction to Algonquian (though really just Ojibwe) morphology

## A bit of terminology

Morphological FST analyzers translate an input **word form** like *walked* into an **analysis** like `walk+V+Past`. 

The word form *walked* can be split into two **morphemes**: 

* The **stem** *walk* and
* the **affix** *ed* (sometimes denoted as *-ed* to mark that it is bound to the stem).

The stem is the **unchanging** part of all inflected forms of *walk*, namely, *walk*, *walks*, *walking*, *walked*. The set of all inflected forms of *walk* is called the **lexeme** /walk/. The lexeme is denoted using one of the inflected forms of *walk* which is called the **base form** or **lemma** of the /walk/ lexeme. In the case of English verbs, this is the infinitive form.   

Inflectional affixes that occur before the stem are called **prefixes** and affixes that occur after the stem are called **suffixes**.

The morphological analysis `walk+V+Past` consists of the lemma `walk` and a number of **morphological features** like `+V` and `+Past` which here mark part of speech and tense, respectively.

Some word forms like *walks* are **ambiguous** in the sense that they correspond to more than one analysis. The form *walks* can be analyzed either as `walk+V+3Sg+Pres` (the 3rd singular present tense form of the verb walk) or `walk+N+Pl` (the plural form of the noun walk). This is called **morphological ambiguity**. An FST morphological analyzer should return all of the possible analyses given an input form like *walk*. 

## Ojibwe verbs

Ojibwe verb forms split into three segments:

1. Prefix
2. Stem
3. Suffix

The following example illustrates this division:

![Ojibwe verb](word.png)

### Verb prefix

The prefix can be empty or consist of several elements falling into two categories. The prefix starts with a **person prefix** which is followed by zero or more **preverbs**.

The person prefix denotes the subject of the verb. It is exclusively present in the independent order (see below) and only for the VAIO, VTI and VTA paradigms (see below). In the illustration above, the verb prefix contains the person prefix *ni* and a preverb *gii-*

Preverbs are separated from the stem (and other preverbs) by a hyphen `-`. In the verb analysis, they are marked by a preverb tag like *PVTense/gii+*. There are five types preverb markers:

1. `PVSub/xyz` & `ChCnj+` (subordinate preverb and changed conjunct marker)
2. `PVTense/xyz` (tense preverb)
3. `PVDir/xyz` (directional preverb)
4. `PDLex/xyz` (lexical preverb)

Where `xyz` is the canonical form of the preverb followed by `+`, e.g. `PVTense/gii+`, `PVTense/ga+` and `PVSub/a+`. In the example above, we can see that the analysis contains the tag `PVTense/gii+` which in the word form is realized as the prefix `gii-`.

The subordinate preverbs and changed conjunct marker can only occur in conjunct forms. The changed conjunct marker differs from the other preverbs in the sense that it is not realized as a prefix. Rather, it causes a *phonological alternation* in the first vowel of the verb form.  

### The verb stem and lexeme

The verb stem in the example above is `waabam`. It marks *nigii-waabamaabaniig* as an inflected form of the lexeme /waabam/. We can also see that the analysis contains the lemma `waabam`. Unlike tags, e.g. `+` 

### The verb suffix

The suffix encodes most of the inflectional information in the verb form. We have chosen to treat the verb suffix as a contiguous string like *aabaniig* in the example above. In reality, it consists of several smaller suffixes with complex dependencies that are difficult to model. 
