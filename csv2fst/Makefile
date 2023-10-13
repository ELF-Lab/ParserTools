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
YAMLTESTDIR=$(CSVDIR)/yaml_output

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
	$(PYTHON) $(CSVTOLEXC) --csv_file $< --lexc_file $@ --database_file $(OPDDATABASE)

$(FSTTARGET):$(FSTSCRIPT) $(LEXCTARGETS)
	mkdir -p $(RESDIR)
	cp $(FSTSCRIPT) $(RESDIR)
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd $(RESDIR); $(FOMA) -f $<

check:all
	# FIXME: Enable VTA tests
	rm -f yamltest.log
	for f in `ls $(YAMLTESTDIR)/*yaml | grep -v VTA`; do \
                  echo "YAML test file $$f"; \
                  $(PYTHON) $(MORPHTEST) --hide-passes --app $(LOOKUP) --surface --mor $(RESDIR)/$(FSTTARGET) $$f; \
                  done > yamltest.log

clean:
	rm -rf $(RESDIR)
