"""Phase-1 TDD: kill_switch.py — manual stop via a KILL file + PID + interruptible sleep."""
from harness_core.kill_switch import KillSwitch


def test_not_killed_initially(tmp_path):
    assert KillSwitch(str(tmp_path / "KILL")).is_killed() is False


def test_arm_sets_killed(tmp_path):
    ks = KillSwitch(str(tmp_path / "KILL"))
    ks.arm()
    assert ks.is_killed() is True


def test_disarm_clears(tmp_path):
    ks = KillSwitch(str(tmp_path / "KILL"))
    ks.arm()
    ks.disarm()
    assert ks.is_killed() is False


def test_write_and_read_pid(tmp_path):
    ks = KillSwitch(str(tmp_path / "KILL"), pid_path=str(tmp_path / "PID"))
    ks.write_pid(4242)
    assert ks.read_pid() == 4242


def test_read_pid_none_when_absent(tmp_path):
    assert KillSwitch(str(tmp_path / "KILL"), pid_path=str(tmp_path / "PID")).read_pid() is None


def test_sleep_interruptible_returns_early_when_killed(tmp_path):
    ks = KillSwitch(str(tmp_path / "KILL"))
    slept = []

    def fake_sleep(s):
        slept.append(s)
        ks.arm()  # kill arrives during the first chunk

    assert ks.sleep_interruptible(100, chunk=10, sleeper=fake_sleep) is True
    assert len(slept) == 1  # stopped after first chunk, not 10


def test_sleep_interruptible_completes_when_not_killed(tmp_path):
    ks = KillSwitch(str(tmp_path / "KILL"))
    slept = []
    assert ks.sleep_interruptible(30, chunk=10, sleeper=slept.append) is False
    assert sum(slept) == 30
    assert len(slept) == 3
