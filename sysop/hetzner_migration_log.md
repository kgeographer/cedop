# Hetzner Migration Log

**Goal**: Migrate CEDOP (and co-hosted apps) from DigitalOcean droplet to Hetzner VM
**Driver**: Cost reduction + Pitt handoff readiness
**Start date**: 2026-04-05

---

## Current DO Droplet

| Item | Value |
|------|-------|
| Plan | 2 GB RAM, 50 GB disk |
| OS | Ubuntu (old — confirm exact version) |
| Monthly cost | $13.39 |
| Apps hosted | cedop.kgeographer.org (primary), others TBD |
| DNS | Namecheap — kgeographer.org / kgeographer.com |

---

## ✓ MIGRATION COMPLETE — 2026-04-05
cedop.kgeographer.org live on Hetzner CPX32, Nuremberg. All features verified faster than DO droplet.
Remaining: glos/linkedpaths migration, DO droplet cancellation.

---

## Phase 0 — Provisioning Decisions

*To be filled in as decisions are made.*

### VM choice
- [ ] Select Hetzner plan
- [ ] Select datacenter region
- [ ] Select OS

### Networking
- [ ] Static/floating IP or standard
- [ ] IPv6 only or dual-stack
- [ ] Firewall rules

---

## Phase 1 — New VM Setup

- [ ] Provision VM
- [ ] Initial hardening (SSH keys, ufw, fail2ban)
- [ ] Install stack: Apache2, Python 3.x, PostgreSQL + PostGIS
- [ ] Virtualenv + pip install requirements
- [ ] Clone repo, configure .env
- [ ] Gunicorn systemd service
- [ ] Apache vhost + SSL (certbot)
- [ ] Smoke test: health endpoint

---

## Phase 2 — Database Migration

- [ ] pg_dump on DO
- [ ] Transfer dump to Hetzner
- [ ] pg_restore + verify row counts
- [ ] Test signature endpoint

---

## Phase 3 — DNS Cutover

- [ ] Point DNS to Hetzner IP (low TTL first)
- [ ] Verify SSL auto-renewal
- [ ] Monitor for 48h

---

## Phase 4 — DO Cleanup

- [ ] Migrate / sunset other DO-hosted apps
- [ ] Cancel DO droplet

---

## Action Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-04-05 | Migration planning started | sysop/ folder created |
| 2026-04-05 | VM provisioned | CPX32, Nuremberg (NBG1), Ubuntu 24.04, IP: 46.225.125.25 |
| 2026-04-05 | SSH access confirmed | karlg user created, sudo group, key auth working (id_rsa_2023) |
| 2026-04-05 | ~/.ssh/config entry added | Host kgeographer-1 → 46.225.125.25 as karlg |
| 2026-04-05 | Stack installed | Nginx, Python 3.12, PostgreSQL 17 (pgdg), PostGIS 3, certbot |
| 2026-04-05 | DB restored | pg_dump from droplet piped to Hetzner; 190,675 basins confirmed |
| 2026-04-05 | App running | gunicorn + uvicorn worker on 127.0.0.1:8001, systemd service enabled |
| 2026-04-05 | Nginx configured | Reverse proxy vhost for cedop.kgeographer.org |
| 2026-04-05 | DNS cutover | cedop A record → 46.225.125.25 (Namecheap) |
| 2026-04-05 | SSL live | certbot --nginx, auto-renewal configured |
| 2026-04-05 | glos migrated | Flask app, glos DB restored, gunicorn service, nginx vhost, SSL live |
| 2026-04-05 | linkedpaths migrated | Static _site/ rsynced, nginx vhost, DNS updated |

