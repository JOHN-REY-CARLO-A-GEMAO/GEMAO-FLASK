# Design System: Layout Changes

## User Interfaces
- Audio control panel (`#audio-panel`) removed entirely from `base.html`.
- No residual UI indicators remain for audio controls on user pages.
- Keep interfaces clean; avoid adding floating utility panels on user routes.

## Admin Interfaces
- Admin navigation uses a left sidebar on `md+` and an offcanvas menu on small screens.
- Audio controls live only in `MyFlaskapp/templates/admin/settings.html`.
- Do not render floating audio controls elsewhere.

## Accessibility
- Offcanvas trigger includes `aria-controls` and close button uses `aria-label`.
- Audio controls include explicit labels and `aria-live` for status when applicable.

## Responsive Behavior
- Sidebar hidden on small screens (`d-none d-md-block`); offcanvas provides access.
- Audio settings page uses range inputs that scale across device sizes.

## Implementation Notes
- `base.html` no longer contains `#audio-panel`; related JS guards for missing elements.
- Admin layout updated in `MyFlaskapp/templates/admin/base.html` to add offcanvas.
