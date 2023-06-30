import pandas
import math
import yaml

df = pandas.read_excel("VII.xlsx",sheet_name=None)

df_ind = df["VII_IND"]
df_cnj = df["VII_CNJ"]

# df_ind_aa = df_ind[df_ind["Stem"] == "aa"]

yaml_dict_ind = {}
yaml_dict_cnj = {}

# for i, row in df_ind_aa.iterrows():
# 	row = row.to_dict()
# 	#print(row)
# 	#print("--")
# 	test_analysis = "+".join([row["Lexeme"], "VII", row["Subject"], row["Negation"], row["Mode"].replace(" ","")])
# 	for key in ["Form1", "Form2"]:
# 		test_form = row[key]
# 		if type(test_form) == type(""):
# 			yaml_dict[test_analysis] = test_form

# f = open("VII_IND_aa.yaml", "w")
# yaml.dump(yaml_dict, f)

vii_analysis = lambda: "+".join([row["Lexeme"], "VII", row["Subject"], row["Negation"], row["Mode"].replace(" ","")])

for i, row in df_ind.iterrows():
	row = row.to_dict()
	# this will skip empty lines, which are read as floats
	if type(row["Form1"]) is float:
		continue
	if row["Stem"] not in yaml_dict_ind:
		yaml_dict_ind[row["Stem"]] = []
	# check if there is a form2
	if type(row["Form2"]) is not float:
		forms = f"[{row['Form1']},{row['Form2']}]"
	else:
		forms = f"{row['Form1']}"
	yaml_dict_ind[row["Stem"]].append((vii_analysis(),forms))

print(yaml_dict_ind)

# for i, row in df_ind.iterrows():
# 	row = row.to_dict()
# 	print(row)
# 	test_analysis = "+".join([row["Lexeme"], "VII", row["Subject"], row["Negation"], row["Mode"].replace(" ","")])
# 	for key in ["Form1", "Form2"]:
# 		test_form = row[key]
# 		if type(test_form) == type(""):
# 			yaml_dict_ind[test_analysis] = test_form

# f = open("VII_IND.yaml", "w")
# yaml.dump(yaml_dict_ind, f)


# for i, row in df_cnj.iterrows():
# 	row = row.to_dict()
# 	test_analysis = "+".join([row["Lexeme"], "VII", row["Subject"], row["Negation"], row["Mode"].replace(" ","")])
# 	for key in ["Form1", "Form2"]:
# 		test_form = row[key]
# 		if type(test_form) == type(""):
# 			yaml_dict_cnj[test_analysis] = test_form

# g = open("VII_CNJ.yaml", "w")
# yaml.dump(yaml_dict_cnj, g)

