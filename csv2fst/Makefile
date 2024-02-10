# Tools
PYTHON=python3
FOMA=foma

# Source files
# Change this to match your source directory
MORPHOLOGYSRCDIR=~/src/BorderLakesMorph

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

generated/%.lexc:$(MORPHOLOGYSRCDIR)/%.json
	mkdir -p generated
	$(PYTHON) csv2lexc.py --config-file $^ --lexc-path generated

generated/ojibwe.fomabin:$(LEXCTARGETS)
	mkdir -p generated
	cp $(MORPHOLOGYSRCDIR)/xfst/phonology.xfst generated
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd generated; $(FOMA) -f phonology.xfst

paradigm_yaml_output:
	$(PYTHON) $(CREATEYAML) $(MORPHOLOGYSRCDIR)/Spreadsheets ./ --non-core-tags=Prt,Dub,PrtDub,DubPrt
	mv yaml_output $@

database_yaml_output:
	python3 ../scrapedcsv2yaml/create_yaml_from_scraped.py $(MORPHOLOGYSRCDIR)/Database/inflectional_forms.csv csv_output/
	$(PYTHON) $(CREATEYAML) csv_output/ ./
	mv yaml_output $@

#####################################################################
#                                                                   #
#                             TESTS                                 #
#                                                                   #
#####################################################################

# We have to build a separate FST for YAML tests because entries from
# the external lexical database will interfere with YAML testing due
# to morphological ambiguity.

check: check-core-yaml check-yaml check-database

check-generated/%.lexc:$(MORPHOLOGYSRCDIR)/%.json
	mkdir -p check-generated
	$(PYTHON) csv2lexc.py --config-file $^ --lexc-path check-generated --read-lexical-database False

check-generated/ojibwe.fomabin:$(POS:%=check-generated/ojibwe_%.lexc)
	mkdir -p check-generated
	cp $(MORPHOLOGYSRCDIR)/xfst/phonology.xfst check-generated
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd check-generated; $(FOMA) -f phonology.xfst

check-core-yaml:check-generated/ojibwe.fomabin paradigm_yaml_output
	rm -f core-yaml-test.log
	for f in `ls paradigm_yaml_output/*core.yaml`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor check-generated/ojibwe.fomabin $$f; \
                  echo ; \
                  done > core-yaml-test.log

check-yaml:check-generated/ojibwe.fomabin paradigm_yaml_output
	rm -f yaml-test.log
	for f in `ls paradigm_yaml_output/*.yaml | grep -v core`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor check-generated/ojibwe.fomabin $$f; \
                  echo ; \
                  done > yaml-test.log

check-database:generated/ojibwe.fomabin database_yaml_output
	rm -f opd-test.log
	for f in `ls database_yaml_output/*.yaml | grep -v core`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor generated/ojibwe.fomabin $$f; \
                  echo ; \
                  done > opd-test.log


clean:
	rm -rf generated check-generated paradigm_yaml_output database_yaml_output compile.log core-yaml-test.log yaml-test.log opd-test.log

