# Security Policy

An engine is a local executable program. Protocol compatibility does not make
an engine trusted, so only install engines from sources you trust.

Please do not disclose security vulnerabilities or exploit details in a public
issue. For sensitive reports, contact the repository owner through their GitHub
profile and request a confidential contact method without including the details
in the first message.

Host implementations should validate message sizes and schemas, avoid shell
command construction, enforce timeouts, and treat engine-provided text as
untrusted.
