"""
Checkpoint test pass case
"""
import json
import subprocess
from jsonschema import validate

# env = os.environ.copy()
# env["PYTHONPATH"] = os.path.abspath("rekor_monitor_jacksonqu")

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

def test_checkpoint():
    """
    Test whether the checkpoint function is normal
    """
    result = subprocess.run(
        ["python", "rekor_monitor_jacksonqu/main.py", "-c"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Test failed. Error message:\n{result.stderr}"
    output = result.stdout
    data = json.loads(output)
    validate(instance=data, schema=checkpoint_schema)

if __name__ == "__main__":
    test_checkpoint()
