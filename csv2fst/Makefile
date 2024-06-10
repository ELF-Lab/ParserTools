# Tools
PYTHON=python3
FOMA=foma

# Source files
# Change this to match your source morphology directory
MORPHOLOGYSRCDIR=~/src/OjibweMorph
VERB_JSON = $(MORPHOLOGYSRCDIR)/config/ojibwe_verbs.json
NOUN_JSON = $(MORPHOLOGYSRCDIR)/config/ojibwe_nouns.json
# Change this to match your Lexical database directory
DATABASEDIR=~/src/OPDDatabase

# YAML tests
CREATEYAML=../csv2yaml/create_yaml.py
LOOKUP=flookup

# These depend on the env variable GTCORE which is set when you build
# giella-core (I think...)
ifndef GTCORE
       $(warning The GTCORE environment variable is not set)
endif
MORPHTEST=$(GTCORE)/scripts/morph-test.py 

# Definitions for building the LEXC files
POS=verbs nouns pronouns adverbs particles numerals
LEXCTARGETS=$(POS:%=ojibwe_%.lexc)

all:$(LEXCTARGETS:%=generated/%) generated/ojibwe.fomabin generated/ojibwe.att

release:all
	zip generated.zip generated/*

generated/%.lexc:$(MORPHOLOGYSRCDIR)/config/%.json
	mkdir -p generated
	$(PYTHON) csv2lexc.py --config-file $^ --source-path $(MORPHOLOGYSRCDIR) --database-path $(DATABASEDIR) --lexc-path generated

%/phonology.xfst:$(MORPHOLOGYSRCDIR)/xfst/phonology.xfst
	mkdir -p $*
	cp $^ $@

generated/ojibwe.fomabin:$(LEXCTARGETS:%=generated/%) generated/phonology.xfst 
	mkdir -p generated
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd generated; $(FOMA) -f phonology.xfst

generated/ojibwe.noAlt.fomabin:generated/ojibwe.fomabin assets/delete_alt_tag.xfst 
	cp assets/delete_alt_tag.xfst generated
	cd generated; $(FOMA) -f delete_alt_tag.xfst

#####################################################################
#                                                                   #
#                             TESTS                                 #
#                                                                   #
#####################################################################

# We have to build a separate FST for YAML tests because entries from
# the external lexical database will interfere with YAML testing due
# to morphological ambiguity.

check: check-core-yaml check-yaml check-database

paradigm_yaml_output:
	rm -Rf $@
	mkdir $@
	$(PYTHON) $(CREATEYAML) $(MORPHOLOGYSRCDIR)/VerbSpreadsheets $(VERB_JSON) ./ --non-core-tags=Prt,Dub,PrtDub,DubPrt --pos=verb
	mv yaml_output/* $@
	$(PYTHON) $(CREATEYAML) $(MORPHOLOGYSRCDIR)/NounSpreadsheets $(NOUN_JSON) ./ --non-core-tags=Prt,Dub,PrtDub,DubPrt --pos=noun
	mv yaml_output/* $@

database_yaml_output:
	$(PYTHON) ../scrapedcsv2yaml/create_csv_from_scraped.py $(DATABASEDIR)/data/OPD_inflectional_forms.csv ../scrapedcsv2yaml/subj_obj_tags.csv csv_output/
	$(PYTHON) $(CREATEYAML) csv_output/ $(VERB_JSON) ./ --pos=verb
	mv yaml_output $@

check-generated/%.lexc:$(MORPHOLOGYSRCDIR)/config/%.json
	mkdir -p check-generated
	$(PYTHON) csv2lexc.py --config-file $^ --source-path $(MORPHOLOGYSRCDIR) --database-path $(DATABASEDIR) --lexc-path check-generated --read-lexical-database False

check-generated/ojibwe.fomabin:$(POS:%=check-generated/ojibwe_%.lexc) check-generated/phonology.xfst
	mkdir -p check-generated
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

check-database:generated/ojibwe.noAlt.fomabin assets/delete_alt_tag.xfst database_yaml_output
	rm -f opd-test.log	
	for f in `ls database_yaml_output/*.yaml | grep -v core`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor generated/ojibwe.noAlt.fomabin $$f; \
                  echo ; \
                  done > opd-test.log
	$(PYTHON) test_summary.py


clean:
	rm -rf generated check-generated paradigm_yaml_output database_yaml_output compile.log core-yaml-test.log yaml-test.log opd-test.log paradigm_yaml_output csv_output

