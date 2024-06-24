# [ParserTools](https://github.com/ELF-Lab/ParserTools/)

## Verb lexicons

Let's examine an example verb `nigii-waabamaabaniig` which corresponds to the analysis `PVTense/gii+waabam+VTA+Ind+Pos+Prt+1SgSubj+3PlProxObj`. This form is a result of a morphophonological intermediate representation from the lexicon: `ni<<gii<T>-<<waabam>>aabaniig` which together with phonological rules gives the correct surface form (in this case, the rules simply delete the boundary markers `<<` and `>>` as well as delete the tense-rule trigger `<T>`).

The flowchart below illustrates how the analysis and morphophonological form are represented in the Ojibwe lexc lexicon. Each block represents an entry in lexc sublexicon (like `VerbRoot`). The block contains an upper (or analysis string) and a lower (or morpholphonological) string. The concatenation of these define the string-pair `PVTense/gii+waabam+VTA+Ind+Pos+Prt+1SgSubj+3PlProxObj:nigii-waabamaabaniig`: 

<img src="img/lexc_diagram.png" width="2000" />
(click on the image to zoom in)

The sublexicons are:

1. `Root`: Generation always start here. This lexicon leads to word class-specific sublexicons like `VerbRoot`, `NounRoot`, `AdverbRoot`. The `Root` lexicon is located in the generated file `root.lexc`
2. `VerbRoot`: This lexicon leads to paradigm-specific person prefix lexicons e.g. `VTA_Prefix`. We use the flag diacritic `@P.Paradigm.VTA@` to mark this form as a VTA. We need to use a flag diacritic because the preverb lexicon is shared between multiple different verb paradigms and we need to make sure that we re-enter the stem lexicon. We continue to a person prefix lexicon. All verb-specific lexicons (apart from preverb lexicons) are located in the generated file `ojibwe_verbs.lexc`.
3. `VTA_Prefix`: The lexicon contains all person prefixes which are valid for VTAs (i.e. all of them `ni`, `gi`, `o` and the empty prefix). Here we get both the person prefix entry which is `ni` in this case and use the flag diacritic `@P.Prefix.NI@` to mark this as a ni-form. We continue to a morpheme boundary lexicon.
4. `VTA_PrefixBoundary`: Here we add a morpheme boundary on the lower side. From this lexicon, we continue to the PreverbRoot lexicon.
5. Multiple preverb lexicons: 
