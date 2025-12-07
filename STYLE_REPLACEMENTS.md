# Bootstrap Style Replacement Summary

- Navbar background/border: `navbar navbar-expand-lg navbar-dark bg-dark border-bottom border-3 border-warning` (replaces custom black background and orange border)
- Navbar brand color/weight/size: `navbar-brand text-warning fw-bold fs-4` (replaces custom brand color and font sizing)
- Global dark theme: `body` uses `bg-dark text-light` classes (replaces custom body background and text color)
- Cards: `card bg-dark text-white border-secondary` applied across templates (replaces custom dark panel styles)
- Card headers: `bg-dark text-white border-bottom border-secondary` where applicable
- Form controls: `form-control bg-dark text-white border-secondary` for inputs (replaces custom dark input and focus styles)
- Primary action button: `btn btn-warning` (replaces `.btn-naruto` and its hover effects)
- Index logo image: `img-fluid w-25 mx-auto d-block` (replaces `max-width: 300px` inline style)
- Horizontal rule tint: `hr` with `border-secondary` (replaces `border-color: #555` inline style)
- Blog index title accent: `text-warning` on span (replaces inline brand color)
- Blog post content wrapping: `text-wrap` used; note that exact `white-space: pre-wrap` is not available as a Bootstrap utility. If preserving line breaks is required without custom CSS, consider rendering line breaks in content via template filters (e.g., converting `\n` to `<br>`).

All changes modify only `class` attributes and remove custom CSS blocks/inline styles. No structural HTML changes were introduced.
