# Contributing

Riichi Engine Protocol is currently a public draft. Compatibility discussions
are welcome before implementations depend on a field or behavior.

Before opening a change:

1. Read `architecture.md` and the shared data contract.
2. Keep host, engine runtime, and model-package responsibilities separate.
3. Use vendor-neutral examples; do not make a model family part of the protocol.
4. Update `CHANGELOG.md` when behavior or compatibility changes.
5. Run `python scripts/check_protocol.py`.

Compatible optional fields raise the protocol minor version. Removing a field,
narrowing valid input, or changing existing semantics requires a new major
version. Editorial corrections do not change the wire version.

By contributing, you agree that your contribution is licensed under the
Apache License 2.0 used by this repository.
