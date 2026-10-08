"""Contracts for the public builder's bounded native AI startup wait.

These tests execute only the already-public workflow snippet, never private
product code. They do not replace the real frozen Windows/Qwen journey.
"""
import ast
from pathlib import Path
import textwrap
import unittest


WORKFLOW = Path(__file__).resolve().parents[1] / '.github/workflows/build-windows.yml'


def startup_wait_source():
    workflow = WORKFLOW.read_text(encoding='utf-8')
    block = workflow.split('$replacement = @(', 1)[1].split(
        ') -join [Environment]::NewLine', 1)[0]
    lines = []
    for raw in block.splitlines():
        value = raw.strip()
        if not value or value.startswith('#'):
            continue
        lines.append(ast.literal_eval(value))
    return textwrap.dedent('\n'.join(lines))


def execute_wait(states, source=None):
    class Clock:
        elapsed = 0

        def monotonic(self):
            return self.elapsed

        def sleep(self, seconds):
            if seconds != 1:
                raise AssertionError('Startup wait polling interval changed')
            self.elapsed += seconds
            if self.elapsed > 400:
                raise RuntimeError('Startup wait lost its finite deadline')

    clock = Clock()
    seen = []

    def state():
        value = states[min(len(seen), len(states) - 1)]
        seen.append(value)
        return value

    namespace = {'time': clock, 'state': state}
    try:
        exec(compile(source or startup_wait_source(), '<builder-startup-wait>', 'exec'), namespace)
    except AssertionError as exc:
        exc.observed_wait_seconds = clock.elapsed
        raise
    return namespace['initial_state'], clock.elapsed, len(seen)


def busy(*blockers):
    return {'eligibility_code': 'BUSY', 'blockers': list(blockers)}


READY = {'eligibility_code': 'ELIGIBLE', 'blockers': []}


class NativeAiStartupWaitTests(unittest.TestCase):
    def test_observed_backup_and_update_startup_can_finish(self):
        result, elapsed, observations = execute_wait([busy('backup', 'update'), busy('update'), READY])
        self.assertEqual(result, READY)
        self.assertEqual(elapsed, 2)
        self.assertEqual(observations, 3)

    def test_backup_only_keeps_existing_wait_behavior(self):
        result, elapsed, _ = execute_wait([busy('backup'), READY])
        self.assertEqual((result, elapsed), (READY, 1))

    def test_ready_state_does_not_wait(self):
        self.assertEqual(execute_wait([READY]), (READY, 0, 1))

    def test_other_priority_operations_are_rejected(self):
        for blocker in ('restore', 'maintenance', 'import', 'unknown'):
            with self.subTest(blocker=blocker), self.assertRaises(AssertionError):
                execute_wait([busy('backup', blocker), READY])

    def test_busy_without_owner_is_rejected(self):
        with self.assertRaises(AssertionError):
            execute_wait([busy(), READY])

    def test_stuck_background_work_still_fails_at_original_deadline(self):
        with self.assertRaises(AssertionError) as failure:
            execute_wait([busy('update')])
        self.assertEqual(failure.exception.observed_wait_seconds, 330)
        self.assertIn('initial_deadline = time.monotonic() + 330', startup_wait_source())

    def test_removing_priority_allowlist_is_detected(self):
        source = startup_wait_source()
        guard = next(line for line in source.splitlines() if 'assert ' in line and 'blockers' in line)
        mutated = source.replace(guard, guard[:len(guard) - len(guard.lstrip())] + 'pass', 1)
        with self.assertRaises(AssertionError):
            execute_wait([busy('restore'), READY], source=source)
        result, _, _ = execute_wait([busy('restore'), READY], source=mutated)
        self.assertEqual(result, READY)

    def test_real_model_and_resource_checks_remain_mandatory(self):
        workflow = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('assert initial_state["eligibility_code"] != "BUSY", initial_state', startup_wait_source())
        self.assertIn("if ($testExitCode -ne 0) { throw 'Modello AI reale Windows non superato.' }", workflow)
        self.assertIn('"windows_frozen_real_model":\\s*"PASS"', workflow)
        self.assertIn('Exercise real Qwen model under Windows resource guard', workflow)
        self.assertIn('Exercise native RTF printing on disposable Windows printer', workflow)
        self.assertIn('Smoke test installer and installed application', workflow)


if __name__ == '__main__':
    unittest.main()
