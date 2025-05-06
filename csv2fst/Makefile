# Tools
PYTHON=python3
FOMA=foma

# Source files
# Change this to match your source morphology directory
MORPHOLOGYSRCDIR=~/Documents/ELF/OjibweTesting/OjibweMorph
VERB_JSON = $(MORPHOLOGYSRCDIR)/config/verbs.json
NOUN_JSON = $(MORPHOLOGYSRCDIR)/config/nouns.json
# Can be a list (separated by commas) e.g., LEMMAS_DIR=~/folder1,~/folder2
LEMMAS_DIR=~/Documents/ELF/OjibweTesting/OjibweLexicon/OPD,~/Documents/ELF/OjibweTesting/OjibweLexicon/HammerlyFieldwork
LEXICAL_DATA_TO_EXCLUDE=""
OUTPUT_DIR=$(MORPHOLOGYSRCDIR)/FST
# Additional info used for testing the FST
SPREADSHEETS_FOR_YAML_DIR=~/Documents/ELF/OjibweTesting/OjibweLexicon/OPD/for_yaml
PARADIGM_MAPS_DIR=~/Documents/ELF/OjibweTesting/OjibweLexicon/resources

# For naming output files
LANGUAGE_NAME=language

# YAML tests
CREATEYAML=../csv2yaml/create_yaml.py
LOOKUP=flookup

MORPHTEST=src/morph-test.py

# Definitions for building the LEXC files
# POS are determined by the files in config/
CONFIG_FILES=$(shell find $(MORPHOLOGYSRCDIR)/config/ -name "*.json")
# Add escape chars to the file path so it can be used in the gsub below
MORPHOLOGYSRCDIR_REGEX=$(shell echo $(MORPHOLOGYSRCDIR) | sed 's/\./\\\./g' | sed 's/\//\\\//g')
# Strip each file path to only include the POS e.g., "../config/nouns.json" -> "nouns"
POS=$(shell awk '{ gsub(/$(MORPHOLOGYSRCDIR_REGEX)\/config\/+/, ""); gsub(/\.json/, ""); print }' <<< "$(CONFIG_FILES)")
LEXCTARGETS=$(POS:%=%.lexc)
TAG_CONFIGURATION_FILES=$(POS:%=$(OUTPUT_DIR)/generated/%_tags.json)
ALTTAG=False
DERIVATIONS=True

all:$(OUTPUT_DIR)/generated/all.lexc $(OUTPUT_DIR)/generated/$(LANGUAGE_NAME).fomabin $(OUTPUT_DIR)/generated/$(LANGUAGE_NAME).att $(TAG_CONFIGURATION_FILES)

release:all
	zip generated.zip $(OUTPUT_DIR)/generated/*

$(OUTPUT_DIR)/generated/all.lexc:$(CONFIG_FILES)
	mkdir -p $(OUTPUT_DIR)/generated
	$(PYTHON) src/csv2lexc.py --config-files `echo $^ | tr ' ' ','` \
                              --source-path $(MORPHOLOGYSRCDIR) \
                              --database-paths $(LEMMAS_DIR) \
                              --alt-tag $(ALTTAG) \
                              --add-derivations $(DERIVATIONS) \
                              --lexc-path $(OUTPUT_DIR)/generated \
                              --lexical-data-to-exclude $(LEXICAL_DATA_TO_EXCLUDE)
	cd $(OUTPUT_DIR)/generated; \
        cat root.lexc `ls *lexc | grep -v root.lexc | tr '\n' ' '` > all.lexc

%/phonology.xfst:$(MORPHOLOGYSRCDIR)/xfst/phonology.xfst
	mkdir -p $*
	cp $^ $@

$(OUTPUT_DIR)/generated/compile_fst.xfst:./assets/compile_fst.xfst
	mkdir -p $(OUTPUT_DIR)/generated
	cp $^ $@
	cat $^ | sed 's/LANGUAGE_NAME/$(LANGUAGE_NAME)/g' > $@

$(OUTPUT_DIR)/check-generated/compile_fst.xfst:./assets/compile_fst.xfst
	mkdir -p $(OUTPUT_DIR)/check-generated
	cat $^ | sed 's/LANGUAGE_NAME/$(LANGUAGE_NAME)/g' > $@

$(OUTPUT_DIR)/generated/$(LANGUAGE_NAME).fomabin:$(OUTPUT_DIR)/generated/all.lexc $(OUTPUT_DIR)/generated/phonology.xfst $(OUTPUT_DIR)/generated/compile_fst.xfst
	mkdir -p $(OUTPUT_DIR)/generated
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd $(OUTPUT_DIR)/generated; $(FOMA) -f compile_fst.xfst

$(OUTPUT_DIR)/generated/$(LANGUAGE_NAME).noAlt.fomabin:$(OUTPUT_DIR)/generated/$(LANGUAGE_NAME).fomabin assets/delete_alt_tag.xfst 
	cat assets/delete_alt_tag.xfst | sed 's/LANGUAGE_NAME/$(LANGUAGE_NAME)/g' > $(OUTPUT_DIR)/generated/delete_alt_tag.xfst
	cd $(OUTPUT_DIR)/generated; $(FOMA) -f delete_alt_tag.xfst

# For building spell checkers etc. using Giellatekno infrastructure.
$(OUTPUT_DIR)/generated/lang-ciw:$(OUTPUT_DIR)/generated/all.lexc $(OUTPUT_DIR)/generated/phonology.xfst
	mkdir -p $(OUTPUT_DIR)/generated
	cd $(OUTPUT_DIR)/generated; \
        git clone https://github.com/giellalt/lang-ciw.git; \
	cp root.lexc lang-ciw/src/fst/morphology/ ; \
	cp phonology.xfst lang-ciw/src/fst/morphology/phonology.xfscript ; \
	cp $(LEXCTARGETS) lang-ciw/src/fst/morphology/stems/; \
	cp preverbs.lexc prenouns.lexc preadverbs.lexc lang-ciw/src/fst/morphology/stems/

# Tag specification file
$(OUTPUT_DIR)/generated/verbs_tags.json:$(MORPHOLOGYSRCDIR)/config/verbs.json
	mkdir -p $(OUTPUT_DIR)/generated
	$(PYTHON) src/extract_tag_combinations.py \
             --config-file $< \
             --source-path $(MORPHOLOGYSRCDIR) \
             --pre-element=TensePreverbs \
             --pre-element-tags="PVTense/gii,0" \
             --post-element=Derivations \
             --post-element-tags="VII+Augment/magad,0" \
             --output-file $@

$(OUTPUT_DIR)/generated/%_tags.json:$(MORPHOLOGYSRCDIR)/config/%.json
	mkdir -p $(OUTPUT_DIR)/generated
	$(PYTHON) src/extract_tag_combinations.py \
             --config-file $< \
             --source-path $(MORPHOLOGYSRCDIR) \
             --output-file $@


#####################################################################
#                                                                   #
#                             TESTS                                 #
#                                                                   #
#####################################################################

# We have to build a separate FST for YAML tests because entries from
# the external lexical database will interfere with YAML testing due
# to morphological ambiguity.

check: check-core-paradigm check-paradigm check-opd

# Add non-core-tags if you want to run some "core" tests as well
$(OUTPUT_DIR)/paradigm_yaml_output:
	rm -Rf $@
	mkdir $@
	$(PYTHON) $(CREATEYAML) $(MORPHOLOGYSRCDIR)/VerbSpreadsheets $(VERB_JSON) ./ --pos=verb
	mv yaml_output/* $@
	$(PYTHON) $(CREATEYAML) $(MORPHOLOGYSRCDIR)/NounSpreadsheets $(NOUN_JSON) ./ --pos=noun
	mv yaml_output/* $@
	rm -d yaml_output

$(OUTPUT_DIR)/opd_yaml_output:
	rm -Rf $@
	mkdir $@
	$(PYTHON) $(CREATEYAML) $(SPREADSHEETS_FOR_YAML_DIR)/verbs/ $(VERB_JSON) ./ --pos=verb
	mv yaml_output/* $@
	$(PYTHON) $(CREATEYAML) $(SPREADSHEETS_FOR_YAML_DIR)/nouns/ $(NOUN_JSON) ./ --pos=noun
	mv yaml_output/* $@
	rm -d yaml_output

$(OUTPUT_DIR)/check-generated/all.lexc:$(shell find $(MORPHOLOGYSRCDIR)/config/ -name "*.json")
	mkdir -p $(OUTPUT_DIR)/check-generated
	$(PYTHON) src/csv2lexc.py --config-files `echo $^ | tr ' ' ','` \
                              --source-path $(MORPHOLOGYSRCDIR) \
                              --database-paths $(LEMMAS_DIR) \
                              --lexc-path $(OUTPUT_DIR)/check-generated \
                              --add-derivations $(DERIVATIONS) \
                              --read-lexical-database False \
                              --alt-tag False \
                              --lexical-data-to-exclude $(LEXICAL_DATA_TO_EXCLUDE)
	cd $(OUTPUT_DIR)/check-generated; \
        cat root.lexc `ls *lexc | grep -v root.lexc | tr '\n' ' '` > all.lexc

$(OUTPUT_DIR)/check-generated/$(LANGUAGE_NAME).fomabin:$(OUTPUT_DIR)/check-generated/all.lexc $(OUTPUT_DIR)/check-generated/phonology.xfst $(OUTPUT_DIR)/check-generated/compile_fst.xfst 
	mkdir -p $(OUTPUT_DIR)/check-generated
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd $(OUTPUT_DIR)/check-generated; $(FOMA) -f compile_fst.xfst

# If there are no core YAML files, this will do nothing.
check-core-paradigm:$(OUTPUT_DIR)/check-generated/$(LANGUAGE_NAME).fomabin $(OUTPUT_DIR)/paradigm_yaml_output
	rm -f $(OUTPUT_DIR)/core-paradigm-test.log
	for f in `ls $(OUTPUT_DIR)/paradigm_yaml_output/*core.yaml`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor $(OUTPUT_DIR)/check-generated/$(LANGUAGE_NAME).fomabin $$f; \
                  echo ; \
                  done > $(OUTPUT_DIR)/core-paradigm-test.log
	if [ ! -s "$(OUTPUT_DIR)/core-paradigm-test.log" ]; then \
		rm -f $(OUTPUT_DIR)/core-paradigm-test.log; \
	fi

check-paradigm:$(OUTPUT_DIR)/check-generated/$(LANGUAGE_NAME).fomabin $(OUTPUT_DIR)/paradigm_yaml_output
	rm -f $(OUTPUT_DIR)/paradigm-test.log
	for f in `ls $(OUTPUT_DIR)/paradigm_yaml_output/*.yaml | grep -v core`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor $(OUTPUT_DIR)/check-generated/$(LANGUAGE_NAME).fomabin $$f; \
                  echo ; \
                  done > $(OUTPUT_DIR)/paradigm-test.log
	$(PYTHON) src/test_summary.py --input_file_name "$(OUTPUT_DIR)/paradigm-test.log" --paradigm_map_path "$(PARADIGM_MAPS_DIR)/VERBS_paradigm_map.csv" --output_dir $(OUTPUT_DIR) --output_file_name "paradigm_verb_test_summary.csv"
	$(PYTHON) src/test_summary.py --input_file_name "$(OUTPUT_DIR)/paradigm-test.log" --paradigm_map_path "$(PARADIGM_MAPS_DIR)/NOUNS_paradigm_map.csv" --output_dir $(OUTPUT_DIR) --output_file_name "paradigm_noun_test_summary.csv" --for_nouns

check-opd:$(OUTPUT_DIR)/generated/$(LANGUAGE_NAME).noAlt.fomabin assets/delete_alt_tag.xfst $(OUTPUT_DIR)/opd_yaml_output
	rm -f $(OUTPUT_DIR)/opd-test.log	
	for f in `ls $(OUTPUT_DIR)/opd_yaml_output/*.yaml | grep -v core`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --app $(LOOKUP) --surface --mor $(OUTPUT_DIR)/generated/$(LANGUAGE_NAME).noAlt.fomabin $$f; \
                  echo ; \
                  done > $(OUTPUT_DIR)/opd-test.log
	$(PYTHON) src/test_summary.py --input_file_name "$(OUTPUT_DIR)/opd-test.log" --yaml_source_csv_path "$(SPREADSHEETS_FOR_YAML_DIR)/verbs/verb_inflectional_forms_for_yaml.csv" --paradigm_map_path "$(PARADIGM_MAPS_DIR)/VERBS_paradigm_map.csv" --output_dir $(OUTPUT_DIR) --output_file_name "opd_verb_test_summary.csv"
	$(PYTHON) src/test_summary.py --input_file_name "$(OUTPUT_DIR)/opd-test.log" --yaml_source_csv_path "$(SPREADSHEETS_FOR_YAML_DIR)/nouns/noun_inflectional_forms_for_yaml.csv" --paradigm_map_path "$(PARADIGM_MAPS_DIR)/NOUNS_paradigm_map.csv" --output_dir $(OUTPUT_DIR) --output_file_name "opd_noun_test_summary.csv" --for_nouns


clean:
	rm -rf $(OUTPUT_DIR)/generated $(OUTPUT_DIR)/check-generated $(OUTPUT_DIR)/paradigm_yaml_output $(OUTPUT_DIR)/opd_yaml_output $(OUTPUT_DIR)/core-paradigm-test.log $(OUTPUT_DIR)/paradigm-test.log $(OUTPUT_DIR)/opd-test.log csv_output

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

