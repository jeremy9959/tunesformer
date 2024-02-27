import sys

tune = sys.argv[1]

print("<script src='./abcjs-basic-min.js'></script>")
print(f"<div id='paper'></div>")
with open(tune, "r") as f:
    s = f.read()
lines = s.split("\n")

s = "\\ \n".join(lines)

print('<script> var tune = "\\')
print(s + '";')
print('ABCJS.renderAbc("paper", tune); </script>')
