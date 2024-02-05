# Tools
PYTHON=python3
FOMA=foma

# Source files
BORDERLAKESMORPH=~/src/BorderLakesMorph
CONFFILE=examples/ojibwe.json
FSTSCRIPT=$(BORDERLAKESMORPH)/xfst/phonology.xfst

# YAML tests
# These depends on the env variable GTCORE which is set when you build
# giella-core (I think...)
ifndef GTCORE
       $(warning The GTCORE environment variable is not set)
endif
CREATEYAML=../csv2yaml/create_yaml.py
LOOKUP=flookup
MORPHTEST=$(GTCORE)/scripts/morph-test.py 
YAMLTESTDIR=$(shell pwd)/../csv2yaml/yaml_output

# Definitions for building the LEXC files
POS=verbs
LEXCTARGETS=$(POS:%=generated/ojibwe_%.lexc)

# Definitions for building the FST
FSTTARGET=generated/ojibwe.fomabin

all:$(LEXCTARGETS) $(FSTTARGET)

generated/%.lexc:examples/%.json
	mkdir -p generated
	$(PYTHON) csv2lexc.py --config-file $^ 

generated/ojibwe.fomabin:$(LEXCTARGETS)
	mkdir -p generated
	cp $(FSTSCRIPT) generated
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd generated; $(FOMA) -f phonology.xfst

yaml_output:
	$(PYTHON) $(CREATEYAML) $(BORDERLAKESMORPH)/Spreadsheets . --non-core-tags=Prt,Dub,PrtDub,DubPrt

check: check-core-yaml check-yaml

check-core-yaml:generated/ojibwe.fomabin yaml_output
	rm -f core-yaml-test.log
	for f in `ls yaml_output/*core.yaml`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor generated/ojibwe.fomabin $$f; \
                  echo ; \
                  done > core-yaml-test.log

check-yaml:generated/ojibwe.fomabin yaml_output
	rm -f yaml-test.log
	for f in `ls yaml_output/*.yaml | grep -v core`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor generated/ojibwe.fomabin $$f; \
                  echo ; \
                  done > yaml-test.log

clean:
	rm -rf generated yaml_output core-yaml-test.log yaml-test.log

