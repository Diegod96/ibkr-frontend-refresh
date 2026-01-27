# IBKR Frontend Refresh - Part 1: Overview & Features

A UI wrapper for Interactive Brokers that adds modern portfolio management features to enhance the user experience.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)

---

## Overview

This project creates a modern frontend wrapper for Interactive Brokers, adding:
- Portfolio pie/slice organization (similar to M1 Finance)
- Auto-invest deposit allocation
- Position building with configurable triggers

---

## Features

### Feature #1: Portfolio Pie/Slice Structure

Organize portfolios using a pie-and-slice format.

| Concept | Description |
|---------|-------------|
| **Pie** | A themed grouping of assets (e.g., "Semiconductors" containing NVDA, TSM, ASML) |
| **Slice** | An individual holding within a pie |
| **Rules** | Slices within a pie must sum to 100%; applies to stocks and ETFs only |

**Example Portfolio (Roth IRA):**

| Pie | Weight | Slices |
|-----|--------|--------|
| Semiconductors | 25% | NVDA (40%), TSM (35%), ASML (25%) |
| Big Tech | 25% | AAPL (50%), MSFT (50%) |
| Financials | 25% | JPM (50%), V (30%), MA (20%) |
| Healthcare | 25% | UNH (40%), JNJ (30%), LLY (30%) |

### Feature #2: Auto-Invest Deposits

Automatically allocate deposits across pies and slices based on target weights.

**Behavior:**
1. User deposits cash into account
2. User toggles auto-invest on or off
3. If enabled, cash is distributed proportionally by pie weight, then slice weight

### Feature #3: Position Building

Control how slices are purchased—immediately or gradually over time.

| Position Type | Description |
|---------------|-------------|
| **Full Position** | Buy entire allocation immediately when funds are available |
| **Build Position** | Spread purchases over time based on configurable triggers |

**Trigger Types:**
- Time-based (regular intervals)
- Price-based (pullbacks or breakouts)
- Technical signals (moving averages, RSI, volume, Bollinger Bands)
- Fundamental triggers (earnings, catalysts, valuation levels)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js + TypeScript |
| Backend | Python + FastAPI |
| Database | PostgreSQL (Supabase) |
| Auth | Supabase Auth or Auth0 |
| Broker API | IBKR Web API (primary), TWS API (advanced features) |
| Hosting | Vercel (frontend), Railway/Render (backend) |

---

## Related Documents

- [Part 2: Development Phases](./plan-part2-development-phases.md)
- [Part 3: Testing Strategy](./plan-part3-testing-strategy.md)
- [Part 4: Git Strategy](./plan-part4-git-strategy.md)