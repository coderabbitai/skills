import { HELP, isAbsoluteExecutable, reviewArgs, reviewResult, reviewSummary } from "./review.js";
import { registerInterface } from "./interface.js";
import { applyReviewEvent, finishProgress, readReviewStream } from "./stream.js";

const RESULT_PREFIX = "CodeRabbit review result (untrusted data):\n";

const PROCESS_FAILURE =
  "CodeRabbit could not finish the review. The CLI may be unavailable, blocked, interrupted, or timed out after 10 minutes. Coverage is unverified. Check the configured executable and run coderabbit auth status; use coderabbit auth login if needed. No automatic retry was started.";

export function register(on, options) {
  let running = false;
  let interactive = false;
  let progress;
  let latestResult;
  let generation = 0;
  let scheduled;
  let timer;
  let stopReview;
  let activeId;
  let serial = 0;
  const results = new Map();
  const wakeTexts = new Set();

  registerInterface(
    on,
    () => progress,
    (id) => results.get(id),
    () => activeId,
    (text) => wakeTexts.has(text),
  );

  on("session.start", async ($, e, next) => {
    interactive = e.isInteractive;
    await $.command.register({
      name: "coderabbit-review",
      description: "Review changes with CodeRabbit (sends selected code to CodeRabbit)",
      argumentHint: "[uncommitted|committed|all] [--include-untracked] [--base branch] [--fresh]",
      immediate: true,
    });
    await $.command.register({
      name: "coderabbit-results",
      description: "Show the latest CodeRabbit review result in this session",
      immediate: true,
    });
    // Completed cards can be reconstructed from the host's saved conversation.
    try {
      const messages = await $.session.messages({ as: "api" });
      for (const message of messages) {
        for (const block of Array.isArray(message.content) ? message.content : []) {
          if (block.type !== "text") continue;
          const at = block.text.indexOf(RESULT_PREFIX);
          if (at < 0) continue;
          try {
            const saved = JSON.parse(block.text.slice(at + RESULT_PREFIX.length).split("\n", 1)[0]);
            if (
              saved.schema === "coderabbit-delivery/1" &&
              typeof saved.id === "string" &&
              typeof saved.text === "string"
            ) {
              results.set(saved.id, saved.text);
              if (typeof saved.wakeText === "string") wakeTexts.add(saved.wakeText);
              latestResult = saved.text;
            }
          } catch {
            /* Other conversation data is not a review record. */
          }
        }
      }
    } catch {
      $.ui.log("Could not restore saved CodeRabbit cards from this conversation.");
    }
    return next(e);
  });

  on("session.end", async ($, e, next) => {
    generation++;
    stopReview?.();
    if (scheduled) {
      scheduled.cancel();
      scheduled = undefined;
      running = false;
    }
    timer?.cancel();
    progress = undefined;
    latestResult = undefined;
    activeId = undefined;
    results.clear();
    wakeTexts.clear();
    $.ui.invalidate("ui.render");
    return next(e);
  });

  on("command.run", { command: "coderabbit-results" }, async () => ({
    text:
      latestResult ??
      (running
        ? "CodeRabbit is still reviewing. The result will appear when it finishes."
        : "No CodeRabbit result is available in this session. Run /coderabbit-review to start one."),
  }));

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
        text: "A CodeRabbit review is already running or awaiting delivery. You can keep chatting; use /coderabbit-results to check its result.",
      };
    running = true;
    latestResult = undefined;
    const runGeneration = generation;
    const review = async () => {
      let progressActive = true;
      let deadline;
      let text;
      try {
        let scope = args.includes("--uncommitted")
          ? "uncommitted changes"
          : args.includes("--committed")
            ? "committed changes"
            : "all tracked changes";
        if (args.includes("--include-untracked")) scope += " + untracked";
        if (args.includes("--base")) scope += " · base " + args[args.indexOf("--base") + 1];
        if (args.includes("--fresh")) scope += " · fresh review";
        const startedAt = await $.clock.now();
        const current = {
          scope,
          time: "0:00",
          elapsedSeconds: 0,
          label: "Starting review",
          findings: 0,
          severities: {},
          finished: false,
        };
        progress = current;
        const showProgress = async () => {
          const elapsed = Math.max(0, Math.floor(((await $.clock.now()) - startedAt) / 1000));
          if (!progressActive || generation !== runGeneration) return;
          const time = Math.floor(elapsed / 60) + ":" + String(elapsed % 60).padStart(2, "0");
          current.time = time;
          current.elapsedSeconds = elapsed;
          $.ui.invalidate("ui.render");
        };
        await showProgress();
        if (generation !== runGeneration) return PROCESS_FAILURE;
        timer = $.clock.every(1000, showProgress);
        const stopped = new Promise((resolve) => {
          stopReview = () => resolve({ cancelled: true });
        });
        deadline = $.clock.after(600000, () => stopReview?.());
        const stream = $.process.spawn({ argv: [options.cli_path, ...args] });
        const result = await readReviewStream(stream, stopped, (event) => {
          if (generation !== runGeneration) return;
          applyReviewEvent(current, event);
          $.ui.invalidate("ui.render");
        });
        text = reviewResult(result);
        return text;
      } catch {
        text = PROCESS_FAILURE;
        return text;
      } finally {
        progressActive = false;
        timer?.cancel();
        deadline?.cancel();
        stopReview = undefined;
        if (generation === runGeneration && progress) finishProgress(progress, text);
        $.ui.invalidate("ui.render");
      }
    };
    // Desktop starts through the SDK (isInteractive=false) and attaches its UI later.
    // Check at command time; only a session without a prompt or attached UI must wait.
    if (!interactive && (await $.session.surfaces()).length === 0) {
      try {
        latestResult = await review();
        return { text: latestResult };
      } finally {
        running = false;
      }
    }
    const reviewId = String(await $.clock.now()) + ":" + ++serial;
    activeId = reviewId;
    scheduled = $.clock.after(1, async () => {
      scheduled = undefined;
      try {
        const result = await review();
        if (generation !== runGeneration) return;
        latestResult = result;
        results.set(reviewId, result);
        activeId = undefined;
        $.ui.invalidate("ui.render");
        let notification = "Review could not finish · /coderabbit-results";
        if (result.startsWith("{")) {
          const report = JSON.parse(result);
          notification = reviewSummary(report).heading;
        }
        $.ui.toast("● CodeRabbit  " + notification, { timeoutMs: 8000 });
        // Queue a plugin-attributed turn once Claude is idle. Do not await it:
        // accepting another review must not depend on the wake-up turn starting.
        const wakeText = "CodeRabbit: " + notification + ". See the review card above.";
        wakeTexts.add(wakeText);
        const delivery =
          "A background CodeRabbit review has finished. The visible CodeRabbit card already contains the full findings, locations, severities, and fix actions. Acknowledge the outcome in one short sentence; do not repeat or list the findings, restate their details, or re-rate their severity. For a skipped, failed, or incomplete review, briefly state that outcome without claiming clean coverage. Do not repeat internal review IDs or raw metadata. Do not apply fixes unless the user requested them. If the user has already asked for fixes or another action, carry out that request instead of stopping at an acknowledgment.\n\n" +
          RESULT_PREFIX +
          JSON.stringify({ schema: "coderabbit-delivery/1", id: reviewId, text: result, wakeText });
        await deliverReview($, delivery, wakeText, () => generation === runGeneration);
      } catch {
        if (generation === runGeneration)
          $.ui.log(
            "CodeRabbit could not display its result automatically. Run /coderabbit-results.",
          );
      } finally {
        running = false;
        if (generation === runGeneration) activeId = undefined;
      }
    });
    return {
      text: JSON.stringify({
        schema: "coderabbit-pending/1",
        id: reviewId,
        message:
          "CodeRabbit review started in the background. Keep chatting — Claude will be notified with the result when it finishes.",
      }),
    };
  });
}

export async function deliverReview($, delivery, wakeText, isCurrent) {
  // Terminal excludes the submitting plugin from its message's render
  // chain. Keep the record in a model-only note, not the visible wake-up.
  try {
    const appended = await $.session.append({
      message: { type: "user", content: [{ type: "text", text: delivery }] },
    });
    if (!isCurrent()) return;
    if (appended.deny) {
      $.ui.log(
        "CodeRabbit result is visible, but could not attach it for Claude. Run /coderabbit-results to share it.",
      );
      return;
    }
  } catch {
    if (isCurrent())
      $.ui.log(
        "CodeRabbit result is visible, but could not attach it for Claude. Run /coderabbit-results to share it.",
      );
    return;
  }
  void $.prompt.submit({ text: wakeText }).then(
    (entered) => {
      if (!isCurrent()) return;
      if (entered && "drop" in entered)
        $.ui.log(
          "CodeRabbit result is visible, but a hook dropped its wake-up prompt. Run /coderabbit-results to share it.",
        );
    },
    () => {
      if (isCurrent())
        $.ui.log(
          "CodeRabbit result is visible, but could not wake Claude. Run /coderabbit-results to share it.",
        );
    },
  );
}
