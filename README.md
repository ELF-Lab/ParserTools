# FSTmorph
This repository houses a set of language-neutral tools for converting CSVs to a finite-state transducer (FST), as well as for testing that FST via YAML files.

Documentation can be found inside [docs](./docs/).

## User Instructions
#### Installation
This package can be installed via pip:  
`pip install fstmorph`

The distribution files can also be downloaded directly from the `dist/` folder.

#### Using FSTmorph
A thorough example of how to use this package is given in [OjibweMorph](https://github.com/ELF-Lab/OjibweMorph), outlining how to build, test, and use an FST in Ojibwe using FSTmorph.  The [Makefile](https://github.com/ELF-Lab/OjibweMorph/blob/main/Makefile) there outlines how the code in this repo is utilized.

That said, this FST-generating code is intended to be applicable for other Algonquian languages and beyond -- if you have the necessary spreadsheets for your target language, it should be compatible with this code!

## Citation
To cite this work or the contents of the repository in an academic work, please use the following:

> [Hammerly, C., Livesay, N., Arppe A., Stacey, A., & Silfverberg, M. (Submitted) OjibweMorph: An approachable morphological parser for Ojibwe](https://christopherhammerly.com/publication/ojibwemorph/OjibweMorph.pdf)
