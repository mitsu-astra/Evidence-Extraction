# Halide Theme Design System Reference

## 🎨 Color Palette

### Primary Colors
```
Background:  #0a0a0a     rgb(10, 10, 10)      [Deep Black]
Silver:      #e0e0e0     rgb(224, 224, 224)   [Light Silver]
Accent:      #ff3c00     rgb(255, 60, 0)      [Bright Orange]
```

### Derived Colors
```
Semi-transparent accent:  rgba(255, 60, 0, 0.3)
Text opacity 60%:         rgba(224, 224, 224, 0.6)
Text opacity 40%:         rgba(224, 224, 224, 0.4)
Subtle border:            rgba(255, 60, 0, 0.2)
```

## 🔤 Typography System

### Font Stack
```css
Primary:   'Courier Prime', 'Courier New', monospace    [Body text]
Headers:   'Syncopate', 'Courier Prime', monospace      [Titles]
Fallback:  monospace                                      [System fonts]
```

### Font Sizes & Weights
```
hero-title:     clamp(3rem, 10vw, 10rem)  | weight: 700
section-header: 2.5rem                    | weight: 700
h1:             2rem                      | weight: 700
h2:             1.5rem                    | weight: 700
body:           1rem                      | weight: 400
small:          0.875rem                  | weight: 400
micro:          0.75rem                   | weight: 400
```

### Letter Spacing
```
hero-title:     -0.04em
headers:        0.05em
normal text:    0.02em
labels:         0.1em
monospace:      0.05em
```

## ✨ Component Styles

### Navbar
```
Background:     rgba(10, 10, 10, 0.85)
Backdrop:       blur(10px)
Border:         1px solid rgba(255, 60, 0, 0.2)
Height:         80px (with padding)
Position:       fixed top-0
Z-Index:        50
```

### Links in Navbar
```
Default:        #e0e0e0
Hover:          #ff3c00 with text-shadow
Active:         #ff3c00 with animation
Underline:      2px #ff3c00 (animated)
Animation:      0.3s cubic-bezier(0.16, 1, 0.3, 1)
```

### Buttons
```
Border:         1px solid #ff3c00
Background:     transparent → rgba(255, 60, 0, 0.1) on hover
Color:          #ff3c00
Padding:        0.5rem 1.2rem
Border-radius:  4px
Clip-path:      polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px))
Box-shadow:     0 0 20px rgba(255, 60, 0, 0.5) on hover
Transform:      translateY(-2px) on hover
```

### Input Fields
```
Background:     rgba(224, 224, 224, 0.03)
Border:         1px solid rgba(255, 60, 0, 0.2)
Color:          #e0e0e0
Focus:
  Border:       rgba(255, 60, 0, 1)
  Background:   rgba(255, 60, 0, 0.05)
  Box-shadow:   0 0 10px rgba(255, 60, 0, 0.3), inset 0 0 10px rgba(255, 60, 0, 0.1)
```

### Cards
```
Background:     rgba(10, 10, 10, 0.8)
Border:         1px solid rgba(255, 60, 0, 0.3)
Backdrop:       blur(10px)
Hover Border:   rgba(255, 60, 0, 0.6)
Hover Shadow:   0 0 20px rgba(255, 60, 0, 0.3)
```

## 🎬 Animations

### Timing Functions
```
Default:        0.3s ease
Smooth:         0.3s cubic-bezier(0.16, 1, 0.3, 1)
Landing Page:   2.5s cubic-bezier(0.16, 1, 0.3, 1)
Flow Animation: 2s infinite ease-in-out
```

### Animation - Slide In
```
From:   opacity: 0; transform: translateY(-10px);
To:     opacity: 1; transform: translateY(0);
Time:   0.6s cubic-bezier(0.16, 1, 0.3, 1);
```

### Animation - Glow
```
0%, 100%:  box-shadow: 0 0 10px rgba(255, 60, 0, 0.3);
50%:       box-shadow: 0 0 20px rgba(255, 60, 0, 0.6);
```

### Animation - Scanline
```
0%, 100%:  text-shadow: 0 0 10px rgba(255, 60, 0, 0.5);
50%:       text-shadow: 0 0 20px rgba(255, 60, 0, 0.8);
Time:      1.5s ease-in-out infinite;
```

### Animation - Flow (Scroll Hint)
```
0%, 100%:  transform: scaleY(0); transform-origin: top;
50%:       transform: scaleY(1); transform-origin: top;
51%:       transform: scaleY(1); transform-origin: bottom;
Time:      2s infinite ease-in-out;
```

## 📐 Spacing System

### Standard Spacing
```
xs:  0.25rem (4px)
sm:  0.5rem  (8px)
md:  1rem    (16px)
lg:  1.5rem  (24px)
xl:  2rem    (32px)
2xl: 3rem    (48px)
3xl: 4rem    (64px)
```

### Component-Specific
```
navbar padding:     1.5rem vertical, 2rem horizontal
card padding:       2rem
section padding:    4rem + 2rem
gap between items:  1rem - 1.5rem
```

## 🌐 Layout Grid

### Navbar Layout
```
[Logo + Branding] --- [Navigation Links] --- [Exit Button]
```

### Landing Page Layout
```
[Title Area]
[3D Canvas]
[Interface Grid with CTA]
[Scroll Hint]
```

### Analysis Section Layout
```
[Navbar - fixed]
[Section Header]
[Content Area]
[Accent Line]
[Next Section]
```

## 🎯 Responsive Breakpoints

```
Mobile:   < 640px
Tablet:   640px - 1024px
Desktop:  > 1024px
Large:    > 1280px
XL:       > 1536px
```

### Responsive Rules
- Hero title uses `clamp()` for fluid sizing
- Navbar collapses on mobile (implement as needed)
- Content wraps at `max-w-7xl` (80rem)
- Padding adjusts with breakpoints

## 🔆 Visual Effects

### Glow Effects
```
Subtle:    box-shadow: 0 0 10px rgba(255, 60, 0, 0.3);
Medium:    box-shadow: 0 0 20px rgba(255, 60, 0, 0.5);
Strong:    box-shadow: 0 0 30px rgba(255, 60, 0, 0.8);
```

### Text Effects
```
Glow:      text-shadow: 0 0 10px rgba(255, 60, 0, 0.5);
Scan:      text-shadow: 0 0 20px rgba(255, 60, 0, 0.8);
Blur:      text-shadow: 0 0 20px rgba(255, 60, 0, 0.3);
```

### Blur Effects
```
Light:     backdrop-filter: blur(5px);
Medium:    backdrop-filter: blur(10px);
Heavy:     backdrop-filter: blur(20px);
```

## 🖼️ Grain Texture

### Implementation
```css
opacity: 0.1 - 0.15
pattern: fractal noise (SVG filter)
frequency: 0.65
octaves: 3
```

### Result Effect
- Adds analog, CRT-monitor feel
- Reduces harsh edges
- Creates depth and texture
- Authenticity to the halide aesthetic

## 📱 Icon Styling

### Current Icons
```
Logo Diamond:       ◆ (rotated square)
Home/Exit:          ✕ (close/exit symbol)
Navigation Prefix:  [ (bracket)
Navigation Suffix:  ] (bracket)
```

### Style
```
Color:              #ff3c00 (accent)
Font:               Monospace
Size:               Inherited from parent
Opacity:            Full or 0.5 (dimmed)
```

## 🎨 Usage Examples

### Creating a Halide Button
```tsx
<button
  className="border-2 border-accent hover:border-silver"
  style={{
    background: 'transparent',
    color: '#ff3c00',
    padding: '0.5rem 1rem',
    fontFamily: "'Courier Prime', monospace",
    cursor: 'pointer',
    transition: 'all 0.3s ease',
  }}
  onMouseEnter={(e) => {
    e.currentTarget.style.boxShadow = '0 0 15px rgba(255, 60, 0, 0.5)';
  }}
  onMouseLeave={(e) => {
    e.currentTarget.style.boxShadow = 'none';
  }}
>
  [ BUTTON ]
</button>
```

### Creating a Halide Card
```tsx
<div
  style={{
    background: 'rgba(10, 10, 10, 0.8)',
    border: '1px solid rgba(255, 60, 0, 0.3)',
    backdropFilter: 'blur(10px)',
    padding: '2rem',
    borderRadius: '4px',
    transition: 'all 0.3s ease',
  }}
  onMouseEnter={(e) => {
    e.currentTarget.style.borderColor = 'rgba(255, 60, 0, 0.6)';
    e.currentTarget.style.boxShadow = '0 0 20px rgba(255, 60, 0, 0.3)';
  }}
  onMouseLeave={(e) => {
    e.currentTarget.style.borderColor = 'rgba(255, 60, 0, 0.3)';
    e.currentTarget.style.boxShadow = 'none';
  }}
>
  {/* Content */}
</div>
```

## 🔧 CSS Custom Properties

### Available in CSS
```css
:root {
  --bg: #0a0a0a;
  --silver: #e0e0e0;
  --accent: #ff3c00;
  --grain-opacity: 0.1;
}

/* Usage */
color: var(--silver);
background: var(--bg);
border-color: var(--accent);
```

## 💾 Asset Requirements

### Images (Currently using Unsplash)
- Layer 1: Landscape/landscape photography
- Layer 2: Seascape/nature photography
- Layer 3: Landscape/landscape photography
- All are grayscale-filtered and darkened

### Custom Assets to Consider
- Team logo in SVG
- Custom icon set
- Pattern textures
- Animated backgrounds

---

**This design system ensures consistency across all components while maintaining the cool, futuristic halide aesthetic.**
