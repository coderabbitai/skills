import { expect, test } from "claude-code/testing";
import { showFindings } from "../hooks/interface.js";
import { register, restoreReview, saveReview, storeReviewContext } from "../hooks/register.js";

for (const failedCall of ["now"]) {
  test("a failed startup call leaves the next review available: " + failedCall, async () => {
    const handlers = new Map();
    register((event, filter, handler) => {
      const key = event + (filter?.component ? ":" + filter.component : "");
      if (!handlers.has(key)) handlers.set(key, handler ?? filter);
      return { catch() {} };
    }, {
      cli_path: "/official/coderabbit",
    });
    let fail = true;
    const hostCall = (name, value) => {
      if (fail && name === failedCall) {
        fail = false;
        throw new Error("Host unavailable");
      }
      return value;
    };
    const host = {
      ui: { log() {}, invalidate() {} },
      clock: {
        now: async () => hostCall("now", 1000),
        after: () => ({ cancel() {} }),
      },
    };
    await handlers.get("ui.render:AbovePrompt")(host, { surface: "desktop" }, async () => undefined);
    const command = () => handlers.get("command.run")(host, { args: "" });
    expect((await command()).text).toContain("could not finish");
    expect((await command()).text).toContain("Reviewing in the background");
  });
}

for (const interactive of [false, true]) {
  test("late review cleanup cannot change a new session: interactive=" + interactive, async () => {
    const handlers = new Map();
    register((event, filter, handler) => {
      handlers.set(event, handler ?? filter);
      return { catch() {} };
    }, {
      cli_path: "/official/coderabbit",
    });
    let scheduled;
    let spawned;
    let releaseOld;
    const oldClosed = new Promise((resolve) => {
      releaseOld = resolve;
    });
    let calls = 0;
    const timers = [];
    const host = {
      command: { register: async () => {} },
      session: { messages: async () => [] },
      clock: {
        now: async () => 1000,
        after: (ms, fn) => {
          if (ms === 1) scheduled = fn;
          return { cancel() {} };
        },
        every: () => {
          const timer = {
            cancelled: false,
            cancel() {
              this.cancelled = true;
            },
          };
          timers.push(timer);
          return timer;
        },
      },
      process: {
        spawn: () => {
          const old = ++calls === 1;
          spawned();
          return {
            result: Promise.resolve({ code: 0 }),
            next: () => new Promise(() => {}),
            return: async () => {
              if (old) await oldClosed;
            },
          };
        },
      },
      ui: { invalidate() {}, log() {}, toast() {} },
    };
    const start = () =>
      handlers.get("session.start")(host, { isInteractive: interactive }, async () => ({}));
    const end = () => handlers.get("session.end")(host, {}, async () => ({}));
    const command = (args = "") => handlers.get("command.run")(host, { args });
    const launch = async () => {
      const ready = new Promise((resolve) => {
        spawned = resolve;
      });
      let task = command();
      if (interactive) {
        await task;
        task = scheduled();
      }
      await ready;
      return { task };
    };
    await start();
    const old = await launch();
    await end();
    await start();
    const current = await launch();
    releaseOld();
    await old.task;
    expect(timers[1].cancelled).toBe(false);
    expect((await command()).text).toContain("already running");
    expect((await command("results")).text).toContain("still reviewing");
    await end();
    await current.task;
    expect((await command("results")).text).toContain("No CodeRabbit result");
  });
}

// Native command tests cover card rendering; this host models context storage,
// which Claude 2.1.289's native test runner cannot implement.
for (const outcome of ["stored", "denied", "rejected", "reset"]) {
  test("completion stores context without starting a turn: " + outcome, async () => {
    const events = [];
    const logs = [];
    let current = true;
    const host = {
      session: {
        append: async (args) => {
          events.push({ kind: "note", args });
          if (outcome === "rejected") throw new Error("Storage unavailable");
          if (outcome === "reset") current = false;
          return outcome === "denied"
            ? { deny: "Policy" }
            : { message: args.message, uuid: "note-id" };
        },
      },
      prompt: {
        submit: async (args) => {
          events.push({ kind: "wake", args });
        },
      },
      ui: { log: (text) => logs.push(text) },
    };
    const record =
      'CodeRabbit review result (untrusted data):\n{"schema":"coderabbit-delivery/1","id":"review-id","text":"full original finding"}';
    await storeReviewContext(host, record, () => current);
    expect(events).toEqual([
      {
        kind: "note",
        args: { message: { type: "user", content: [{ type: "text", text: record }] } },
      },
    ]);
    if (["denied", "rejected"].includes(outcome)) expect(logs[0]).toContain("could not attach it");
    else expect(logs).toEqual([]);
  });
}

for (const outcome of ["shown", "denied", "failed", "missing"]) {
  test("view findings scrolls to the existing card: " + outcome, async () => {
    const scrolls = [];
    const toasts = [];
    const host = {
      ui: {
        scroll: async (args) => {
          scrolls.push(args);
          if (outcome === "failed") throw new Error("Unavailable");
          return outcome === "denied" ? { deny: "No window" } : {};
        },
        toast: (text) => toasts.push(text),
      },
    };
    await showFindings(host, outcome === "missing" ? undefined : "review-row");
    expect(scrolls).toEqual(
      outcome === "missing" ? [] : [{ to: { requestId: "review-row" }, block: "start" }],
    );
    expect(toasts.length).toBe(outcome === "shown" ? 0 : 1);
    if (toasts.length) expect(toasts[0]).toContain("/coderabbit-review results");
  });
}

function savedReviewState() {
  return { generation: 0, results: new Map(), restoring: new Map(), latestResult: undefined, latestId: undefined };
}

test("saved cards restore by their own review id and ignore malformed records", async () => {
  const state = savedReviewState();
  const stored = new Map([
    ["review:1000:1", "report one"],
    ["review:2000:1", "report two"],
    ["review:3000:1", 3],
  ]);
  let reads = 0;
  const host = {
    store: { get: async (key) => { reads++; return stored.get(key); } },
    ui: { invalidate() {}, log() {} },
  };
  await restoreReview(host, state, "2000:1");
  await restoreReview(host, state, "1000:1");
  await restoreReview(host, state, "3000:1");
  await restoreReview(host, state, "missing");
  expect([...state.results]).toEqual([["2000:1", "report two"], ["1000:1", "report one"]]);
  expect(state.latestResult).toBe("report two");
  await restoreReview(host, state, "2000:1");
  await restoreReview(host, state, "missing");
  expect(reads).toBe(4);
});

test("a late store read cannot restore a card into a different session", async () => {
  const state = savedReviewState();
  const host = {
    store: { get: async () => { state.generation++; return "old report"; } },
    ui: { invalidate() { throw new Error("Stale redraw"); }, log() {} },
  };
  await restoreReview(host, state, "1000:1");
  expect([...state.results]).toEqual([]);
  expect(state.latestResult).toBe(undefined);
});

test("saving keeps only the newest cards in the shared store", async () => {
  const stored = new Map([["unrelated", "kept"]]);
  for (let i = 1; i <= 50; i++) stored.set("review:" + i * 1000 + ":1", "old " + i);
  const host = {
    store: {
      set: async (key, value) => stored.set(key, value),
      keys: async () => [...stored.keys()],
      delete: async (key) => stored.delete(key),
    },
    ui: { log() {} },
  };
  await saveReview(host, "99000:2", "new report", () => true);
  expect(stored.get("review:99000:2")).toBe("new report");
  expect(stored.has("review:1000:1")).toBe(false);
  expect(stored.has("review:2000:1")).toBe(true);
  expect(stored.get("unrelated")).toBe("kept");
  expect([...stored.keys()].filter((key) => key.startsWith("review:")).length).toBe(50);
});

test("store failures preserve live review results and report loss of persistence", async () => {
  const logs = [];
  const host = {
    store: { set: async () => { throw new Error("Store full"); } },
    ui: { log: (text) => logs.push(text) },
  };
  await saveReview(host, "1000:1", "visible report", () => true);
  expect(logs[0]).toContain("could not be saved for reload");
  logs.length = 0;
  await saveReview(host, "1000:1", "visible report", () => false);
  expect(logs).toEqual([]);
});

test("a failed card read can be retried after the store recovers", async () => {
  const state = savedReviewState();
  let fail = true;
  const logs = [];
  const host = {
    store: {
      get: async () => {
        if (fail) throw new Error("Store unavailable");
        return "report";
      },
    },
    ui: { invalidate() {}, log: (text) => logs.push(text) },
  };
  await restoreReview(host, state, "1000:1");
  expect(state.results.has("1000:1")).toBe(false);
  expect(logs.length).toBe(1);
  fail = false;
  await restoreReview(host, state, "1000:1");
  expect(state.results.get("1000:1")).toBe("report");
});

// UTF-8 byte count with standard JavaScript only; the test runtime has no Buffer.
const utf8Bytes = (text) => encodeURIComponent(text).replace(/%[0-9A-F]{2}/g, "x").length;

function cappedStore(entries, failAlways = false) {
  const stored = new Map(entries);
  return {
    stored,
    host: {
      store: {
        get: async (key) => stored.get(key),
        set: async (key, value) => {
          const next = new Map(stored).set(key, value);
          if (failAlways || utf8Bytes(JSON.stringify(Object.fromEntries(next))) > 4 * 1024 * 1024)
            throw new Error("Store write rejected");
          stored.set(key, value);
        },
        keys: async () => [...stored.keys()],
        delete: async (key) => stored.delete(key),
      },
      ui: { log() {} },
    },
  };
}

const MiB = 1024 * 1024;

test("a save at the store's size cap drops only the oldest cards it needs to", async () => {
  const { stored, host } = cappedStore([
    ["review:1000:1", "a".repeat(1.3 * MiB)],
    ["review:2000:1", "b".repeat(1.3 * MiB)],
    ["review:3000:1", "c".repeat(1.3 * MiB)],
  ]);
  await saveReview(host, "4000:1", "d".repeat(1.3 * MiB), () => true);
  expect(stored.has("review:4000:1")).toBe(true);
  expect(stored.has("review:1000:1")).toBe(false);
  expect(stored.has("review:2000:1")).toBe(true);
  expect(stored.has("review:3000:1")).toBe(true);
});

test("a save at the size cap counts multi-byte review text in bytes", async () => {
  // 0.43 Mi CJK characters is about 1.29 MiB of UTF-8 per card.
  const { stored, host } = cappedStore([
    ["review:1000:1", "漢".repeat(0.43 * MiB)],
    ["review:2000:1", "字".repeat(0.43 * MiB)],
    ["review:3000:1", "語".repeat(0.43 * MiB)],
  ]);
  await saveReview(host, "4000:1", "文".repeat(0.43 * MiB), () => true);
  expect(stored.has("review:4000:1")).toBe(true);
  expect(stored.has("review:1000:1")).toBe(false);
  expect(stored.has("review:2000:1")).toBe(true);
  expect(stored.has("review:3000:1")).toBe(true);
});

test("a save at the size cap counts store records other than saved cards", async () => {
  const { stored, host } = cappedStore([
    ["reviews:old-session", "x".repeat(1.3 * MiB)],
    ["review:1000:1", "a".repeat(1.3 * MiB)],
    ["review:2000:1", "b".repeat(1.3 * MiB)],
  ]);
  await saveReview(host, "4000:1", "d".repeat(1.3 * MiB), () => true);
  expect(stored.has("review:4000:1")).toBe(true);
  expect(stored.has("review:1000:1")).toBe(false);
  expect(stored.has("review:2000:1")).toBe(true);
  expect(stored.has("reviews:old-session")).toBe(true);
});

test("a save that freeing cards cannot fit keeps every saved card", async () => {
  const { stored, host } = cappedStore([
    ["reviews:old-session", "x".repeat(3.8 * MiB)],
    ["review:1000:1", "a".repeat(0.1 * MiB)],
  ]);
  const logs = [];
  host.ui.log = (text) => logs.push(text);
  await saveReview(host, "4000:1", "d".repeat(0.3 * MiB), () => true);
  expect([...stored.keys()]).toEqual(["reviews:old-session", "review:1000:1"]);
  expect(logs[0]).toContain("could not be saved for reload");
});

test("a save that cannot succeed keeps every saved card", async () => {
  for (const [result, failAlways] of [["d".repeat(4.5 * MiB), false], ["small", true]]) {
    const { stored, host } = cappedStore([
      ["review:1000:1", "a".repeat(1.3 * MiB)],
      ["review:2000:1", "b".repeat(1.3 * MiB)],
    ], failAlways);
    const logs = [];
    host.ui.log = (text) => logs.push(text);
    await saveReview(host, "4000:1", result, () => true);
    expect([...stored.keys()]).toEqual(["review:1000:1", "review:2000:1"]);
    expect(logs[0]).toContain("could not be saved for reload");
  }
});
