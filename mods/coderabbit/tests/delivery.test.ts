import { expect, test } from "claude-code/testing";
import { showFindings } from "../hooks/interface.js";
import { storeReviewContext } from "../hooks/register.js";

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
