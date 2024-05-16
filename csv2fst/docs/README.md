## A bit of terminology

Morphological FST analyzers translate an input **word form** like *walked* into an **analysis** like `walk+V+Past`. 

The word form *walked* can be split into two **morphemes**: 

* The **stem** *walk* and
* the **affix** *ed* (sometimes denoted as *-ed* to mark that it is bound to the stem).

The stem is the **unchanging** part of all inflected forms of *walk*, namely, *walk*, *walks*, *walking*, *walked*. The set of all inflected forms of *walk* is called the **lexeme** /walk/. The lexeme is denoted using one of the inflected forms of *walk* which is called the **base form** or **lemma** of the /walk/ lexeme. In the case of English verbs, this is the infinitive form.   

Inflectional affixes that occur before the stem are called **prefixes** and affixes that occur after the stem are called **suffixes**.

The morphological analysis `walk+V+Past` consists of the lemma `walk` and a number of **morphological features** like `+V` and `+Past` which here mark part of speech and tense, respectively.

Some word forms like *walks* are **ambiguous** in the sense that they correspond to two or more analyses. The form *walks* can be analyzed either as `walk+V+3Sg+Pres` (the 3rd singular present tense form of the verb walk) or `walk+N+Pl` (the plural form of the noun walk). This is called **morphological ambiguity**. An FST morphological analyzer should return all of the possible analyses given an input form like *walk*. 

## Ojibwe verbs

Ojibwe verbforms can be split into three segments:

1. Prefix
2. Stem
3. Suffix

The following example illustrates this division:

![Ojibwe verb](word.png)

### The verb prefix

The prefix can consist of several elements falling into two categories. The prefix can start with a person prefix which can be followed by one or more preverbs. One or both of these can also be missing.

#### Person prefix

The person prefix marks subject. It is exclusively present in the independent order (see below) and only for the VAIO, VTI and VTA paradigms (see below) which take both a subject and an object. In the illustration above, the verb prefix contains the person prefix *ni* and a preverb *gii-*

Preverbs are marked by a preverb tag like *PVTense/gii+* in the verb analysis. 

### The verb stem

### The verb suffix