# Python Rekor Monitor

Verify your software using trusted supply chains.

## Description

This repository uses `Rekor API`, a tool that helps improve security in software supply chains by providing immutable records of software build metadata. This repository includes code that interacts with Rekor's API and verifies the consistency using transparency logs.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/JacksonQu/Software-Supply-Chain-Security-Assignment1.git
cd Software-Supply-Chain-Security-Assignment1/
```

2. (Optional) Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install cryptography requests
```

## Usage

- Fetch a checkpoint of Rekor transparency log.

```bash
python main.py -c
```

- Verify the artifact signature.

```bash
python main.py --inclusion {logIndex} --artifact {filepath}
```

- Verify merkle tree consistency.

```bash
python main.py --consistency --tree-id {treeID} --tree-size {treeSize} --root-hash {hash}
```

## Reference

- Fork from [mayank-ramnani/python-rekor-monitor-template](https://github.com/mayank-ramnani/python-rekor-monitor-template)

- [Rekor API Sepc](https://www.sigstore.dev/swagger/#/)
