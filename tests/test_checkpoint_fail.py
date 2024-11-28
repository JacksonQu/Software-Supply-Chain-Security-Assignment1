"""
Checkpoint test fail case
"""
import os
import subprocess

checkpoint_schema = {
    "type": "object",
    "properties": {
        "inactiveShards": {"type": "array"},
        "rootHash": {"type": "string"},
        "signedTreeHead": {"type": "string"},
        "treeID": {"type": "string"},
        "treeSize": {"type": "integer"}
    },
    "required": ["inactiveShards", "rootHash", "signedTreeHead", "treeID", "treeSize"]
}

env = os.environ.copy()
env["http_proxy"] = "http://0.0.0.0:0"
env["https_proxy"] = "http://0.0.0.0:0"

def test_checkpoint():
    """
    Test whether the checkpoint function is normal
    This test case uses an invalid local proxy to simulate network request
    failure
    """
    result = subprocess.run(
        ["python", "rekor_monitor_jacksonqu/main.py", "-c"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, "The program should throw an error, but it doesn't."

if __name__ == "__main__":
    test_checkpoint()
