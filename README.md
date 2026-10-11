# .github

What [github.com/FFD-Labs](https://github.com/FFD-Labs) shows of Fair Food Data.

| File | What it is |
|---|---|
| `profile/README.md` | The text of the page |
| `profile/banner.svg` | Its banner |
| `scripts/banner.py` | Draws the banner from the files of the brand kit |

## The banner

The banner is not edited by hand. The script takes the lockup of the brand kit as it is, turns the two lines of text into outlines and writes `profile/banner.svg`:

```
uv run scripts/banner.py <lockup svg> <Host Grotesk woff2> <Spline Sans Mono woff2>
```

The lockup and the two typefaces are kept with the brand, not here. With the animated lockup the mark runs its loop, and stays still for a visitor who asks for reduced motion. With the still one the banner does not move.

## The name and the mark

The name Fair Food Data and its mark identify us. Use them to refer to Fair Food Data, without changes.
