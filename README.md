# 34-gcp-reliability-security-governance

A portfolio-grade repository focused on **governance that is testable**: deterministic checks, evidence artifacts, and explicit demo vs production validation.


## The top pains this repo addresses
1) Replacing manual, risky changes with automated delivery—repeatable infrastructure, safe deployments, and drift-free environments (IaC + CI/CD + GitOps).
2) Shipping fast without compromising security—policy-as-code, least privilege, secrets hygiene, and audit-ready evidence collection.
3) Building a data platform people trust—reliable pipelines, clear ownership, data quality checks, and governance that scales without slowing delivery.

## Quick demo (local)
```bash
make demo-offline
make test
```

What you get:
- offline demo pipeline output (no pip installs needed)
- governance guardrails report (`artifacts/governance_guardrails.json`)
- explicit `TEST_MODE=demo|production` tests with safe production gating

## Tests (two explicit modes)

- `TEST_MODE=demo` (default): offline-only checks, deterministic artifacts
- `TEST_MODE=production`: real integrations (requires explicit opt-in + dependencies)

Run demo mode:

```bash
make test-demo
```

Run production mode:

```bash
make test-production
```

## Governance guardrails

Generate evidence:

```bash
python3 tools/governance_guardrails.py --format json --out artifacts/governance_guardrails.json
```

## Sponsorship and contact

Sponsored by:
CloudForgeLabs  
https://cloudforgelabs.ainextstudios.com/  
support@ainextstudios.com

Built by:
Freddy D. Alvarez  
https://www.linkedin.com/in/freddy-daniel-alvarez/

For job opportunities, contact:
it.freddy.alvarez@gmail.com

## License

Personal, educational, and non-commercial use is free. Commercial use requires paid permission.
See `LICENSE` and `COMMERCIAL_LICENSE.md`.
