"""
Inclusion test fail case2
"""
import subprocess

def test_inclusion():
    """
    Using wrong artifact
    """
    result = subprocess.run(
        ["python", "rekor_monitor_jacksonqu/main.py",
         "--inclusion", "128595953",
         "--artifact", "README.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, "The program should throw an error, but it doesn't."

if __name__ == "__main__":
    test_inclusion()
