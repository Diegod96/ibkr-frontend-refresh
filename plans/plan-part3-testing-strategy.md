# IBKR Frontend Refresh - Part 3: Testing Strategy

Comprehensive testing approach for quality assurance.

---

## Unit Testing

| Layer | Framework | Coverage Target |
|-------|-----------|-----------------|
| Frontend | Jest + React Testing Library | 80% |
| Backend | pytest | 90% |
| Database | pytest + fixtures | 85% |

**Key areas to test:**
- Weight calculation and validation (must sum to 100%)
- Allocation distribution algorithms
- Trigger condition evaluation
- Order generation logic

---

## Integration Testing

| Type | Tools | Description |
|------|-------|-------------|
| API Integration | pytest + httpx | Test FastAPI endpoints end-to-end |
| Database | pytest + testcontainers | Test PostgreSQL operations with real DB |
| Frontend-Backend | Cypress | Test full user flows |

---

## End-to-End Testing

| Tool | Purpose |
|------|---------|
| Cypress | Critical user journeys (create portfolio, deposit, trigger execution) |
| Playwright | Cross-browser testing |

**Critical E2E Scenarios:**
1. User creates account and connects IBKR
2. User creates portfolio with multiple pies and slices
3. User makes deposit with auto-invest enabled
4. Position building triggers fire and execute correctly
5. Portfolio rebalancing workflow

---

## IBKR API Testing

| Environment | Purpose |
|-------------|---------|
| Paper Trading Account | All development and testing |
| Sandbox/Mock Server | Unit tests with mocked responses |

> ⚠️ **Important:** Never test with real money accounts during development.

---

## Performance Testing

| Tool | Metric |
|------|--------|
| Locust | API response times under load |
| Lighthouse | Frontend performance scores |

**Targets:**
| Metric | Target |
|--------|--------|
| API response time (p95) | < 200ms |
| Frontend LCP | < 2.5s |
| Frontend FID | < 100ms |

---

## Security Testing

- [ ] OWASP ZAP scan for vulnerabilities
- [ ] Dependency audit (npm audit, pip-audit)
- [ ] Authentication flow penetration testing
- [ ] Encrypted credential storage verification

---

## Test Coverage by Feature

### Portfolio Pie/Slice Structure
| Test Type | Coverage Areas |
|-----------|----------------|
| Unit | Weight validation, slice calculations, pie aggregation |
| Integration | CRUD operations, database constraints |
| E2E | Create portfolio flow, edit pie/slice, rebalance |

### Auto-Invest Deposits
| Test Type | Coverage Areas |
|-----------|----------------|
| Unit | Allocation algorithm, rounding logic, edge cases |
| Integration | Deposit detection, order generation |
| E2E | Full deposit-to-allocation flow |

### Position Building
| Test Type | Coverage Areas |
|-----------|----------------|
| Unit | Trigger evaluation, indicator calculations |
| Integration | Trigger monitoring, execution engine |
| E2E | Trigger fires and executes purchase |

---

## Related Documents

- [Part 1: Overview & Features](./plan-part1-overview.md)
- [Part 2: Development Phases](./plan-part2-development-phases.md)
- [Part 4: Git Strategy](./plan-part4-git-strategy.md)