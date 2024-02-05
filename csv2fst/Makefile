 $(CSVDIR)/multichar_symbols.txt --lexc_file $@ --database_file $(OPDDATABASE)

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
	rm -rf $(RESDIR)~
