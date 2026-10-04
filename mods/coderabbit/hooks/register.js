import { HELP, isAbsoluteExecutable, reviewArgs, reviewResult } from "./review.js";

export function register(on, options) {
  let running = false;

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
    try {
      $.ui.status(
        "Review running: " +
          (args.slice(2).join(" ") || "all tracked changes") +
          " (up to 10 minutes)",
      );
      $.ui.log("Review started. CodeRabbit findings will appear when the CLI finishes.");
      const result = await $.process.run([options.cli_path, ...args], { timeoutMs: 600000 });
      return { text: reviewResult(result) };
    } catch {
      return {
        text: "CodeRabbit could not finish the review. The CLI may be unavailable, blocked, interrupted, or timed out after 10 minutes. Coverage is unverified. Check the configured executable and run coderabbit auth status; use coderabbit auth login if needed. No automatic retry was started.",
      };
    } finally {
      running = false;
      $.ui.status(undefined);
    }
  });
}
