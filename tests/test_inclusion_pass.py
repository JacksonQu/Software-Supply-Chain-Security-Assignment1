"""
Inclusion test pass case
"""
import subprocess

def test_inclusion():
    """
    Test whether the inclusion function is working properly
    """
    result = subprocess.run(
        ["python", "rekor_monitor_jacksonqu/main.py",
         "--inclusion", "128595953",
         "--artifact", "artifact.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Test failed. Error message:\n{result.stderr}"

if __name__ == "__main__":
    test_inclusion()
