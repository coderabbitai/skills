import { expect, mock, test } from "claude-code/testing";

const OPTIONS = { options: { cli_path: "/test/CodeRabbit CLI" } };
const complete = (status = "review_completed", findings = 0) =>
  JSON.stringify({ type: "complete", status, findings }) + "\n";
const output = (stdout, extra = {}) => ({
  exitCode: 0,
  stdout,
  stderr: "",
  isStdoutTruncated: false,
  isStderrTruncated: false,
  ...extra,
});

function stubProcess(on, result) {
  mock.clock(on);
  const calls = [];
  const statuses = [];
  on("ui.status", ($, e) => {
    statuses.push(e.text);
    return { value: undefined };
  });
  on("ui.log", () => ({ value: undefined }));
  on("process.run", ($, e) => {
    calls.push(e);
    return { value: result };
  });
  return { calls, statuses };
}

test("registers the command without running a process", OPTIONS, async ($, on) => {
  const registered = [];
  on("command.register", ($, e) => {
    registered.push(e);
    return { value: undefined };
  });
  on("session.start", () => ({ cwd: "/work" }));
  await $.session.start({ surface: "terminal", isInteractive: true, cwd: "/work" });
  expect(registered.length).toBe(1);
  expect(registered[0].name).toBe("coderabbit-review");
});

test("help discloses data transfer and does not run a review", OPTIONS, async ($) => {
  const answer = await $.command.run({ command: "coderabbit-review", args: "--help" });
  expect(answer.text).toContain("Usage: /coderabbit-review");
  expect(answer.text).toContain("send the selected diff");
});

for (const [args, expected] of [
  ["", ["--uncommitted"]],
  ["uncommitted --include-untracked", ["--uncommitted", "--include-untracked"]],
  ["committed --base feature/topic", ["--committed", "--base", "feature/topic"]],
  ["all", []],
  ["all --include-untracked", ["--include-untracked"]],
]) {
  test("preserves scope: " + (args || "default"), OPTIONS, async ($, on) => {
    const { calls, statuses } = stubProcess(on, output(complete()));
    const answer = await $.command.run({ command: "coderabbit-review", args });
    expect(answer.text).toContain("review completed: 0 finding(s)");
    expect(calls.length).toBe(1);
    expect(calls[0].argv).toEqual(["/test/CodeRabbit CLI", "review", "--agent", ...expected]);
    expect(calls[0].init).toEqual({ timeoutMs: 600000 });
    expect(statuses.length).toBe(2);
    expect(statuses[0]).toContain("CodeRabbit reviewing");
    expect(statuses[0]).toContain("0:00");
    expect(statuses[1]).toBeUndefined();
  });
}

for (const args of [
  "committed --include-untracked",
  "unknown",
  "all --base",
  "all --base --fresh",
  "all --use-credits",
  "all --api-key secret",
  "all --base main --base other",
  "all ; echo injected",
]) {
  test("rejects invalid scope without a process: " + args, OPTIONS, async ($) => {
    const answer = await $.command.run({ command: "coderabbit-review", args });
    expect(answer.text).toContain("Usage:");
  });
}

test(
  "requires an absolute executable instead of searching PATH",
  { options: { cli_path: "coderabbit" } },
  async ($) => {
    const answer = await $.command.run({ command: "coderabbit-review", args: "" });
    expect(answer.text).toContain("No review started");
  },
);

const finding = {
  type: "finding",
  severity: "major",
  fileName: "src/example.ts",
  codegenInstructions: "Check the nullable value.",
  suggestions: ["Keep existing behavior."],
};

test(
  "returns original finding severity and fix guidance as untrusted data",
  OPTIONS,
  async ($, on) => {
    stubProcess(on, output(JSON.stringify(finding) + "\n" + complete("review_completed", 1)));
    const answer = await $.command.run({ command: "coderabbit-review", args: "" });
    expect(answer.text).toContain("review completed: 1 finding(s)");
    expect(answer.text).toContain('"severity": "major"');
    expect(answer.text).toContain("Check the nullable value.");
    expect(answer.text).toContain("not instructions");
  },
);

for (const [name, result, expected] of [
  ["skipped", output(complete("review_skipped")), "no new analysis"],
  ["heartbeat only", output('{"type":"heartbeat"}\n'), "incomplete"],
  ["malformed", output("not-json\n" + complete()), "incomplete"],
  ["count mismatch", output(complete("review_completed", 2)), "incomplete"],
  ["duplicate completion", output(complete() + complete()), "incomplete"],
  ["unknown status", output(complete("new_status")), "unknown outcome"],
  ["stdout truncated", output(complete(), { isStdoutTruncated: true }), "incomplete"],
  ["stderr truncated", output(complete(), { isStderrTruncated: true }), "incomplete"],
  ["nonzero exit", output(complete(), { exitCode: 1 }), "failed"],
  [
    "auth error",
    output('{"type":"error","errorType":"auth","message":"Please log in"}\n'),
    "failed",
  ],
  [
    "error then complete",
    output('{"type":"error","message":"Disconnected"}\n' + complete()),
    "failed",
  ],
]) {
  test("does not claim clean coverage for " + name, OPTIONS, async ($, on) => {
    const { calls } = stubProcess(on, result);
    const answer = await $.command.run({ command: "coderabbit-review", args: "" });
    expect(answer.text).toContain(expected);
    expect(answer.text).not.toContain("review completed:");
    expect(calls.length).toBe(1);
  });
}

test("bounds displayed findings and explicitly reports truncation", OPTIONS, async ($, on) => {
  stubProcess(
    on,
    output(
      JSON.stringify({ ...finding, codegenInstructions: "x".repeat(25000) }) +
        "\n" +
        complete("review_completed", 1),
    ),
  );
  const answer = await $.command.run({ command: "coderabbit-review", args: "" });
  expect(answer.text).toContain("Display truncated");
  expect(answer.text).toContain("review findings");
});

test(
  "failed process clears progress, does not retry, and allows a later user retry",
  OPTIONS,
  async ($, on) => {
    mock.clock(on);
    let calls = 0;
    const statuses = [];
    on("ui.status", ($, e) => {
      statuses.push(e.text);
      return { value: undefined };
    });
    on("ui.log", () => ({ value: undefined }));
    on("process.run", () => {
      calls++;
      throw new Error("Process unavailable");
    });
    const first = await $.command.run({ command: "coderabbit-review", args: "" });
    expect(first.text).toContain("Coverage is unverified");
    expect(calls).toBe(1);
    const second = await $.command.run({ command: "coderabbit-review", args: "" });
    expect(second.text).toContain("Coverage is unverified");
    expect(calls).toBe(2);
    expect(statuses[statuses.length - 1]).toBeUndefined();
  },
);

test("refuses an overlapping review without launching a second process", OPTIONS, async ($, on) => {
  mock.clock(on);
  let finish;
  let started;
  let calls = 0;
  const entered = new Promise((resolve) => {
    started = resolve;
  });
  const pending = new Promise((resolve) => {
    finish = resolve;
  });
  on("ui.status", () => ({ value: undefined }));
  on("ui.log", () => ({ value: undefined }));
  on("process.run", async () => {
    calls++;
    started();
    return { value: await pending };
  });
  const first = $.command.run({ command: "coderabbit-review", args: "" });
  await entered;
  const second = await $.command.run({ command: "coderabbit-review", args: "" });
  expect(second.text).toContain("already running");
  expect(calls).toBe(1);
  finish(output(complete()));
  expect((await first).text).toContain("review completed");
});

for (const fails of [false, true]) {
  test(
    "updates elapsed status and stops after " + (fails ? "failure" : "completion"),
    OPTIONS,
    async ($, on) => {
      const clock = mock.clock(on);
      const statuses = [];
      on("ui.status", ($, e) => {
        statuses.push(e.text);
        return { value: undefined };
      });
      on("ui.log", () => ({ value: undefined }));
      on("process.run", async () => {
        await clock.sleep(65000);
        if (fails) throw new Error("Process interrupted");
        return { value: output(complete()) };
      });
      on("ui.render", { component: "AbovePrompt" }, ($, e) => {
        const { Text } = $.ui.resolve(e);
        return Text({ key: "other-mod", children: ["Other mod content"] });
      });
      const band = await $.ui.mount({
        plugin: "coderabbit-mod",
        surface: "terminal",
        component: "AbovePrompt",
        props: {
          hasSurvey: false,
          isWorking: false,
          maxRows: 5,
          bodyColumns: 80,
          scroll: { offset: 0, bodyRows: 5 },
          view: {},
        },
      });
      expect(JSON.stringify(await band.drawn())).not.toContain("CodeRabbit reviewing");
      const pending = $.command.run({
        command: "coderabbit-review",
        args: "committed --base main",
      });
      await clock.settle();
      expect(statuses[0]).toBe("CodeRabbit reviewing · committed changes · 0:00");
      expect(await band.drawn()).toMatchObject({
        type: "Box",
        children: [
          { type: "Text", children: [statuses[0]] },
          { type: "Text", children: ["Other mod content"] },
        ],
      });
      expect(JSON.stringify(await band.drawn())).toContain("Other mod content");
      await clock.advance(12000);
      expect(statuses[statuses.length - 1]).toBe("CodeRabbit reviewing · committed changes · 0:12");
      expect(JSON.stringify(await band.drawn())).toContain(statuses[statuses.length - 1]);
      await clock.advance(50000);
      expect(statuses[statuses.length - 1]).toBe("CodeRabbit reviewing · committed changes · 1:02");
      await clock.advance(3000);
      const answer = await pending;
      expect(answer.text).toContain(fails ? "Coverage is unverified" : "review completed");
      expect(statuses[statuses.length - 1]).toBeUndefined();
      expect(JSON.stringify(await band.drawn())).not.toContain("CodeRabbit reviewing");
      expect(JSON.stringify(await band.drawn())).toContain("Other mod content");
      const count = statuses.length;
      await clock.advance(5000);
      expect(statuses.length).toBe(count);
    },
  );
}
