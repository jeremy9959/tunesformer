import re
import add_cc_filter
import sys
import json

abc_files = sys.argv[1:]
json_file = "data.json"
data = []
tune_count = 0

for abc_file in abc_files:

    with open(abc_file) as f:
        abc = f.read()

    split_abc = abc.split("X:")

    for raw_tune in split_abc[1:]:
        tune = "X:" + raw_tune
        tune_names = ""
        tune_names = re.findall(r"T:\s*(?P<tune_name>.*)", tune)
        tune_names = [
            re.sub(r"[^a-zA-Z\s]", "", x).lstrip().rstrip().replace("The", "")
            for x in tune_names
        ]
        tune_names = "|".join(tune_names)
        item = add_cc_filter.add_control_codes(tune)
        item["tune_name"] = tune_names
        data.append(item)
        tune_count += 1

with open(json_file, "w") as f:
    json.dump(data, f)

print(f"Processed {tune_count} tunes")
