# Evidence Packs

Autonomous lifecycle decisions are strongest when findings are stored as evidence packs instead of loose text files.

## Pack Layout

Store each candidate under `findings/<target>/<pack-name>/`.

Recommended files:

- `request.http` - exact request that triggers the issue
- `response.http` or `response.json` - exact response proving the issue
- `scope.txt` or `scope.json` - why the asset is in scope
- `victim.txt` - the victim/object proof or affected identifier
- `negative_control.txt` - expected-safe comparison or denied request
- `impact.txt` - concrete impact statement
- `metadata.json` - optional structured fields like `bug_class`, `endpoint`, `severity_guess`

## Example

```text
findings/example.com/idor-invoice-read/
  request.http
  response.json
  scope.txt
  victim.txt
  negative_control.txt
  impact.txt
  metadata.json
```

Example `metadata.json`:

```json
{
  "bug_class": "idor",
  "endpoint": "/api/invoices/42",
  "severity_guess": "high"
}
```

## Lifecycle Behavior

`core/lifecycle.py` scores actual packs instead of category names alone.

- missing any required proof for the bug class -> `KILL`
- strong classes can pass only when their required proof is complete
- noisy classes stay fail-closed unless impact and control evidence are present
- chain-prone classes without impact -> `CHAIN REQUIRED`

That means the autonomous layer is now judging proof quality, not just file names.
