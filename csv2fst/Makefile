PYTHON=python3

# Source files
BORDERLAKESMORPH=~/src/BorderLakesMorph
CSVDIR= $(BORDERLAKESMORPH)/Spreadsheets
OPDDATABASE=$(BORDERLAKESMORPH)/Database/main_entries-VERBS_fields-lemma-stem-POS.csv
FSTSCRIPT=$(BORDERLAKESMORPH)/xfst/phonology.xfst

# YAML tests
# These depends on the env variable GTCORE which is set when you build
# giella-core (I think...)
ifndef GTCORE
       $(warning The GTCORE environment variable is not set)
endif
LOOKUP=flookup
MORPHTEST=$(GTCORE)/scripts/morph-test.py 
YAMLTESTDIR=$(shell pwd)/../csv2yaml/yaml_output

# Definitions for building the LEXC files
CSVTOLEXC=./csv2lexc.py
SUBCLASSES=VAIO_CNJ VAIO_IMP VAIO_IND VAI_CNJ VAI_IMP VAI_IND VII_CNJ VII_IND VTA_CNJ VTA_IMP VTA_IND VTI_CNJ VTI_IMP VTI_IND
RESDIR=generated
LEXCTARGETS=$(SUBCLASSES:%=$(RESDIR)/%.lexc)

# Definitions for building the FST
FOMA=foma
FSTTARGET=ojibwe.fomabin

all:ojibwe.fomabin $(LEXCTARGETS)

$(RESDIR)/%.lexc:$(CSVDIR)/%.csv
	mkdir -p $(RESDIR)
	$(PYTHON) $(CSVTOLEXC) --csv_file $< --multichar_symbol_file $(CSVDIR)/multichar_symbols.txt --lexc_file $@ --database_file $(OPDDATABASE)

$(FSTTARGET):$(FSTSCRIPT) $(LEXCTARGETS)
	mkdir -p $(RESDIR)
	cp $(FSTSCRIPT) $(RESDIR)
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd $(RESDIR); $(FOMA) -f $<

check-yaml:all
	rm -f yamltest.log
	mkdir -p yaml-generated
	for c in `ls $(CSVDIR)/*csv`; do $(PYTHON) $(CSVTOLEXC) --csv_file $$c --multichar_symbol_file $(CSVDIR)/multichar_symbols.txt --lexc_file yaml-generated/`echo $$c | sed 's/.*\/\(.*\).csv/\1.lexc/'`; done
	cp $(FSTSCRIPT) yaml-generated
	cd yaml-generated; $(FOMA) -f $(FSTSCRIPT)
	for f in `ls $(YAMLTESTDIR)/*yaml`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor yaml-generated/$(FSTTARGET) $$f; \
                  done > yamltest.log

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
	rm -rf $(RESDIR)
