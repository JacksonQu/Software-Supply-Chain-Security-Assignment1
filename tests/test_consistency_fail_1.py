"""
Consistency test fail case1
"""
import subprocess

def test_consistency():
    """
    Using wrong tree-id
    It will not affect the consistency verification results
    """
    result = subprocess.run(
        ["python", "rekor_monitor_jacksonqu/main.py", "--consistency",
         "--tree-id", "1234567",
         "--tree-size", "21769644",
         "--root-hash",
         "cadc0252423f2b41489c10c4b848b034bad90903be100a7c5877f4f98d6f5b6f"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Test failed. Error message:\n{result.stderr}"

if __name__ == "__main__":
    test_consistency()
