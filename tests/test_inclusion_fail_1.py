"""
Inclusion test fail case1
"""
import subprocess

def test_inclusion():
    """
    Using wrong logID
    """
    result = subprocess.run(
        ["python", "rekor_monitor_jacksonqu/main.py",
         "--inclusion", "123456789",
         "--artifact", "artifact.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, "The program should throw an error, but it doesn't."

if __name__ == "__main__":
    test_inclusion()
