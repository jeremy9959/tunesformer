import sys

def python_string_to_js_multiline(python_string):
    # Replace Python newline characters with JavaScript newline characters
    js_string = python_string.replace('\n', '\\n')
    # Escape any backticks in the string
    js_string = js_string.replace('`', '\\`')
    # Wrap the string in backticks to create a JavaScript multiline string
    js_multiline_string = '`' + js_string + '`'
    return js_multiline_string

tune = sys.argv[1]

print("<script src='js/abcjs-basic-min.js'></script>")
print(f"<div id='paper'></div>")
with open(tune, "r") as f:
    s = f.read()

js_string = python_string_to_js_multiline(s)

print(f"<script> var tune = {js_string};")

print('ABCJS.renderAbc("paper", tune); </script>')
