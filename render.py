import sys
import glob

abcjs_cdn = "https://cdnjs.cloudflare.com/ajax/libs/abcjs/6.3.0/abcjs-basic-min.min.js"


def python_string_to_js_multiline(python_string):
    # Replace Python newline characters with JavaScript newline characters
    js_string = python_string.replace("\n", "\\n")
    # Escape any backticks in the string
    js_string = js_string.replace("`", "\\`")
    # Wrap the string in backticks to create a JavaScript multiline string
    js_multiline_string = "`" + js_string + "`"
    return js_multiline_string


def render_abc_html(filename, abc):
    js_string = python_string_to_js_multiline(abc)
    with open(filename, "w") as f:
        f.write(f"<script src={abcjs_cdn}></script>\n")
        f.write(f"<div id='paper'></div>\n")
        f.write(f"<script> var tune = {js_string};\n")
        f.write('ABCJS.renderAbc("paper", tune); </script>\n')


tune = sys.argv[1]
dir = f"results/{tune}"

for file in glob.glob(f"{dir}/*.abc"):
    with open(file) as f:
        abc = f.read()
        html = file.replace("abc", "html")
        render_abc_html(f"{html}", abc)
