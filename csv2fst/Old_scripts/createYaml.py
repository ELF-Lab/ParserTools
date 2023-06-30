import pandas as pd

# Change XLS_NAME and analysis for each spreadsheet
XLS_NAME = "VII.xlsx"
analysis = lambda: "+".join([row["Lexeme"], "VII", row["Subject"], row["Negation"], row["Mode"].replace(" ","")])

xls = pd.ExcelFile(XLS_NAME)

for sheet in xls.sheet_names:
	df = pd.read_excel(XLS_NAME, sheet_name=sheet)
	yaml_dict = {}

	for i, row in df.iterrows():
		row = row.to_dict()

		# this will skip empty lines, which are read as floats
		if type(row["Form1"]) is float:
			continue

		if row["Stem"] not in yaml_dict:
			yaml_dict[row["Stem"]] = []

		# check if there is a form2
		if type(row["Form2"]) is not float:
			forms = f"[{row['Form1']},{row['Form2']}]"
		else:
			forms = f"{row['Form1']}"

		yaml_dict[row["Stem"]].append((analysis(), forms))

	for key, value in yaml_dict.items():
		with open(f"{sheet}_{key}.yaml", "w+") as yaml_file:
			for tag, forms in value:
				yaml_file.write(f"{tag}: {forms}\n")
