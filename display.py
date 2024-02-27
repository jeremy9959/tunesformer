import sys
import glob

script_tag = """
<script
    src="https://cdn.jsdelivr.net/combine/npm/tone@14.7.58,npm/@magenta/music@1.23.1/es6/core.js,npm/focus-visible@5,npm/html-midi-player@1.5.0">
</script>
"""

tune = sys.argv[1]
dir = f"results/{tune}"

with open(f"{dir}/index.html", "w") as f:
    f.write(script_tag)
    f.write("<h2> Closest Tunes</h2>\n")
    midis = sorted(list(glob.glob(f"{dir}/*.mid")))
    for filename in midis:
        name = filename.split("/")[-1]
        html = name.replace("mid", "html")
        name = name.split(".")[0]
        if name.startswith("tune"):
            index = name.split("_")[2]
            f.write(
                f'<h3><a href={html}>Index: {index}</a></h3>\n<midi-player src="{name}.mid" sound-font></midi-player>\n'
            )
        else:
            f.write(
                f'<h3><a href={html}>Reference: {name}</a></h3>\n<midi-player src="{name}.mid" sound-font></midi-player>\n'
            )
