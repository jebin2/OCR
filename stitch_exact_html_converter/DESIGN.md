---
name: Sketchbook UI
colors:
  surface: '#f9f9ff'
  surface-dim: '#d8d9e3'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3fd'
  surface-container: '#ecedf7'
  surface-container-high: '#e6e7f2'
  surface-container-highest: '#e1e2ec'
  on-surface: '#191b23'
  on-surface-variant: '#424754'
  inverse-surface: '#2e3038'
  inverse-on-surface: '#eff0fa'
  outline: '#727785'
  outline-variant: '#c2c6d6'
  surface-tint: '#005ac2'
  primary: '#0058be'
  on-primary: '#ffffff'
  primary-container: '#2170e4'
  on-primary-container: '#fefcff'
  inverse-primary: '#adc6ff'
  secondary: '#006c49'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#6b38d4'
  on-tertiary: '#ffffff'
  tertiary-container: '#8455ef'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#f9f9ff'
  on-background: '#191b23'
  surface-variant: '#e1e2ec'
typography:
  headline-lg:
    fontFamily: Patrick Hand, cursive
    fontSize: 36px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Patrick Hand, cursive
    fontSize: 28px
    fontWeight: '600'
    lineHeight: '1.2'
  body-lg:
    fontFamily: Patrick Hand, cursive
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.5'
  body-md:
    fontFamily: Patrick Hand, cursive
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-sm:
    fontFamily: Patrick Hand, cursive
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  gutter: 24px
  margin: 32px
  container-max: 1200px
---

## Brand & Style

The brand personality of this design system is intentionally informal, creative, and human-centric. It is designed to evoke the tactile nostalgia of a physical notebook, stripping away corporate rigidity in favor of a "work-in-progress" aesthetic. The target audience includes students, creators, and professionals who value tools that feel approachable rather than intimidating.

The design style is a hybrid of **Tactile / Skeuomorphic** and **Brutalist** influences. It utilizes physical metaphors—paper textures, pencil grains, and ink bleeds—while maintaining the bold, structural clarity of high-contrast layouts. Every element is treated as if it were hand-sketched on a desk, creating an emotional response that is playful, disarming, and highly imaginative.

## Colors

The palette for the design system is anchored in a vibrant, primary spectrum that mimics the look of high-pigment colored pencils. 
- **Primary Blue (#3B82F6):** Used for main actions and focus states.
- **Secondary Green (#10B981):** Reserved for success states and growth indicators.
- **Tertiary Purple (#8B5CF6):** Used for decorative elements and secondary navigation.
- **Accent Orange & Red:** Utilized for warnings and errors, rendered with a heavy "crayola" texture.

The background is a subtle, off-white paper texture (#F9F8F6), providing a warm, non-glare surface. All colors must be applied with a "scribble" fill effect—where the color density is slightly irregular and does not perfectly meet the border edges—to reinforce the hand-drawn metaphor.

## Typography

Typography in this design system prioritizes a friendly, handwritten feel. While 'beVietnamPro' serves as the technical fallback, the primary visual intent relies on 'Patrick Hand' or 'Gochi Hand' (Google Fonts). The letterforms are slightly irregular, suggesting a human hand at work.

Text should never be pure black; instead, it uses a deep "Graphite" (#374151) to simulate pencil lead. Headings should have a slight 1-2 degree rotation occasionally to mimic natural writing on a page. Line heights are generous to prevent the irregular characters from feeling cluttered.

## Layout & Spacing

The design system uses a **Fluid Grid** model that is constrained by "notebook margins." The layout is organized into 12 columns, but unlike traditional systems, the gutters and margins are visually defined by hand-drawn "ruler lines" or dashed pencil marks.

Spacing follows an 8px rhythm, but elements should rarely be perfectly aligned. A "wobble" factor of 1-3 pixels is encouraged for component placement to maintain the sketchbook feel. Containers should have generous internal padding (minimum 24px) to allow the "scribbled" borders enough room to breathe without clipping content.

## Elevation & Depth

Hierarchy in this design system is achieved through **Tonal Layers** and line weight rather than traditional shadows. 
- **The "Doodle" Depth:** To indicate focus or elevation, elements gain a thicker, darker hand-drawn border (simulating pressing harder with a pencil).
- **Stacking:** Elements that appear "above" others should have a secondary "drop-scribble" (a light gray, textured stroke offset by 4px) instead of a soft Gaussian blur.
- **Layering:** Use "paper-on-paper" effects where a card might have a slightly different paper grain or a subtle "tape" graphic at the corners to show it is "stuck" onto the background.

## Shapes

The shape language is defined by "imperfect geometry." While the base `roundedness` is set to `2` (0.5rem), this is a mathematical baseline only. In practice, every shape must be processed through an SVG displacement map or CSS `clip-path` to create wobbly, non-linear edges.

Corners should never be perfectly symmetrical. Rectangles should look like they were drawn with a quick, single motion where the start and end points of the line might slightly overlap or miss each other (the "over-shoot" effect).

## Components

### Buttons
Buttons are rendered as "filled scribbles." The background color should look like colored pencil shading, with visible white gaps in the grain. Borders are 2px thick with a "rough" texture. On hover, the "shading" density increases.

### Inputs & Text Fields
Inputs are simple, hand-drawn horizontal lines or rough boxes. The focus state is indicated by a "highlight" effect—a transparent yellow or bright blue wash that looks like a marker stroke behind the text.

### Chips & Tags
Chips look like small, torn pieces of paper or circled text. Use a different primary color for each category, rendered as a thin, wobbly outline.

### Icons
All icons must be custom "doodles." They should have varying line weights and look like they were drawn with a 0.5mm felt-tip pen. For example, a "Refresh" icon is a spiral with a small arrowhead at the end, and a "Heart" is a slightly asymmetrical, hand-filled shape.

### Cards
Cards are the primary container and should feature a "rough-cut" edge. They use the primary background color but may feature a subtle grid or lined-paper pattern (light blue or pink horizontal lines) to distinguish them from the main canvas.

### Progress Bars
Progress bars look like a rectangular box filled in with "crayon" as the percentage increases, with the color often bleeding slightly outside the containing box for added whimsy.