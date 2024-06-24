# [ParserTools](https://github.com/ELF-Lab/ParserTools/)

## Verb lexicons

Let's examine an example verb `nigii-waabamaabaniig` which corresponds to the analysis `PVTense/gii+waabam+VTA+Ind+Pos+Prt+1SgSubj+3PlProxObj`. This form is a result of a morphophonological intermediate representation from the lexicon: `ni<<gii<T>-<<waabam>>aabaniig` which together with phonological rules gives the correct surface form (in this case, the rules simply delete the boundary markers `<<` and `>>` as well as delete the tense-rule trigger `<T>`).

The flowchart below illustrates how the analysis and morphophonological form are represented in the Ojibwe lexc lexicon. Each block represents an entry in lexc sublexicon (like `VerbRoot`). The block contains an upper (or analysis string) and a lower (or morpholphonological) string. The concatenation of these define the string-pair `PVTense/gii+waabam+VTA+Ind+Pos+Prt+1SgSubj+3PlProxObj:nigii-waabamaabaniig`: 

<img src="img/lexc_diagram.png" width="2000" />
(click on the image to zoom in)


