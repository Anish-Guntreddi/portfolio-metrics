"""
Engineering portfolio — interactive metrics dashboard.

Ten projects: five full-stack apps + five systems-programming (C/C++) projects.
Run locally:   streamlit run streamlit_app.py
Deploy free:   push to a public GitHub repo, then https://share.streamlit.io
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

IMG_DIR = Path(__file__).parent / "img"

# --------------------------------------------------------------------------- #
# Project data (real metrics from the build: test counts, benchmarks)
# --------------------------------------------------------------------------- #
PROJECTS: list[dict] = [
    # ---------- Full-stack applications ----------
    {
        "name": "WorkflowOps", "domain": "Full-stack", "lang": "Python · TS",
        "stack": ["FastAPI", "Postgres", "Redis", "React/TS"],
        "tests": 94, "throughput": None, "headline": "RBAC + Redis workers",
        "tagline": "Enterprise workflow automation — build, run, and monitor business workflows.",
        "description": (
            "A SaaS platform to create, run, and monitor business workflows (onboarding, leave/expense "
            "approvals). Workflows are ordered steps with conditions that invoke mock integrations "
            "(Slack/email/Sheets) through one swappable adapter interface. A background worker walks each "
            "run step-by-step through a state machine, with retries, and the dashboard reflects the engine's "
            "authoritative state in real time."
        ),
        "architecture": [
            "Run/step state machine: pending → running → succeeded/failed, with bounded retries and append-only attempts",
            "Redis-backed background workers; the engine is the single source of truth for run state",
            "One Adapter protocol with swappable mock adapters (Slack/email/Sheets + a deliberately-failing one)",
            "Server-side RBAC (admin/editor/viewer) enforced on every route; JWT role re-read from the DB each request",
        ],
        "highlight": "Eval-free condition evaluator + parameterized SQL — zero injection surface; RBAC matrix proven by 22 tests.",
        "security": "Broken-access-control hardened: a viewer can't trigger/edit; user A can't read user B's run logs (403).",
    },
    {
        "name": "QueueForge", "domain": "Full-stack", "lang": "Python · TS",
        "stack": ["FastAPI", "Redis", "React/TS"],
        "tests": 77, "throughput": None, "headline": "DLQ + visibility timeout",
        "tagline": "Distributed job queue + worker dashboard — reliability is the product.",
        "description": (
            "Submit background jobs (CSV processing, report generation, webhook delivery); workers process them "
            "asynchronously while a dashboard tracks status live. The reliability surface — retries with backoff, "
            "a dead-letter queue, scheduling, priority, and worker heartbeats — is the whole point."
        ),
        "architecture": [
            "Job state machine queued → running → succeeded/failed; poison messages route to a DLQ at max attempts",
            "Redis-backed queue + worker pool with heartbeats and a visibility timeout: a dead worker's in-flight job is requeued",
            "Atomic claim via a Lua ZPOPMIN→ZADD (with a documented atomic fallback) — no check-then-act race",
            "Scheduler promotes run_at≤now jobs; priority ordering honored",
        ],
        "highlight": "Dead-worker requeue is tested end-to-end: lease expiry → mark_failed → retry-with-backoff → DLQ.",
        "security": "Webhook SSRF guard (live-probed: IPv6 loopback, DNS-rebind, metadata IP all blocked); bounded payloads.",
    },
    {
        "name": "DevGate", "domain": "Full-stack", "lang": "Python · TS",
        "stack": ["FastAPI", "Postgres", "Redis", "SDK"],
        "tests": 55, "throughput": None, "headline": "Hashed keys + rate limit",
        "tagline": "API-key management & developer platform, with a Python SDK.",
        "description": (
            "Register APIs, generate/revoke API keys, enforce per-key rate limits, and view usage analytics "
            "(request counts, error rate, p50/p95 latency). A gateway endpoint authenticates the key, enforces "
            "limits, records usage, and a small Python SDK wraps it with typed errors."
        ),
        "architecture": [
            "Keys returned in plaintext exactly once; only a SHA-256 hash + masked prefix is persisted",
            "Constant-time verification (hmac.compare_digest); key accepted in the header only, never the URL",
            "Per-key rate limit via a single atomic Redis Lua script (INCR + conditional EXPIRE)",
            "Ownership scoped server-side; non-owners get 404 (no existence leak)",
        ],
        "highlight": "Verified live in the browser: a generated key authenticates at the gateway (200); missing/garbage/query-string keys → 401.",
        "security": "Secrets hashed at rest, shown once, revocation effective immediately, no rate-limit bypass.",
    },
    {
        "name": "CollabBoard", "domain": "Full-stack", "lang": "Python · TS",
        "stack": ["FastAPI", "WebSockets", "Postgres", "React/TS"],
        "tests": 75, "throughput": None, "headline": "Per-board WS authz",
        "tagline": "Real-time collaborative workspace — boards, tasks, presence, live editing.",
        "description": (
            "A team workspace with boards, tasks, threaded comments, and a shared doc that update in real time "
            "over WebSockets, including live presence. A connection manager broadcasts events to the right board "
            "subscribers; concurrent edits are version-checked."
        ),
        "architecture": [
            "WebSocket connection authenticated AND authorized per board BEFORE accept(), with per-message re-auth",
            "Removing a member force-closes their live sockets; an outsider can't subscribe or receive events",
            "REST authz on every route via a single require_board_access (returns 404, not 403, to avoid leaks)",
            "Concurrent edits resolved with optimistic version checks (409 on conflict)",
        ],
        "highlight": "The hard part — authorizing a WS connection before the handshake completes — is done right and proven by 7 tests.",
        "security": "Real-time auth: token-checked at connect, re-checked per frame; cross-team reads/writes blocked.",
    },
    {
        "name": "Ledgerly", "domain": "Full-stack", "lang": "Python · TS",
        "stack": ["FastAPI", "Postgres", "React/TS"],
        "tests": 113, "throughput": None, "headline": "CSV import, injection-safe",
        "tagline": "Small-business bookkeeping — CSV import, categorization, invoices, reports.",
        "description": (
            "Upload CSV bank transactions, categorize expenses with priority-ordered rules, track invoices, and "
            "view monthly revenue/expense reports with safe exports. Money is stored as integer cents; every read "
            "and write is scoped to the owner's org."
        ),
        "architecture": [
            "Bounded streaming CSV parse (size cap, header/shape validation) with a smart column auto-mapper",
            "Priority-ordered categorization rules with an 'uncategorized' fallback",
            "CSV formula-injection neutralized on export (leading =,+,-,@ prefixed with a quote)",
            "Strict per-org isolation: org_id always derived from the JWT principal, never client input",
        ],
        "highlight": "Verified live: an exported `=cmd|calc` cell becomes `'=cmd|calc`; cross-org access returns 404.",
        "security": "Upload safety + spreadsheet formula-injection defense + strict per-org data isolation.",
    },
    # ---------- Systems programming ----------
    {
        "name": "MicroMatch", "domain": "Systems", "lang": "C++17", "flagship": True,
        "stack": ["C++17", "price-time FIFO"],
        "tests": 45, "throughput": 11_300_000, "throughput_unit": "ops/sec",
        "latency_ns": 42, "headline": "~11.3M ops/s · p50 42ns",
        "tagline": "Limit order book & matching engine simulating an exchange.",
        "description": (
            "An in-process matching engine with strict price-time priority: limit and market orders, cancels, "
            "modifies, partial fills across multiple levels, trade reports, best bid/offer, market depth, and "
            "event replay. Built for correctness first, then latency."
        ),
        "architecture": [
            "Two-sided book: std::map per side (bids desc / asks asc), each price level a FIFO preserving time priority",
            "std::unordered_map<order_id, location> for O(1) cancel/modify",
            "Aggressive orders sweep the opposite book best-first at the maker's price; remainder posts (limit) or drops (market)",
            "Deterministic, byte-stable replay from a command file",
        ],
        "highlight": "~11.3M ops/sec, mean 88.5 ns/op, p50 42 ns. Price-time priority verified adversarially; ASan + UBSan clean.",
        "security": "In-process simulator — no network surface; the bar is correctness, not threat model.",
    },
    {
        "name": "ThreadServe", "domain": "Systems", "lang": "C++17",
        "stack": ["C++17", "POSIX sockets"],
        "tests": 66, "throughput": 38_000, "throughput_unit": "req/sec",
        "headline": "~38k req/s · traversal-hardened",
        "tagline": "Multithreaded HTTP/1.1 server from scratch over raw TCP.",
        "description": (
            "A from-scratch HTTP/1.1 server: an accept loop dispatches connections to a fixed worker thread pool "
            "via a bounded thread-safe queue. It parses untrusted requests safely, serves static files with "
            "path-traversal defense, and shuts down gracefully."
        ),
        "architecture": [
            "Accept loop → bounded blocking queue (mutex + condvar) → N worker threads",
            "Hardened parser: every read bounded; rejects bare-LF injection, NUL, Content-Length smuggling, oversized input",
            "Static serving with realpath canonicalization + symlink-escape check (defense in depth)",
            "Async-signal-safe graceful shutdown via a self-pipe; workers joined, RAII fds (no double-close/leak)",
        ],
        "highlight": "Adversarial probes (encoded traversal, smuggling, symlink-to-/etc/passwd) all rejected; ASan + UBSan clean; ~38k req/s.",
        "security": "Parses untrusted network input — bounded everywhere, traversal-proof, race-free under concurrency.",
    },
    {
        "name": "MiniCache", "domain": "Systems", "lang": "C++17",
        "stack": ["C++17", "RESP protocol"],
        "tests": 69, "throughput": 1_840_000, "throughput_unit": "GET/sec",
        "headline": "~1.8M GET/s · TTL/LRU/AOF",
        "tagline": "Redis-inspired in-memory key-value store.",
        "description": (
            "A KV store with a RESP-like TCP protocol: SET/GET/DEL/EXPIRE/TTL/INCR/LPUSH/LRANGE, plus lazy + "
            "active TTL expiry, LRU eviction under a cap, append-only-file persistence with replay, and snapshots."
        ),
        "architecture": [
            "Tagged-union values (string | list) in a hash map; parallel expiry map; intrusive LRU recency list",
            "Bounded RESP parser (every length checked before allocation); binary-safe payloads",
            "AOF append on writes + replay on startup; full-store snapshot dump/load with bounds-checked reader",
            "Single mutex guards the keyspace; concurrency suite is ASan-clean (real lost-update detection)",
        ],
        "highlight": "69 tests / 300+ assertions across 6 suites; ~1.08M SET/s, ~1.84M GET/s; INT64_MIN/overflow-safe INCR; AOF crash-consistency tested.",
        "security": "Untrusted protocol parsing bounded + validated; no client-controlled file paths.",
    },
    {
        "name": "MiniShell", "domain": "Systems", "lang": "C11",
        "stack": ["C11", "fork/exec"],
        "tests": 86, "throughput": None, "headline": "no zombies/fd-leaks",
        "tagline": "A Unix shell — pipes, redirection, jobs, signals.",
        "description": (
            "A shell with command execution via fork/execvp, built-ins (cd/pwd/exit/export/env/echo), N-stage "
            "pipes, redirection (>, >>, <), background jobs with SIGCHLD reaping, signal handling, and $VAR "
            "expansion. Correctness of process/signal/fd handling is the whole challenge."
        ),
        "architecture": [
            "Tokenize (quote-aware) → parse into a pipeline of commands with redirections + background flag",
            "Built-ins run in-process; others fork, wire pipes (pipe + dup2) and redirections, then execvp",
            "SIGCHLD reaper drains a lock-free ring; SIGCHLD blocked across fork+foreground-wait to avoid status theft",
            "SIGINT forwarded to the foreground child, never the shell",
        ],
        "highlight": "300 pipelines held the open-fd count steady at 5; 50 rapid bg jobs reaped with no zombies; SIGINT survival proven via a real PTY.",
        "security": "Local tool — the risk is fd/zombie leaks and signal correctness, all verified under ASan.",
    },
    {
        "name": "MallocLab", "domain": "Systems", "lang": "C11",
        "stack": ["C11", "heap internals"],
        "tests": 20, "throughput": None, "utilization": "78–95%",
        "headline": "78–95% utilization · checkheap",
        "tagline": "A custom dynamic memory allocator.",
        "description": (
            "malloc/free/realloc/calloc implemented over a simulated heap (an mmap'd memlib, so it never touches "
            "the system allocator). Boundary-tag blocks, segregated free lists, splitting, immediate coalescing, "
            "16-byte alignment, and a real heap consistency checker."
        ),
        "architecture": [
            "memlib mmaps a region; the allocator hands out memory via mem_sbrk — fully self-contained",
            "Boundary tags (header + footer) enable O(1) coalescing of adjacent free blocks",
            "find_fit starts at the correct size class; split when the remainder ≥ a minimum block",
            "mm_checkheap asserts alignment, header==footer, no adjacent free blocks, and a heap-walk vs list-walk cross-check",
        ],
        "highlight": "A shadow model detects overlap/corruption/misalignment after every op; 50k-op random stress; 78–95% utilization; ASan + UBSan clean.",
        "security": "No network surface; the bar is brutal pointer correctness — one bad tag corrupts the heap.",
    },
]

DOMAIN_COLORS = {"Full-stack": "#6c8cff", "Systems": "#22d3a6"}

# --------------------------------------------------------------------------- #
# Page setup
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="Engineering Portfolio — Metrics", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
      .block-container{padding-top:2.2rem;max-width:1180px}
      h1,h2,h3{letter-spacing:-.01em}
      [data-testid="stMetricValue"]{font-size:1.7rem}
      .pill{display:inline-block;background:#1b2230;border:1px solid #1f2937;border-radius:999px;
            padding:2px 10px;margin:2px 4px 2px 0;font-size:.78rem;color:#c8d3e2}
      .muted{color:#93a1b5}
      a{color:#6c8cff}
    </style>
    """,
    unsafe_allow_html=True,
)

df = pd.DataFrame(PROJECTS)

# --------------------------------------------------------------------------- #
# Sidebar filters
# --------------------------------------------------------------------------- #
st.sidebar.header("Filters")
domains = st.sidebar.multiselect("Domain", ["Full-stack", "Systems"], default=["Full-stack", "Systems"])
st.sidebar.caption("Five full-stack apps · five systems projects in C/C++.")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**700** automated tests passing\n\nBuilt with a plan → implement → review → "
    "security-audit → verify workflow."
)

view = df[df["domain"].isin(domains)] if domains else df

# --------------------------------------------------------------------------- #
# Header + KPIs
# --------------------------------------------------------------------------- #
st.title("Engineering Portfolio — Metrics")
st.markdown(
    '<p class="muted">Ten projects, built end to end: five full-stack applications and five '
    "systems-programming projects in C/C++. Every project ships with tests, a clean build, a "
    "security review, and a README.</p>",
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Projects", len(view))
k2.metric("Automated tests", f"{int(view['tests'].sum()):,}")
k3.metric("Full-stack", int((view["domain"] == "Full-stack").sum()))
k4.metric("Systems (C/C++)", int((view["domain"] == "Systems").sum()))

st.markdown("---")

tab_overview, tab_deep, tab_compare, tab_table = st.tabs(
    ["📊 Overview", "🔎 Deep dive", "⚖️ Compare", "📋 All metrics"]
)

# --------------------------------------------------------------------------- #
# Overview tab
# --------------------------------------------------------------------------- #
with tab_overview:
    c1, c2 = st.columns([3, 2])

    with c1:
        st.subheader("Test coverage")
        tests_df = view.sort_values("tests", ascending=True)
        fig = px.bar(
            tests_df, x="tests", y="name", orientation="h", color="domain",
            color_discrete_map=DOMAIN_COLORS, text="tests",
            labels={"tests": "Automated tests", "name": "", "domain": "Domain"},
        )
        fig.update_layout(
            template="plotly_dark", height=430, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.08, x=0),
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Throughput (systems)")
        perf = view[view["throughput"].notna()].copy()
        if len(perf):
            perf = perf.sort_values("throughput", ascending=True)
            perf["label"] = perf.apply(
                lambda r: f"{r['throughput']/1e6:.2f}M {r.get('throughput_unit','')}"
                if r["throughput"] >= 1e6 else f"{int(r['throughput']/1e3)}k {r.get('throughput_unit','')}",
                axis=1,
            )
            figp = px.bar(
                perf, x="throughput", y="name", orientation="h", text="label",
                color_discrete_sequence=["#22d3a6"], log_x=True,
                labels={"throughput": "ops/sec (log scale)", "name": ""},
            )
            figp.update_layout(
                template="plotly_dark", height=300, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            )
            figp.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(figp, use_container_width=True)
            st.caption("Log scale — units differ per project (ops/req/GET per second). Full-stack apps aren't RPS-benchmarked.")
        else:
            st.info("Select the Systems domain to see throughput benchmarks.")

        if "MicroMatch" in view["name"].values:
            st.metric("MicroMatch order-match latency (p50)", "42 ns", help="Mean 88.5 ns/op across 1M ops")

# --------------------------------------------------------------------------- #
# Deep-dive tab
# --------------------------------------------------------------------------- #
with tab_deep:
    names = list(view["name"])
    if not names:
        st.info("No projects match the current filter.")
    else:
        pick = st.selectbox("Project", names, index=0)
        p = next(x for x in PROJECTS if x["name"] == pick)

        title = f"{p['name']}  " + ("★" if p.get("flagship") else "")
        st.subheader(title.strip())
        st.markdown(f"**{p['tagline']}**")
        st.markdown(
            " ".join(f'<span class="pill">{s}</span>' for s in p["stack"])
            + f' &nbsp; <span class="pill">{p["lang"]}</span>'
            + f' &nbsp; <span class="pill">{p["domain"]}</span>',
            unsafe_allow_html=True,
        )

        m = st.columns(3)
        m[0].metric("Tests", p["tests"])
        if p.get("throughput"):
            val = f"{p['throughput']/1e6:.2f}M" if p["throughput"] >= 1e6 else f"{int(p['throughput']/1e3)}k"
            m[1].metric("Throughput", f"{val} {p.get('throughput_unit','')}")
        elif p.get("utilization"):
            m[1].metric("Memory utilization", p["utilization"])
        if p.get("latency_ns"):
            m[2].metric("Match latency (p50)", f"{p['latency_ns']} ns")

        shot = IMG_DIR / f"{p['name'].lower()}.png"
        if shot.exists():
            st.image(str(shot), caption=f"{p['name']} — live UI", use_container_width=True)

        st.markdown("#### What it is")
        st.write(p["description"])

        st.markdown("#### Architecture")
        for a in p["architecture"]:
            st.markdown(f"- {a}")

        st.markdown("#### Standout")
        st.success(p["highlight"])

        st.markdown("#### Security / correctness focus")
        st.info(p["security"])

# --------------------------------------------------------------------------- #
# Compare tab
# --------------------------------------------------------------------------- #
with tab_compare:
    st.subheader("Side-by-side")
    picks = st.multiselect(
        "Pick projects to compare", list(df["name"]),
        default=["MicroMatch", "MiniCache", "WorkflowOps"],
    )
    if picks:
        cols = st.columns(len(picks))
        for col, name in zip(cols, picks):
            p = next(x for x in PROJECTS if x["name"] == name)
            with col:
                st.markdown(f"### {p['name']}")
                st.caption(p["tagline"])
                st.metric("Tests", p["tests"])
                if p.get("throughput"):
                    val = f"{p['throughput']/1e6:.2f}M" if p["throughput"] >= 1e6 else f"{int(p['throughput']/1e3)}k"
                    st.metric("Throughput", f"{val} {p.get('throughput_unit','')}")
                st.markdown(" ".join(f'<span class="pill">{s}</span>' for s in p["stack"]), unsafe_allow_html=True)
                st.write(p["description"])
    else:
        st.info("Pick at least one project.")

# --------------------------------------------------------------------------- #
# Table tab
# --------------------------------------------------------------------------- #
with tab_table:
    st.subheader("All projects")
    table = view[["name", "domain", "lang", "tests", "headline"]].rename(
        columns={"name": "Project", "domain": "Domain", "lang": "Language",
                 "tests": "Tests", "headline": "Headline metric"}
    )
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.caption("Metrics are real: test counts from the suites, throughput/latency from the benchmark harnesses.")

st.markdown("---")
st.caption("Built by Anish Guntreddi · systems + full-stack engineering.")
