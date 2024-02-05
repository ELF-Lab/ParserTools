# Tools
PYTHON=python3
FOMA=foma

# Source files
# Change this to match your source directory
BORDERLAKESMORPH=~/src/BorderLakesMorph

# YAML tests
CREATEYAML=../csv2yaml/create_yaml.py
LOOKUP=flookup
# These depends on the env variable GTCORE which is set when you build
# giella-core (I think...)
ifndef GTCORE
       $(warning The GTCORE environment variable is not set)
endif
MORPHTEST=$(GTCORE)/scripts/morph-test.py 

# Definitions for building the LEXC files
POS=verbs
LEXCTARGETS=$(POS:%=generated/ojibwe_%.lexc)

all:$(LEXCTARGETS) generated/ojibwe.fomabin

generated/%.lexc:examples/%.json
	mkdir -p generated
	$(PYTHON) csv2lexc.py --config-file $^ 

generated/ojibwe.fomabin:$(LEXCTARGETS)
	mkdir -p generated
	cp $(BORDERLAKESMORPH)/xfst/phonology.xfst generated
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

check-core-yaml:all
	rm -f core-yamltest.log
	mkdir -p yaml-generated
	for c in `ls $(CSVDIR)/*csv`; do $(PYTHON) $(CSVTOLEXC) --csv_file $$c --multichar_symbol_file $(CSVDIR)/multichar_symbols.txt --lexc_file yaml-generated/`echo $$c | sed 's/.*\/\(.*\).csv/\1.lexc/'`; done
	cp $(FSTSCRIPT) yaml-generated
	cd yaml-generated; $(FOMA) -f $(FSTSCRIPT)
	for f in `ls $(YAMLTESTDIR)/*core.yaml`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor yaml-generated/$(FSTTARGET) $$f; \
                  done > core-yamltest.log

clean:
	rm -rf generated yaml_output core-yaml-test.log yaml-test.log

