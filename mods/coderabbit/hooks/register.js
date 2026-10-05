import { HELP, isAbsoluteExecutable, reviewArgs, reviewResult } from "./review.js";

const BRAND_ORANGE = "#FF570A";

export function register(on, options) {
  let running = false;
  let progress;

  on("ui.render", { component: "AbovePrompt" }, async ($, e, next) => {
    const rest = await next(e);
    if (!progress || e.props.hasSurvey) return rest;
    const { Box, Text } = $.ui.resolve(e);
    return Box({
      flexDirection: "column",
      marginTop: 1,
      children: [
        Text({
          children: [
            Text({ color: BRAND_ORANGE, bold: true, children: ["● CodeRabbit"] }),
            "  Reviewing  ",
            Text({ dimColor: true, children: [progress.time] }),
          ],
        }),
        Text({ dimColor: true, children: ["  " + progress.scope] }),
        rest,
      ],
    });
  });

  on("session.start", async ($, e, next) => {
    await $.command.register({
      name: "coderabbit-review",
      description: "Review changes with CodeRabbit (sends selected code to CodeRabbit)",
      argumentHint: "[uncommitted|committed|all] [--include-untracked] [--base branch]",
    });
    return next(e);
  });

  on("command.run", { command: "coderabbit-review" }, async ($, e) => {
    let args;
    try {
      args = reviewArgs(e.args);
    } catch (error) {
      return { text: error.message + "\n\n" + HELP };
    }
    if (!args) return { text: HELP };
    if (!isAbsoluteExecutable(options.cli_path)) {
      return {
        text:
          "Set cli_path to the absolute path of your official CodeRabbit CLI in this plugin's configuration, then reload the plugin. No review started.\n\n" +
          HELP,
      };
    }
    if (running)
      return {
        text: "A CodeRabbit review is already running in this session. Wait for its result before starting another.",
      };
    running = true;
    let timer;
    let progressActive = true;
    try {
      let scope = args.includes("--uncommitted")
        ? "uncommitted changes"
        : args.includes("--committed")
          ? "committed changes"
          : "all tracked changes";
      if (args.includes("--include-untracked")) scope += " + untracked";
      const startedAt = await $.clock.now();
      const showProgress = async () => {
        const elapsed = Math.max(0, Math.floor(((await $.clock.now()) - startedAt) / 1000));
        // A clock read may finish after the process and its cleanup.
        if (!progressActive) return;
        const time = Math.floor(elapsed / 60) + ":" + String(elapsed % 60).padStart(2, "0");
        progress = { scope, time };
        $.ui.invalidate("ui.render");
      };
      await showProgress();
      timer = $.clock.every(1000, showProgress);
      $.ui.log("Review started. CodeRabbit findings will appear when the CLI finishes.");
      const result = await $.process.run([options.cli_path, ...args], { timeoutMs: 600000 });
      return { text: reviewResult(result) };
    } catch {
      return {
        text: "CodeRabbit could not finish the review. The CLI may be unavailable, blocked, interrupted, or timed out after 10 minutes. Coverage is unverified. Check the configured executable and run coderabbit auth status; use coderabbit auth login if needed. No automatic retry was started.",
      };
    } finally {
      progressActive = false;
      timer?.cancel();
      running = false;
      progress = undefined;
      $.ui.invalidate("ui.render");
    }
  });
}
