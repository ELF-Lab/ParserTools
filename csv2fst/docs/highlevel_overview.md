## Overvivew of the compilation process

<img src="img/flow_chart.png" width="500"/>

The FST analyzer is built using three source repositories:

* OjibweMorph houses [morphological paradigms](paradigms.md), skeleton lexc code and the xfst phonological rewrite rules (this repository either is already freely available or will short be made freely available for under a non-commerical license)
* OPDDatabase houses a lexical database from the Ojibwe People's Dictionary (this repository will not be made publicly available)
* ParserTools houses the code for compiling lexc files from the source data in OjibweMorph and OPDDatabase (this repository is publicly available and licensed under CC Deed)

We split the code into three different repositories mainly due to licensing issues. We want everyone to be able to use OjibweMorph and ParserTools together with their own lexical database for Ojibwe or a different Algonquian language.

## OjibweMorph

## OPDDatabase

## ParserTools
