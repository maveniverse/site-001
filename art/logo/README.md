# Maveniverse logo proposal

An M inside a broken orbit, with one amber piece beside the gap. The M stands for Apache Maven, the orbit for
the universe of tools around it, and the piece for the "missing pieces" of the project's tagline. The piece
returns as the dot of the "i" in the wordmark.

```
svg/maveniverse-icon.svg            rounded icon, 512 x 512
svg/maveniverse-avatar-square.svg   same artwork without rounded corners, for the GitHub avatar
svg/maveniverse-lockup-light.svg    icon and wordmark for light backgrounds
svg/maveniverse-lockup-dark.svg     icon and wordmark for dark backgrounds
png/                                the same four as PNG (1024 px icons, 2x lockups)
```

## Rebuild

```shell
pip install fonttools cairosvg
python build_icon.py     # svg/maveniverse-icon.svg, geometry from the ellipse equation
python build_lockup.py   # the two lockups, wordmark converted to outlines
```

The gap, the tilt and the position of the piece are constants at the top of `build_icon.py`.

The wordmark is Noto Sans (variable, weight 640) in lower case, converted to outlines, so no font is needed to
display it. The path of the font file is set in `build_lockup.py`. Noto Sans is licensed under the SIL Open Font
License 1.1.

The square avatar is the icon with `rx="112"` of the background replaced by `rx="0"`, and the PNGs are rendered
from the SVGs with `cairosvg`.

## Palette

| Name             | Value                  |
|------------------|------------------------|
| Deep space       | `#2B2468` to `#0F1033` |
| Maven cream      | `#FFF7E8`              |
| Orbit teal       | `#3FD0C9`              |
| Orbit periwinkle | `#7B8CFF`              |
| Missing piece    | `#FFB347`              |
| Wordmark ink     | `#1C1B4D`              |
