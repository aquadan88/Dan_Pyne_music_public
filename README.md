# Dan Pyne Music: social graphics

Public assets for @danpynemusic social posts (Facebook and Instagram via Buffer).

- `render.py`: renders gig graphics from a JSON spec (`python3 render.py spec.json out.png`; needs Playwright + Chrome).
- `photos/`: approved photos of Dan.
- `fonts/`: Google Fonts (OFL).
- `graphics/YYYY-MM/`: rendered graphics and their specs. Buffer pulls images from the raw GitHub URLs.
- `style-log.json`: which style and photo were used last, so looks rotate.
- `previews/`: style previews.
