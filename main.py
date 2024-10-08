import argparse
import base64
import json
import requests
from util import extract_public_key, verify_artifact_signature
from merkle_proof import DefaultHasher, verify_consistency, verify_inclusion, compute_leaf_hash

def get_log_entry(log_index, debug=False):
    # verify that log index value is sane
    url = f'https://rekor.sigstore.dev/api/v1/log/entries?logIndex={log_index}'
    header = {'accept': 'application/json'}
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        return response.json()
    else:
        return {}
    pass

def get_proof(size1: int, size2: int, debug=False):
    size1 = int(size1)
    size2 = int(size2)
    if size1 > size2:
        raise ValueError(f'Size1({size1}) must smaller than size2({size2})')
    url = f'https://rekor.sigstore.dev/api/v1/log/proof?firstSize={size1}&lastSize={size2}'
    header = {'accept': 'application/json'}
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

def get_verification_proof(log_index, debug=False):
    # verify that log index value is sane
    return get_proof(1, log_index)
    pass

def inclusion(log_index, artifact_filepath, debug=False):
    # verify that log index and artifact filepath values are sane
    log_entry = get_log_entry(log_index)
    # print(json.dumps(log_entry, indent=4))
    outer_key = next(iter(log_entry))
    decoded_body = base64.b64decode(log_entry[outer_key]['body'])
    log_entry_body = json.loads(decoded_body)
    # print(json.dumps(log_entry_body, indent=4))
    signature = log_entry_body['spec']['signature']['content']
    decoded_sig = base64.b64decode(signature)
    certificate = log_entry_body['spec']['signature']['publicKey']['content']
    decoded_cert = base64.b64decode(certificate)
    public_key = extract_public_key(decoded_cert)
    verify_artifact_signature(decoded_sig, public_key, artifact_filepath)
    # verification_proof = get_verification_proof(log_entry[outer_key]['verification']['inclusionProof']['logIndex'])
    # print(json.dumps(verification_proof, indent=4))
    index = log_entry[outer_key]['verification']['inclusionProof']['logIndex']
    tree_size = log_entry[outer_key]['verification']['inclusionProof']['treeSize']
    leaf_hash = compute_leaf_hash(log_entry[outer_key]['body'])
    hashes = log_entry[outer_key]['verification']['inclusionProof']['hashes']
    root_hash = log_entry[outer_key]['verification']['inclusionProof']['rootHash']
    verify_inclusion(DefaultHasher, index, tree_size, leaf_hash, hashes, root_hash)
    print('Offline root hash calculation for inclusion verified.')
    pass

def get_latest_checkpoint(debug=False):
    url = 'https://rekor.sigstore.dev/api/v1/log?stable=true'
    header = {'accept': 'application/json'}
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        return response.json()
    else:
        return {}
    pass

def consistency(prev_checkpoint, debug=False):
    # verify that prev checkpoint is not empty
    ckpt = get_latest_checkpoint()
    # tree_id = prev_checkpoint['treeID']
    tree_size = prev_checkpoint['treeSize']
    root_hash = prev_checkpoint['rootHash']
    proof = get_proof(tree_size, ckpt['treeSize'])
    verify_consistency(DefaultHasher, tree_size, ckpt['treeSize'], proof['hashes'], root_hash, ckpt['rootHash'])
    print('Consistency verification successful.')
    pass

def main():
    debug = False
    parser = argparse.ArgumentParser(description="Rekor Verifier")
    parser.add_argument('-d', '--debug', help='Debug mode',
                        required=False, action='store_true') # Default false
    parser.add_argument('-c', '--checkpoint', help='Obtain latest checkpoint\
                        from Rekor Server public instance',
                        required=False, action='store_true')
    parser.add_argument('--inclusion', help='Verify inclusion of an\
                        entry in the Rekor Transparency Log using log index\
                        and artifact filename.\
                        Usage: --inclusion 126574567',
                        required=False, type=int)
    parser.add_argument('--artifact', help='Artifact filepath for verifying\
                        signature',
                        required=False)
    parser.add_argument('--consistency', help='Verify consistency of a given\
                        checkpoint with the latest checkpoint.',
                        action='store_true')
    parser.add_argument('--tree-id', help='Tree ID for consistency proof',
                        required=False)
    parser.add_argument('--tree-size', help='Tree size for consistency proof',
                        required=False, type=int)
    parser.add_argument('--root-hash', help='Root hash for consistency proof',
                        required=False)
    args = parser.parse_args()
    if args.debug:
        debug = True
        print("enabled debug mode")
    if args.checkpoint:
        # get and print latest checkpoint from server
        # if debug is enabled, store it in a file checkpoint.json
        checkpoint = get_latest_checkpoint(debug)
        print(json.dumps(checkpoint, indent=4))
    if args.inclusion:
        inclusion(args.inclusion, args.artifact, debug)
    if args.consistency:
        if not args.tree_id:
            print("please specify tree id for prev checkpoint")
            return
        if not args.tree_size:
            print("please specify tree size for prev checkpoint")
            return
        if not args.root_hash:
            print("please specify root hash for prev checkpoint")
            return

        prev_checkpoint = {}
        prev_checkpoint["treeID"] = args.tree_id
        prev_checkpoint["treeSize"] = args.tree_size
        prev_checkpoint["rootHash"] = args.root_hash

        consistency(prev_checkpoint, debug)

if __name__ == "__main__":
    main()
