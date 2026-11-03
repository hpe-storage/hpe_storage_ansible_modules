from __future__ import annotations

from ansible.plugins.callback import CallbackBase


DOCUMENTATION = """
    name: minimal_progress
    type: stdout
    short_description: Phase-grouped progress output with clear status and errors
    description:
        - Groups tasks under human-readable phase banners (Preflight, Discovery, ...).
        - Prints a single status line per task (PASSED / CHANGED / INFO / OK).
        - Hides internal plumbing steps (set_fact/stat captures) unless they fail.
        - Surfaces debug 'msg' and 'var' output, including lists and empty values.
        - Calls out failures and unreachable hosts prominently in red.
    requirements:
        - set as stdout_callback in ansible.cfg
"""


# Ordered (substring, phase title). First matching substring wins. Substrings are
# matched against the resolved task name, so templated names (e.g. "... failover ...")
# are matched on a stable fragment.
PHASES = [
    ("Validate replication action", "Preflight Validation"),
    ("Validate replication target", "Preflight Validation"),
    ("OpenStack credentials file", "Cinder Service Discovery"),
    ("Query cinder-volume service inventory", "Cinder Service Discovery"),
    ("Confirm Cinder API is reachable", "Cinder Service Discovery"),
    ("Parse cinder-volume service inventory", "Cinder Service Discovery"),
    ("Select the target cinder-volume backend", "Cinder Service Discovery"),
    ("Verify target backend is online", "Cinder Service Discovery"),
    ("Verify target replication status permits failover", "Cinder Service Discovery"),
    ("Discover configured replication targets", "Backend Policy Validation"),
    ("Resolve permitted replication backend_ids", "Backend Policy Validation"),
    ("Validate requested backend_id", "Backend Policy Validation"),
    ("Report backend already in desired state", "Idempotency Gate"),
    ("End play when no replication change", "Idempotency Gate"),
    ("Capture pre-change", "Replication Execution"),
    ("Execute Cinder", "Replication Execution"),
    ("Wait for replication_status", "Replication Execution"),
    ("transition completed", "Replication Execution"),
    ("Capture post-change", "Post-Change Verification"),
    ("Report target backend details", "Post-Change Verification"),
]

# Internal plumbing tasks: run silently on success, only surface on failure.
HIDDEN = [
    "OpenStack credentials file",
    "Parse cinder-volume service inventory",
    "Select the target cinder-volume backend",
    "Resolve permitted replication backend_ids",
    "Capture pre-change",
    "Capture post-change",
]


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "minimal_progress"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_phase = None
        self._pending_phase = None
        self._task_name = ""
        self._task_hidden = False
        self._header_printed = False

    # -- helpers -----------------------------------------------------------
    @staticmethod
    def _phase_for(name):
        for needle, title in PHASES:
            if needle in name:
                return title
        return None

    @staticmethod
    def _is_hidden(name):
        return any(needle in name for needle in HIDDEN)

    @staticmethod
    def _action_name(action):
        return action.rsplit(".", 1)[-1]

    def _flush_phase(self):
        if self._pending_phase is not None:
            self._display.display("")
            self._display.display("=== %s ===" % self._pending_phase, color="bright blue")
            self._pending_phase = None

    def _ensure_task_header(self):
        # Print the phase banner and the task arrow exactly once per task.
        if not self._header_printed:
            self._flush_phase()
            self._display.display("")
            self._display.display("  -> %s" % self._task_name, color="cyan")
            self._header_printed = True

    def _display_value(self, value):
        # Render strings, lists, and other debug values without dropping empties.
        if isinstance(value, (list, tuple)):
            if not value:
                self._display.display("       DONE", color="green")
                return
            for item in value:
                self._display.display("       %s" % item, color="green")
            return
        text = str(value)
        if text == "":
            self._display.display("       DONE", color="green")
            return
        for line in text.splitlines():
            self._display.display("       %s" % line, color="green")

    # -- play / task lifecycle --------------------------------------------
    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if name:
            self._display.banner(name)

    def v2_playbook_on_task_start(self, task, is_conditional):
        # meta tasks (e.g. end_play) are control flow, not user-facing steps.
        if task.action == "meta":
            return
        self._task_name = task.get_name().strip()
        self._task_hidden = self._is_hidden(self._task_name)
        self._header_printed = False
        phase = self._phase_for(self._task_name)
        if phase is not None and phase != self._current_phase:
            self._current_phase = phase
            self._pending_phase = phase
        if not self._task_hidden:
            self._ensure_task_header()
            #self._display.display("     RUNNING", color="cyan")

    # -- results -----------------------------------------------------------
    def v2_runner_on_ok(self, result):
        res = result._result
        action = self._action_name(result._task.action)
        emitted = False

        if res.get("changed", False):
            self._ensure_task_header()
            self._display.display("     CHANGED", color="yellow")
            emitted = True

        msg = res.get("msg")
        if action == "assert" or msg == "All assertions passed":
            if not self._task_hidden:
                self._ensure_task_header()
                self._display.display("     PASSED", color="green")
            return

        # Only debug tasks intentionally surface content; shell/command msg is noise.
        if action == "debug":
            if msg is None:
                # `debug: var: x` stores the value under the var name, not under "msg".
                var_name = result._task.args.get("var")
                if var_name is not None:
                    msg = res.get(var_name)
            self._ensure_task_header()
            self._display.display("     INFO", color="green")
            if msg is None:
                self._display.display("       (no output returned)", color="green")
            else:
                self._display_value(msg)
            emitted = True

        # Plain visible steps (shell with no reported output) still get a confirmation.
        if not emitted and not self._task_hidden:
            self._ensure_task_header()
            self._display.display("     OK", color="green")

    def v2_runner_on_skipped(self, result):
        if not self._task_hidden:
            self._ensure_task_header()
            self._display.display("     CONDITION NOT MET", color="green")

    def v2_runner_on_failed(self, result, ignore_errors=False):
        res = result._result
        msg = res.get("msg") or "task failed"
        # Force the task context to appear even for hidden/plumbing steps.
        self._ensure_task_header()
        self._display.display("     FAILED", color="red")
        for line in str(msg).splitlines():
            self._display.display("       %s" % line, color="red")
        if res.get("rc") is not None:
            self._display.display("       exit code: %s" % res["rc"], color="red")
        if res.get("cmd"):
            self._display.display("       command: %s" % res["cmd"], color="red")
        for key, label in (("stderr", "stderr"), ("stdout", "stdout")):
            value = res.get(key)
            if value:
                self._display.display("       %s:" % label, color="red")
                for line in str(value).splitlines():
                    self._display.display("         %s" % line, color="red")

    def v2_runner_on_unreachable(self, result):
        msg = result._result.get("msg") or "host unreachable"
        self._ensure_task_header()
        self._display.display("     UNREACHABLE", color="red")
        for line in str(msg).splitlines():
            self._display.display("       %s" % line, color="red")

    def v2_runner_retry(self, result):
        # Suppress the noisy "FAILED - RETRYING ..." line.
        pass

    # -- summary -----------------------------------------------------------
    def v2_playbook_on_stats(self, stats):
        self._display.display("")
        self._display.display("=== Summary ===", color="bright blue")
        for host in sorted(stats.processed.keys()):
            s = stats.summarize(host)
            failed = bool(s["failures"] or s["unreachable"])
            color = "red" if failed else "green"
            verdict = "FAILED" if failed else "SUCCESS"
            self._display.display(
                "  %s : %s (ok=%d changed=%d failed=%d unreachable=%d skipped=%d)"
                % (
                    host,
                    verdict,
                    s["ok"],
                    s["changed"],
                    s["failures"],
                    s["unreachable"],
                    s["skipped"],
                ),
                color=color,
            )
