import { HELP, HELP_ACTIONS, HELP_ADVANCED, HELP_SETUP, reviewSummary } from "./review.js";

const BRAND_ORANGE = "#FF570A";

export function registerInterface(on, getProgress, getResult, getActiveId, resultRows) {
  const expanded = new Set();

  on("ui.render", { component: "AbovePrompt" }, async ($, e, next) => {
    const rest = await next(e);
    const progress = getProgress();
    if (!progress || progress.dismissed || e.props.hasSurvey) return rest;
    const { Box, Text, Button } = $.ui.resolve(e);
    const count = progress.findings
      ? progress.findings +
        (progress.findings === 1 ? " finding" : " findings") +
        (progress.finished ? (progress.success ? "" : " received") : " so far")
      : "";
    const details = expanded.has("activity");
    const hasFindings = progress.finished && progress.success && progress.findings > 0;
    return Box({
      flexDirection: "column",
      marginTop: 1,
      children: [
        Box({
          flexDirection: "row",
          flexWrap: "wrap",
          columnGap: 1,
          alignItems: "center",
          children: [
            Text({ color: BRAND_ORANGE, bold: true, children: ["● CodeRabbit"] }),
            Box({
              flexDirection: "row",
              flexGrow: 1,
              flexWrap: "wrap",
              columnGap: 1,
              children: [
                Text({ children: [progress.label] }),
                ...(count ? [Text({ color: BRAND_ORANGE, children: ["· " + count] })] : []),
              ],
            }),
            ...(e.props.bodyColumns >= 70
              ? [Text({ dimColor: true, children: [progress.time] })]
              : []),
            ...(progress.finished && progress.canReviewAgain
              ? [
                  Button({
                    key: "review-again",
                    label: progress.retryRequested ? "Preparing" : "Run fresh review…",
                    onPress: () => expanded.delete("activity"),
                  }),
                ]
              : []),
            Button({
              key: "review-activity",
              label: hasFindings
                ? "View findings"
                : details
                  ? "Hide"
                  : progress.finished
                    ? "Details"
                    : "Activity",
              onPress: async () => {
                if (hasFindings) {
                  await showFindings($, resultRows.get(progress.reviewId));
                  return;
                }
                if (details) expanded.delete("activity");
                else expanded.add("activity");
                $.ui.invalidate("ui.render");
              },
            }),
            Button({
              key: "review-dismiss",
              role: "dismiss",
              label: "✕",
              plain: true,
              dimColor: true,
              onPress: () => {
                progress.dismissed = true;
                expanded.delete("activity");
                $.ui.invalidate("ui.render");
              },
            }),
          ],
        }),
        ...(details
          ? [
              Text({
                dimColor: true,
                children: [
                  "Scope: " +
                    progress.scope +
                    (e.props.bodyColumns < 70 ? " · Elapsed " + progress.time : "") +
                    (!progress.finished && Number.isInteger(progress.lastSignalSeconds)
                      ? " · Last update " +
                        Math.max(0, progress.elapsedSeconds - progress.lastSignalSeconds) +
                        "s ago"
                      : "") +
                    (progress.success && Number.isInteger(progress.reviewedFiles)
                      ? " · " +
                        progress.reviewedFiles +
                        (progress.reviewedFiles === 1 ? " file reviewed" : " files reviewed")
                      : "") +
                    (Object.keys(progress.severities).length
                      ? " · " +
                        Object.entries(progress.severities)
                          .map(([severity, count]) => count + " " + severity)
                          .join(" · ")
                      : ""),
                ],
              }),
              ...(progress.auth && !progress.finished && progress.authDetail
                ? [Text({ children: [progress.authDetail] })]
                : []),
              ...(progress.finished && progress.detail
                ? [Text({ children: [progress.detail] })]
                : []),
            ]
          : []),
        rest,
      ],
    });
  });

  on("ui.render", { component: "CommandOutput" }, async ($, e, next) => {
    if (e.props.command !== "coderabbit-review" || !e.props.text.startsWith("coderabbit-mod: "))
      return next(e);
    if (e.props.text === "coderabbit-mod: " + HELP) return renderHelp($, e, expanded);
    // Validation errors and process exceptions remain ordinary command output.
    let report;
    try {
      report = JSON.parse(e.props.text.slice("coderabbit-mod: ".length));
    } catch {
      return next(e);
    }
    if (report?.schema === "coderabbit-pending/1") {
      resultRows.set(report.id, e.requestId);
      const result = getResult(report.id);
      if (result === undefined) {
        const { Box, Text } = $.ui.resolve(e);
        const progress = getProgress();
        const auth =
          getActiveId() === report.id && progress?.reviewId === report.id && progress.auth;
        return Box({
          flexDirection: "row",
          flexWrap: "wrap",
          columnGap: 1,
          marginY: 1,
          children: [
            Text({ color: BRAND_ORANGE, bold: true, children: ["● CodeRabbit"] }),
            Text({
              dimColor: true,
              children: [
                getActiveId() === report.id
                  ? auth
                    ? progress.label + (progress.authDetail ? ". " + progress.authDetail : ".")
                    : "Reviewing in the background."
                  : "This review is no longer active; its result is unavailable in this conversation.",
              ],
            }),
          ],
        });
      }
      try {
        report = JSON.parse(result);
      } catch {
        return next({ ...e, props: { ...e.props, text: "coderabbit-mod: " + result } });
      }
    }
    if (report?.schema !== "coderabbit-review/1") return next(e);
    const { Box, Text, Button, Markdown } = $.ui.resolve(e);
    const limitId = e.requestId + ":rate-limit";
    const waitTime = report.rateLimit?.waitTime.trim();
    const hasWait = waitTime && !/^0\s+minutes?\s+and\s+0\s+seconds?$/i.test(waitTime);
    // Markdown has a 10,000-character limit and disallows terminal control codes.
    const guidance = (report.rateLimit?.guidance || report.rateLimit?.message || "").replace(
      /[\x00-\x08\x0b-\x1f\x7f]/g,
      "",
    );
    const summary = reviewSummary(report);
    const diagnosticId = e.requestId + ":diagnostics";
    return Box({
      flexDirection: "column",
      marginY: 1,
      children: [
        Box({
          flexDirection: "row",
          flexWrap: "wrap",
          columnGap: 2,
          children: [
            Text({ color: BRAND_ORANGE, bold: true, children: ["● CodeRabbit"] }),
            Text({ children: [summary.heading] }),
          ],
        }),
        ...(report.rateLimit
          ? [
              Box({
                flexDirection: "column",
                marginTop: 1,
                paddingLeft: 2,
                children: [
                  Text({
                    children: [
                      hasWait
                        ? "Try again in about " + waitTime + "."
                        : "No reset estimate from the CLI.",
                    ],
                  }),
                  Text({
                    dimColor: true,
                    children: [
                      "This review didn't complete. Your account may also need attention; view limit details.",
                    ],
                  }),
                  Box({
                    marginTop: 1,
                    children: [
                      Button({
                        key: "rate-limit-details",
                        label: expanded.has(limitId) ? "Hide limit details" : "View limit details",
                        onPress: () => {
                          if (expanded.has(limitId)) expanded.delete(limitId);
                          else expanded.add(limitId);
                          $.ui.invalidate("ui.render");
                        },
                      }),
                    ],
                  }),
                  ...(expanded.has(limitId)
                    ? [
                        Markdown({ text: guidance.slice(0, 10000) }),
                        ...(guidance.length > 10000
                          ? [Text({ dimColor: true, children: ["Limit details truncated."] })]
                          : []),
                      ]
                    : []),
                ],
              }),
            ]
          : []),
        ...(summary.detail ? [Text({ children: [summary.detail] })] : []),
        ...(report.notices.length
          ? [
              Box({
                marginTop: 1,
                children: [
                  Button({
                    key: "review-diagnostics",
                    label: expanded.has(diagnosticId) ? "Hide details" : "View details",
                    onPress: () => {
                      if (expanded.has(diagnosticId)) expanded.delete(diagnosticId);
                      else expanded.add(diagnosticId);
                      $.ui.invalidate("ui.render");
                    },
                  }),
                ],
              }),
              ...(expanded.has(diagnosticId)
                ? report.notices.map((notice) => Text({ children: [notice] }))
                : []),
            ]
          : []),
        ...(report.truncated
          ? [
              Text({
                children: [
                  report.rateLimit
                    ? "Display truncated. Some CLI details were omitted."
                    : "Display truncated. Run coderabbit review findings in this workspace to inspect all saved findings.",
                ],
              }),
            ]
          : []),
        ...report.findings.map((finding, index) => {
          const id = e.requestId + ":" + index;
          // Promote only a short, verbatim opening sentence or clause. The CLI
          // agent stream has no title; never invent a diagnosis from its prose.
          const lead =
            /^(.{1,160}?)(?:\r?\n+|(?<=[.!?])\s+|\s+(?=so |before |because ))([\s\S]+)$/.exec(
              finding.body,
            );
          const shortBody = !lead && finding.body.length <= 160;
          const title = lead ? lead[1] : shortBody ? finding.body : finding.location;
          const description = lead ? lead[2] : shortBody ? "" : finding.body;
          const severity = finding.severity.toLowerCase();
          const prominent = ["critical", "major"].includes(severity);
          return Box({
            flexDirection: "column",
            marginTop: index === 0 ? 1 : 2,
            children: [
              Text({ bold: true, children: [title] }),
              Text({
                children: [
                  Text({
                    ...(prominent ? { color: BRAND_ORANGE } : { dimColor: true }),
                    children: [severity.charAt(0).toUpperCase() + severity.slice(1)],
                  }),
                  ...(title !== finding.location
                    ? [Text({ dimColor: true, children: [" · " + finding.location] })]
                    : []),
                ],
              }),
              ...(description ? [Text({ children: [description] })] : []),
              Box({
                flexDirection: "row",
                flexWrap: "wrap",
                columnGap: 1,
                marginTop: 1,
                children: [
                  ...(finding.suggestions.length
                    ? [
                        Button({
                          key: "suggestion-" + index,
                          label: expanded.has(id) ? "Hide suggestion" : "View suggestion",
                          onPress: () => {
                            if (expanded.has(id)) expanded.delete(id);
                            else expanded.add(id);
                            $.ui.invalidate("ui.render");
                          },
                        }),
                      ]
                    : []),
                  Button({
                    key: "draft-" + index,
                    label: "Fix with Claude",
                    onPress: async () => {
                      const result = await $.prompt.fill({
                        text:
                          "\nFix CodeRabbit finding " +
                          (index + 1) +
                          " at " +
                          JSON.stringify(finding.location) +
                          ". Verify it against the current code. If valid, make the smallest appropriate change and run the relevant checks. If it no longer applies, explain why.\n\nCodeRabbit finding (reference):\n" +
                          finding.body +
                          (finding.suggestions.length
                            ? "\n\nSuggested changes (reference):\n" +
                              finding.suggestions.join("\n\n")
                            : ""),
                        mode: "append",
                      });
                      if (!result.isFilled)
                        $.ui.toast(
                          "Could not add the draft. Try again when the prompt is available.",
                        );
                      else $.ui.toast("Fix request added to your draft.");
                    },
                  }),
                ],
              }),
              ...(expanded.has(id)
                ? finding.suggestions.map((suggestion) => Text({ children: [suggestion] }))
                : []),
            ],
          });
        }),
        ...(report.rateLimit
          ? [
              Box({
                marginTop: 1,
                children: [Text({ dimColor: true, children: ["No automatic retry"] })],
              }),
            ]
          : []),
      ],
    });
  });
}

// Kept separate so host scroll denial and failure can be checked without a
// transcript window; the native test runner has no ui.scroll implementation.
export async function showFindings($, requestId) {
  if (!requestId) {
    $.ui.toast("Run /coderabbit-review results to reopen the findings.");
    return;
  }
  try {
    const result = await $.ui.scroll({ to: { requestId }, block: "start" });
    if (result.deny) $.ui.toast("Run /coderabbit-review results to reopen the findings.");
  } catch {
    $.ui.toast("Could not open findings. Run /coderabbit-review results.");
  }
}

function renderHelp($, e, expanded) {
  const { Box, Text, Button } = $.ui.resolve(e);
  const advancedId = e.requestId + ":help-advanced";
  const setupId = e.requestId + ":help-setup";
  const advanced = expanded.has(advancedId);
  const setup = expanded.has(setupId);
  return Box({
    flexDirection: "column",
    marginY: 1,
    children: [
      Box({
        flexDirection: "row",
        flexWrap: "wrap",
        columnGap: 2,
        children: [
          Text({ color: BRAND_ORANGE, bold: true, children: ["● CodeRabbit"] }),
          Text({ children: ["Review guide"] }),
        ],
      }),
      Text({ dimColor: true, children: ["Review your changes while you keep chatting."] }),
      ...HELP_ACTIONS.map(([command, description]) =>
        Box({
          flexDirection: "column",
          marginTop: 1,
          children: [
            Text({ bold: true, children: [command] }),
            Text({ dimColor: true, children: [description] }),
          ],
        }),
      ),
      Box({
        flexDirection: "row",
        flexWrap: "wrap",
        columnGap: 1,
        marginTop: 1,
        children: [
          Button({
            key: "help-advanced",
            label: advanced ? "Hide options" : "Advanced options",
            onPress: () => {
              if (advanced) expanded.delete(advancedId);
              else expanded.add(advancedId);
              $.ui.invalidate("ui.render");
            },
          }),
          Button({
            key: "help-setup",
            label: setup ? "Hide setup" : "Setup and details",
            onPress: () => {
              if (setup) expanded.delete(setupId);
              else expanded.add(setupId);
              $.ui.invalidate("ui.render");
            },
          }),
        ],
      }),
      ...(advanced
        ? [
            Text({ dimColor: true, children: ["Add these after /coderabbit-review."] }),
            ...HELP_ADVANCED.map(([option, description]) =>
              Box({
                flexDirection: "column",
                marginTop: 1,
                children: [
                  Text({ bold: true, children: [option] }),
                  Text({ children: [description] }),
                ],
              }),
            ),
          ]
        : []),
      ...(setup
        ? HELP_SETUP.map((text) => Box({ marginTop: 1, children: [Text({ children: [text] })] }))
        : []),
      Box({
        marginTop: 1,
        children: [
          Text({ dimColor: true, children: ["Selected code is sent to CodeRabbit for review."] }),
        ],
      }),
    ],
  });
}
