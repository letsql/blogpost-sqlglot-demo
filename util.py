from collections import deque


def leafs_vector(tree):
    """Returns a vector of nodes for each tree, only leafs are different of 0"""

    stack = deque([tree])

    while stack:
        node = stack.popleft()
        if "leaf" in node:
            yield node["leaf"]
        else:
            yield 0
            for child in node["children"]:
                stack.append(child)


def get_min_leaf(tree):
    if "leaf" in tree:
        return tree["leaf"]

    return min(get_min_leaf(child) for child in tree["children"])


def get_max_leaf(tree):
    if "leaf" in tree:
        return tree["leaf"]

    return max(get_max_leaf(child) for child in tree["children"])


def get_features(tree):
    if "leaf" in tree:
        yield None
    else:
        yield tree["split"], int(tree["split_condition"])
        yield from (feature for child in tree["children"] for feature in get_features(child))


def is_branch_removable(branch, condition):
    ckey, cval, csign = condition
    for key, val, sign in branch:
        if key == ckey and sign != csign:
            return True
    return False
