import { expect, test } from "claude-code/testing";
import { showFindings } from "../hooks/interface.js";
import { register, storeReviewContext } from "../hooks/register.js";

for (const failedCall of ["surfaces", "now"]) {
  test("a failed startup call leaves the next review available: " + failedCall, async () => {
    const handlers = new Map();
    register((event, filter, handler) => handlers.set(event, handler ?? filter), {
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
      session: { surfaces: async () => hostCall("surfaces", ["desktop"]) },
      clock: {
        now: async () => hostCall("now", 1000),
        after: () => ({ cancel() {} }),
      },
    };
    const command = () => handlers.get("command.run")(host, { args: "" });
    expect((await command()).text).toContain("could not finish");
    expect((await command()).text).toContain("Reviewing in the background");
  });
}

for (const interactive of [false, true]) {
  test("late review cleanup cannot change a new session: interactive=" + interactive, async () => {
    const handlers = new Map();
    register((event, filter, handler) => handlers.set(event, handler ?? filter), {
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
      session: { surfaces: async () => [], messages: async () => [] },
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
