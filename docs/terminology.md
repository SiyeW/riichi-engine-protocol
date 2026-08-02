# Terminology

The protocol uses the following English terms consistently:

Game and rule-system prose uses `Riichi Mahjong`. Geographic qualifiers are
not used for the game. Language names and locale identifiers remain valid when
they identify a translation or software-localization boundary.

| Term | Meaning |
| --- | --- |
| host | Application that owns game rules, scheduling, configuration, and UI |
| engine | Executable implementation of one or more protocol engine kinds |
| decision engine | Engine that scores legal action candidates |
| opponent-analysis engine | Engine that predicts declared opponent fields |
| model package | Passive model files and metadata consumed by an engine |
| engine configuration | User-editable reference to an engine and model package |
| session | Isolated incremental analysis context |
| task | One request with a request identifier |

“Opponent analysis” is preferred to “opponent state” because the result can
contain risk estimates and derived probabilities rather than one literal state.
“Game service” is preferred to “environment service” in host implementations;
the latter is easily confused with reinforcement-learning environments.

Product names and model-family names may appear in implementation documentation
or provenance notices, but must not define protocol behavior.
