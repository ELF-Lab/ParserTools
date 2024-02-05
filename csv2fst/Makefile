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

LOOKUP=flookup
MORPHTEST=$(GTCORE)/scripts/morph-test.py 
YAMLTESTDIR=$(shell pwd)/../csv2yaml/yaml_output

# Definitions for building the LEXC files
POS=verbs
LEXCTARGETS=$(POS:%=generated/ojibwe_%.lexc)

# Definitions for building the FST
FOMA=foma
FSTTARGET=generated/ojibwe.fomabin

all:$(LEXCTARGETS) $(FSTTARGET)

generated/%.lexc:examples/%.json
	mkdir -p generated
	python3 csv2lexc.py --config-file $^ 

generated/ojibwe.fomabin:$(LEXCTARGETS)
	mkdir -p generated
	cp $(FSTSCRIPT) generated
	echo "Compiling FST using XFST script $(FSTSCRIPT) and LEXC targets $(LEXCTARGETS)"
	cd generated; $(FOMA) -f phonology.xfst

clean:
	rm -rf generated yaml-generated yaml-core-generated
