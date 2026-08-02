# Riichi Engine Protocol

Status: public draft v1. Project release: `0.1.0-alpha.1`.

Riichi Engine Protocol defines a vendor-neutral boundary between a Riichi Mahjong
host and independently developed analysis engines. It uses JSON-RPC 2.0 over
JSONL and separates the host application, engine runtime, and model package.

The specification is not tied to Riichi Mahjong Studio or any bundled model.
Hosts start with an empty engine configuration and discover capabilities from
engine manifests and the runtime handshake.

## Reading order

All implementers should read:

1. [Architecture and responsibility boundaries](architecture.md)
2. [Process protocol v1](protocol-v1.md)
3. [Shared data contracts v1](data-contracts-v1.md)
4. [Engine and model package format v1](package-format-v1.md)

Then select one or both business contracts:

- [Decision engine v1](decision-engine-v1.md): `decision.analyze` / `decision-v1`
- [Opponent-analysis engine v1](opponent-analysis-engine-v1.md):
  `opponent.predict` / `opponent-analysis-v1`

Supporting material:

- [Third-party engine developer guide](developer-guide.md)
- [Terminology](docs/terminology.md)
- [Minimal mock decision engine](examples/mock-decision-engine/README.md)
- [Machine-readable schemas](schemas/)

Run `python scripts/check_protocol.py` before submitting a change. The check is
dependency-free and verifies JSON syntax, schema identities, example metadata,
and the mock model digest. Full JSON Schema conformance tests will be added
before the draft is declared stable.

## Normative language

The Chinese specification uses the following requirement levels:

- **必须 / 不得**: required for compatibility.
- **应该 / 不应该**: expected unless an implementation has a documented reason.
- **可以**: optional and, when applicable, declared through capability negotiation.

## Minimal architecture

```text
Host application
  |
Riichi Engine Protocol v1 (JSON-RPC 2.0 over JSONL)
  |
Engine process
  |
Model package (optional)
```

The host owns game rules, legal actions, scheduling, caching, error handling,
and presentation. Engines own model loading, engine-specific options, raw model
semantics, and the interpretation of their declared result schema.

## Draft v1 scope

Draft v1 defines two engine kinds:

- `decision`: scores and recommends legal actions for one seat.
- `opponent-analysis`: predicts declared opponent-analysis fields from the
  visibility mode advertised by the engine.

The current draft targets four-player Riichi Mahjong. Three-player rules,
remote engines, signed engine registries, and cross-machine scheduling are not
required by v1.

| Layer | Identifier | Compatibility boundary |
| --- | --- | --- |
| Process protocol | `riichi-engine-protocol` 1.0 | Lifecycle, transport, status, errors |
| Decision result | `decision-v1` | Candidates, score groups, values, probabilities |
| Opponent result | `opponent-analysis-v1` | Opponent state and tile-risk fields |
| Engine manifest | schema v1 | Entrypoints, capabilities, option schema |
| Model metadata | schema v1 | Model identity, format, input/output schema |

Engine versions and host versions are independent from protocol versions.
Implementations declare compatibility rather than sharing one release number.

## Maintenance policy

- Shared fields are defined only in `data-contracts-v1.md`.
- JSON-RPC lifecycle fields are defined only in `protocol-v1.md`.
- Business-result semantics are defined only in their respective engine specs.
- Optional compatible additions increment the protocol minor version.
- Removing fields, narrowing previously valid input, or changing field meaning
  requires a new protocol major version.
- Engine post-processing changes increment the engine version and fingerprint,
  not the protocol version.

## License

Specification text, schemas, examples, and conformance material in this
repository are licensed under Apache License 2.0. Model weights and third-party
engine implementations retain their own licenses.
