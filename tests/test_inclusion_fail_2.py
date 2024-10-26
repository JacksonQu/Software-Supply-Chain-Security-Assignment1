import subprocess

def test_inclusion():
    """
    Using wrong artifact
    """
    result = subprocess.run(
        ["python", "main.py",
         "--inclusion", "128595953",
         "--artifact", "README.md"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 1, "The program should throw an error, but it doesn't."

if __name__ == "__main__":
    test_inclusion()