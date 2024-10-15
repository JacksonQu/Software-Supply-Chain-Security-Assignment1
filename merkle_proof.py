"""
merkle_proof.py
"""
import hashlib
import binascii
import base64

# domain separation prefixes according to the RFC
RFC6962_LEAF_HASH_PREFIX = 0
RFC6962_NODE_HASH_PREFIX = 1


class Hasher:
    """
    Class Hasher
    """
    def __init__(self, hash_func=hashlib.sha256):
        self.hash_func = hash_func

    def new(self):
        """
        Create a new instance of the hash function.
        """
        return self.hash_func()

    def empty_root(self):
        """
        Generate the hash digest for an empty root.
        """
        return self.new().digest()

    def hash_leaf(self, leaf):
        """
        Hash a leaf node.
        """
        hnode = self.new()
        hnode.update(bytes([RFC6962_LEAF_HASH_PREFIX]))
        hnode.update(leaf)
        return hnode.digest()

    def hash_children(self, left, right):
        """
        Hash two child nodes.
        """
        hnode = self.new()
        byte = bytes([RFC6962_NODE_HASH_PREFIX]) + left + right
        hnode.update(byte)
        return hnode.digest()

    def size(self):
        """
        Get the size of the hash digest produced by the current hash function.
        """
        return self.new().digest_size


# DefaultHasher is a SHA256 based LogHasher
DefaultHasher = Hasher(hashlib.sha256)


def verify_consistency(hasher, size, proof, root1, root2):
    """
    Verify the consistency of two Merkle tree roots.
    """
    # change format of args to be bytearray instead of hex strings
    root1 = bytes.fromhex(root1)
    root2 = bytes.fromhex(root2)
    bytearray_proof = []
    for elem in proof:
        bytearray_proof.append(bytes.fromhex(elem))

    if size[1] < size[0]:
        raise ValueError(f"size2 ({size[1]}) < size1 ({size[0]})")
    if size[0] == size[1]:
        if bytearray_proof:
            raise ValueError("size1=size2, but bytearray_proof is not empty")
        verify_match(root1, root2)
        return
    if size[0] == 0:
        if bytearray_proof:
            raise ValueError(
                f"expected empty bytearray_proof, but got {len(bytearray_proof)} components"
            )
        return
    if not bytearray_proof:
        raise ValueError("empty bytearray_proof")

    inner, border = decomp_incl_proof(size[0] - 1, size[1])
    shift = (size[0] & -size[0]).bit_length() - 1
    inner -= shift

    if size[0] == 1 << shift:
        seed, start = root1, 0
    else:
        seed, start = bytearray_proof[0], 1

    if len(bytearray_proof) != start + inner + border:
        raise ValueError(
            f"wrong bytearray_proof size {len(bytearray_proof)}, want {start + inner + border}"
        )

    bytearray_proof = bytearray_proof[start:]

    mask = (size[0] - 1) >> shift
    hash1 = chain_inner_right(hasher, seed, bytearray_proof[:inner], mask)
    hash1 = chain_border_right(hasher, hash1, bytearray_proof[inner:])
    verify_match(hash1, root1)

    hash2 = chain_inner(hasher, seed, bytearray_proof[:inner], mask)
    hash2 = chain_border_right(hasher, hash2, bytearray_proof[inner:])
    verify_match(hash2, root2)


def verify_match(calculated, expected):
    """
    Compare two values to verify they match.
    """
    if calculated != expected:
        raise RootMismatchError(expected, calculated)


def decomp_incl_proof(index, size):
    """
    Decompose an inclusive proof for a given index and size.
    """
    inner = inner_proof_size(index, size)
    border = bin(index >> inner).count("1")
    return inner, border


def inner_proof_size(index, size):
    """
    Calculate the size of the inner proof.
    """
    return (index ^ (size - 1)).bit_length()


def chain_inner(hasher, seed, proof, index):
    """
    Compute the inner hash chain for a Merkle tree inclusion proof.
    """
    for i, hnode in enumerate(proof):
        if (index >> i) & 1 == 0:
            seed = hasher.hash_children(seed, hnode)
        else:
            seed = hasher.hash_children(hnode, seed)
    return seed


def chain_inner_right(hasher, seed, proof, index):
    """
    Compute the right-side inner hash chain for a Merkle tree proof.
    """
    for i, hnode in enumerate(proof):
        if (index >> i) & 1 == 1:
            seed = hasher.hash_children(hnode, seed)
    return seed


def chain_border_right(hasher, seed, proof):
    """
    Compute the hash chain for the border nodes in a Merkle tree proof.
    """
    for hnode in proof:
        seed = hasher.hash_children(hnode, seed)
    return seed


class RootMismatchError(Exception):
    """
    Exception RootMismatchError
    """
    def __init__(self, expected_root, calculated_root):
        super().__init__()
        self.expected_root = binascii.hexlify(bytearray(expected_root))
        self.calculated_root = binascii.hexlify(bytearray(calculated_root))

    def __str__(self):
        return f"calculated root:\n{self.calculated_root}\n does not match \
                 expected root:\n{self.expected_root}"


def root_from_inclusion_proof(hasher, index, size, leaf_hash, proof):
    """
    Calculate the Merkle root from an inclusion
    proof for a specified leaf node.
    """
    if index >= size:
        raise ValueError(f"index is beyond size: {index} >= {size}")

    if len(leaf_hash) != hasher.size():
        raise ValueError(
            f"leaf_hash has unexpected size {len(leaf_hash)}, want {hasher.size()}"
        )

    inner, border = decomp_incl_proof(index, size)
    if len(proof) != inner + border:
        raise ValueError(f"wrong proof size {len(proof)}, want {inner + border}")

    res = chain_inner(hasher, leaf_hash, proof[:inner], index)
    res = chain_border_right(hasher, res, proof[inner:])
    return res


def verify_inclusion(hasher, args, debug=False):
    """
    Verify the inclusion of a leaf node in a Merkle
    tree using the provided proof and parameters.
    """
    index, size, leaf_hash, proof, root = args
    bytearray_proof = []
    for elem in proof:
        bytearray_proof.append(bytes.fromhex(elem))

    bytearray_root = bytes.fromhex(root)
    bytearray_leaf = bytes.fromhex(leaf_hash)
    calc_root = root_from_inclusion_proof(
        hasher, index, size, bytearray_leaf, bytearray_proof
    )
    verify_match(calc_root, bytearray_root)
    if debug:
        print("Calculated root hash", calc_root.hex())
        print("Given root hash", bytearray_root.hex())


# requires entry["body"] output for a log entry
# returns the leaf hash according to the rfc 6962 spec
def compute_leaf_hash(body):
    """
    Compute the SHA-256 hash for a leaf node in
    a Merkle tree using the provided data.
    """
    entry_bytes = base64.b64decode(body)

    # create a new sha256 hash object
    hnode = hashlib.sha256()
    # write the leaf hash prefix
    hnode.update(bytes([RFC6962_LEAF_HASH_PREFIX]))

    # write the actual leaf data
    hnode.update(entry_bytes)

    # return the computed hash
    return hnode.hexdigest()
