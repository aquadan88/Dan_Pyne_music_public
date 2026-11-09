# Dan Pyne Music: social graphics

Public assets for @danpynemusic social posts (Facebook and Instagram via Buffer).

- `render.py`: renders gig graphics from a JSON spec (`python3 render.py spec.json out.png`; needs Playwright + Chrome). See its docstring for styles and spec format.
- `photos/`: approved photos of Dan. `cutouts/`: the same photos with the background removed (`python3 render.py --cutout <stem>`, needs rembg).
- `fonts/`: Google Fonts (OFL).
- `graphics/YYYY-MM/`: rendered graphics and their specs. Buffer pulls images from the raw GitHub URLs, so never delete or overwrite a file a draft uses; use a new file name.
- `style-log.json`: style list and which style/photo were used last, so looks rotate.
- `previews/`: one preview per style.
