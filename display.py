import sys
import glob
script_tag = '''
<script
    src="https://cdn.jsdelivr.net/combine/npm/tone@14.7.58,npm/@magenta/music@1.23.1/es6/core.js,npm/focus-visible@5,npm/html-midi-player@1.5.0">
</script>
'''

tune = sys.argv[1]
dir = f"results/{tune}"

with open(f"{dir}/{tune}.html", "w") as f:
    f.write(script_tag)
    midis = sorted(list(glob.glob(f'{dir}/*.mid')))
    for filename in midis:
        name = filename.split('/')[-1]
        f.write(f'<h3>{name}</h3>\n<midi-player src="{name}" sound-font></midi-player>\n')


    