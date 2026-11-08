# Humation avatar assets

EDUTURNOS bundles the official `@humation/core` renderer and
`@humation/assets-humation-1` parts for its Flask templates. The generated
browser bundle uses the package's real selection slots and color channels and
does not call an external avatar service.

The shadcn AvatarBuilder block targets React; EDUTURNOS is server-rendered
Flask, so the existing dialog is retained and populated from Humation's
official APIs instead of adding a second frontend framework.

Run `npm install --prefix tools/humation` and
`npm run --prefix tools/humation build` to regenerate the bundle and the
server-side allowlist. Humation's MIT license is included in
`static/vendor/HUMATION-LICENSE.md`.
