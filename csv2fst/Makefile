# Tools
PYTHON=python3
FOMA=foma

# Source files
# Change this to match your source morphology directory
MORPHOLOGYSRCDIR=~/OjibweMorph
VERB_JSON = $(MORPHOLOGYSRCDIR)/config/ojibwe_verbs.json
NOUN_JSON = $(MORPHOLOGYSRCDIR)/config/ojibwe_nouns.json
# Change this to match your Lexical database directory
DATABASEDIR=~/OPDDatabase

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

all:generated/all.lexc generated/ojibwe.fomabin generated/ojibwe.att

release:all
	zip generated.zip generated/*

generated/all.lexc:$(shell find $(MORPHOLOGYSRCDIR)/config/ -name "*.json")
	mkdir -p generated
	$(PYTHON) csv2fst/csv2lexc.py --config-files `echo $^ | tr ' ' ','` \
                              --source-path $(MORPHOLOGYSRCDIR) \
                              --database-path $(DATABASEDIR) \
                              --lexc-path generated
	cd generated; \
        cat root.lexc `ls *lexc | grep -v root.lexc | tr '\n' ' '` > all.lexc

%/phonology.xfst:$(MORPHOLOGYSRCDIR)/xfst/phonology.xfst
	mkdir -p $*
	cp $^ $@

generated/compile_fst.xfst:./assets/compile_fst.xfst
	mkdir -p generated
	cp $^ $@

check-generated/compile_fst.xfst:./assets/compile_fst.xfst
	mkdir -p check_generated
	cp $^ $@

generated/ojibwe.fomabin:generated/all.lexc generated/phonology.xfst generated/compile_fst.xfst
	mkdir -p generated
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd generated; $(FOMA) -f compile_fst.xfst

generated/ojibwe.noAlt.fomabin:generated/ojibwe.fomabin assets/delete_alt_tag.xfst 
	cp assets/delete_alt_tag.xfst generated
	cd generated; $(FOMA) -f delete_alt_tag.xfst

# For building spell checkers etc. using Giellatekno infrastructure.
generated/lang-ciw:generated/all.lexc generated/phonology.xfst
	cd generated; \
        git clone git@github.com:giellalt/lang-ciw.git; \
	cp root.lexc lang-ciw/src/fst/morphology/ ; \
	cp phonology.xfst lang-ciw/src/fst/morphology/phonology.xfscript ; \
	cp $(LEXCTARGETS) lang-ciw/src/fst/morphology/stems/; \
	cp preverbs.lexc prenouns.lexc lang-ciw/src/fst/morphology/stems/

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

check-generated/all.lexc:$(shell find $(MORPHOLOGYSRCDIR)/config/ -name "*.json")
	mkdir -p check-generated
	$(PYTHON) csv2fst/csv2lexc.py --config-files `echo $^ | tr ' ' ','` \
                              --source-path $(MORPHOLOGYSRCDIR) \
                              --database-path $(DATABASEDIR) \
                              --lexc-path check-generated \
                              --read-lexical-database False
	cd check-generated; \
        cat root.lexc `ls *lexc | grep -v root.lexc | tr '\n' ' '` > all.lexc

check-generated/ojibwe.fomabin:check-generated/all.lexc check-generated/phonology.xfst check-generated/compile_fst.xfst 
	mkdir -p check-generated
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd check-generated; $(FOMA) -f compile_fst.xfst

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
	$(PYTHON) csv2fst/test_summary.py


clean:
	rm -rf generated check-generated paradigm_yaml_output database_yaml_output compile.log core-yaml-test.log yaml-test.log opd-test.log paradigm_yaml_output csv_output

#####################################################################
#                                                                   #
#                       DOCUMENTATION                               #
#                                                                   #
#####################################################################

# Generating documentation requires the python module pdoc
# Install it by `pip3 install pdoc3` if you need to build
# the docs

doc:*py
	pdoc --force -c syntax_highlighting=True --html .; mv html/csv2fst/* docs/csv2fst_html_docs

