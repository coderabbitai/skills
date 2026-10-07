import { reviewSummary } from "./review.js";

// Status names are protocol data; never display arbitrary event messages as UI commands.
const LABELS = {
  connecting_to_review_service: "Connecting",
  setting_up: "Preparing review",
  preparing_sandbox: "Preparing review",
  building_code_graph: "Mapping changes",
  tools_completed: "Finishing analysis",
  summarizing: "Summarizing changes",
  reviewing: "Reviewing changes",
  review_started: "Starting review",
  review_completed: "Preparing results",
  review_skipped: "Checking review outcome",
  analyzing: "Analyzing changes",
  other: "Reviewing changes",
};

const AUTH_LABELS = {
  checking_auth: "Checking sign-in",
  starting_login: "Starting sign-in",
  awaiting_browser_auth: "Waiting for sign-in",
  browser_open_unavailable: "Sign-in needs attention",
  automatic_login_failed: "Sign-in needs attention",
  processing_callback: "Completing sign-in",
  fetching_user: "Completing sign-in",
  authenticated: "Signed in · Preparing review",
};

export function applyReviewEvent(progress, event) {
  if (!event || typeof event !== "object") return;
  progress.lastSignalSeconds = progress.elapsedSeconds;
  if (event.phase === "auth") {
    if (!["status", "complete", "action_required", "error"].includes(event.type)) return;
    progress.auth = true;
    progress.authDetail = "The review will start after sign-in.";
    if (event.type === "error") {
      progress.errorType = "auth";
      progress.label = "Sign-in failed";
      progress.authDetail = "Run coderabbit auth login, then start the review again.";
    } else if (event.type === "action_required") {
      progress.label = "Sign-in needs attention";
      progress.authDetail = "Finish sign-in with coderabbit auth login in your terminal.";
    } else if (event.type === "status" || event.type === "complete") {
      progress.label = Object.hasOwn(AUTH_LABELS, event.status)
        ? AUTH_LABELS[event.status]
        : "Signing in";
      if (event.status === "awaiting_browser_auth")
        progress.authDetail =
          "Complete sign-in in your browser. The review will continue afterward.";
      else if (event.status === "authenticated") progress.authDetail = "";
      else if (["browser_open_unavailable", "automatic_login_failed"].includes(event.status))
        progress.authDetail = "Finish sign-in with coderabbit auth login in your terminal.";
    }
    return;
  }
  if (
    event.type === "complete" &&
    Array.isArray(event.reviewedFiles) &&
    event.reviewedFiles.every((file) => typeof file === "string")
  ) {
    progress.reviewedFiles = new Set(event.reviewedFiles).size;
  }
  if (event.type === "status" && !progress.errorType) {
    progress.auth = false;
    progress.label = Object.hasOwn(LABELS, event.status)
      ? LABELS[event.status]
      : "Reviewing changes";
  } else if (event.type === "finding") {
    progress.auth = false;
    progress.findings++;
    if (["critical", "major", "minor", "trivial", "info"].includes(event.severity))
      progress.severities[event.severity] = (progress.severities[event.severity] || 0) + 1;
  } else if (event.type === "error") {
    progress.errorType = event.errorType;
    progress.label =
      event.errorType === "rate_limit"
        ? "Review limit reached"
        : event.errorType === "auth"
          ? "Sign in to review"
          : "Review could not finish";
  }
  // A heartbeat proves liveness, not a new phase or a percentage completed.
}

export function finishProgress(progress, text) {
  progress.finished = true;
  progress.label = "Review could not finish";
  try {
    const summary = reviewSummary(JSON.parse(text));
    progress.success = !!summary.success;
    progress.label = summary.label;
    progress.detail = summary.detail;
    progress.canReviewAgain = !!summary.canReviewAgain;
    if (summary.success) progress.findings = summary.count;
  } catch {
    /* Process failures stay visibly incomplete. */
  }
}

export async function readReviewStream(stream, stopped, onEvent) {
  const limit = 4 * 1024 * 1024;
  const result = {
    stdout: "",
    stderr: "",
    isStdoutTruncated: false,
    isStderrTruncated: false,
    exitCode: 0,
  };
  let line = "";
  // Closing early rejects the separate result promise as well as ending the iterator.
  void stream.result.catch(() => {});
  const emit = (text) => {
    try {
      onEvent(JSON.parse(text));
    } catch {
      /* Final validation rejects malformed NDJSON. */
    }
  };
  try {
    while (true) {
      const piece = await Promise.race([stream.next(), stopped]);
      if (piece.cancelled) throw new Error("Review stopped");
      if (piece.done) {
        if (line.trim()) emit(line);
        result.exitCode = piece.value?.code ?? 1;
        return result;
      }
      const { stream: pipe, text } = piece.value;
      if (pipe !== "stdout" && pipe !== "stderr") continue;
      const remaining = limit - result[pipe].length;
      result[pipe] += text.slice(0, remaining);
      if (text.length > remaining) {
        result[pipe === "stdout" ? "isStdoutTruncated" : "isStderrTruncated"] = true;
        return result;
      }
      if (pipe === "stdout") {
        line += text;
        let end;
        while ((end = line.indexOf("\n")) !== -1) {
          const record = line.slice(0, end);
          line = line.slice(end + 1);
          if (record.trim()) emit(record);
        }
      }
    }
  } finally {
    await stream.return();
  }
}
