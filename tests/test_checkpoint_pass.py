import json
import os
from jsonschema import validate
import subprocess

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
    result = subprocess.run(
        ["python", "rekor_monitor_jacksonqu/main.py", "-c"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Test failed. Error message:\n{result.stderr}"
    output = result.stdout
    data = json.loads(output)
    validate(instance=data, schema=checkpoint_schema)

if __name__ == "__main__":
    test_checkpoint()
