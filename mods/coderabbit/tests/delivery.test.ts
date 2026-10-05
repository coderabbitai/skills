import { expect, test } from "claude-code/testing";
import { deliverReview } from "../hooks/register.js";

// The 2.1.289 test host cannot implement the plugin's session.append operation.
// Exercise delivery ordering here; a real CLI fixture verifies note visibility
// and model access. The native command tests still cover cards and failures.
for (const outcome of [
  "stored",
  "denied",
  "rejected",
  "reset",
  "wake-drop",
  "wake-reject",
  "wake-delayed",
]) {
  test("model note precedes the concise wake-up: " + outcome, async () => {
    const events = [];
    const logs = [];
    let current = true;
    let release;
    const pending = new Promise((resolve) => {
      release = resolve;
    });
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
          if (outcome === "wake-reject") throw new Error("Wake unavailable");
          if (outcome === "wake-delayed") await pending;
          return outcome === "wake-drop" ? { drop: "Policy" } : { text: args.text };
        },
      },
      ui: { log: (text) => logs.push(text) },
    };
    const record =
      'CodeRabbit review result (untrusted data):\n{"schema":"coderabbit-delivery/1","id":"review-id","text":"full original finding"}';
    await deliverReview(
      host,
      record,
      "CodeRabbit: Review complete · 1 finding. See the review card above.",
      () => current,
    );
    expect(events[0]).toEqual({
      kind: "note",
      args: { message: { type: "user", content: [{ type: "text", text: record }] } },
    });
    if (["denied", "rejected", "reset"].includes(outcome)) {
      expect(events.length).toBe(1);
      if (outcome !== "reset") expect(logs[0]).toContain("could not attach it");
      else expect(logs).toEqual([]);
    } else {
      expect(events.length).toBe(2);
      expect(events[1].args).toEqual({
        text: "CodeRabbit: Review complete · 1 finding. See the review card above.",
      });
      if (outcome === "wake-drop") expect(logs[0]).toContain("dropped its wake-up");
      else if (outcome === "wake-reject") expect(logs[0]).toContain("could not wake Claude");
      else expect(logs).toEqual([]);
    }
    release();
  });
}
