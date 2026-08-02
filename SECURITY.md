# Security Policy

This draft describes communication with local executable programs. Installing
an engine has the same security implications as running any other local
program; protocol compatibility is not a trust or safety guarantee.

Do not include access tokens, private game records, model files, personal paths,
or exploit details in a public issue. Until a private reporting address is
published, retain sensitive reports locally and open a minimal public issue
requesting a private contact channel.

The draft does not promise operating-system sandboxing. Hosts should validate
message sizes and schemas, avoid shell command construction, limit buffered
diagnostics, enforce timeouts, and treat engine-provided text as untrusted.
