# FST morphological analyzers

This discussion is a highly abbreviated version of the discussion in [the Foma morphological analysis tutorial](https://fomafst.github.io/morphtut.html).

FSTs (finite-state transducers) are models which map between two different set of strings `upper:lower`. The **upper** string represents a morphological analysis like `walk+Verb+Past` and the **lower** string represents the corresponding inflected word form `walked`. The FST can map a lower word form into an upper analysis `walked -> walk+Verb+Past`. This is called **analysis** or **lookup**. It can also perform a mapping in the inverse direction `walk+Verb+Past -> walked`. This is called **generation** or **lookdown**.

## Lexc lexicons

As discussed in the [morphology document](morphology.md), word forms like `walked` consist of a stem `walk` and inflectional affixes `-ed`. A **lexc lexicon** specifies stems for different word classes and their various affixes. Logically, it can be represented as a tree structure:

```
! The Multichar_Symbols section lists string which should
! be treated as atomic tags.
Multichar_Symbols

! Word classes
+Noun +Verb

! Noun morphological features: singular and plural
+Sg +Pl

! Verb morphological features: infinitive and past
+Inf +Past

!!!!! End of Multichar_Symbols !!!!!

! A unique Root lexicon is always required. This represents
! the root of the lexicon tree. All forms start here
LEXICON Root
Noun ; ! When there is only one entry on the lexicon line, it is assumed to be the name of a continuation lexicon 
Verb ; 

LEXICON Noun
dog NounEnding ; ! Here, we get the stem "dog" which doubles as a lemma. The rest of the form can be found in the continuation lexicon NounEnding
cat NounEnding ;

LEXICON Verb
walk VerbEnding ;
talk VerbEnding ;

LEXICON NounEnding
+Noun+Sg:0 # ; ! When the upper and lower string differ, they need to be separated by a colon ":". The upper (analysis) string is written on the left and the lower (word form) string on the right.
+Noun+Pl:s # ; ! '#' marks that the word form ends here.

LEXICON VerbEnding
+Verb+Inf:0 # ;
+Verb+Past:ed # ;
```
