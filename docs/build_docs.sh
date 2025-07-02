pdoc --force -c syntax_highlighting=True --html ../FSTmorph/
rm -r -f ./html_docs
mkdir ./html_docs/
mv ./html/FSTmorph/*  ./html_docs/
rm -r html/

# rm -r -f docs/html_docs
# mkdir docs/html_docs/
# mv html/FSTmorph/* docs/html_docs/
# rm -r html/