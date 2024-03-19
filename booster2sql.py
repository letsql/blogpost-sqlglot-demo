import json
import pprint
from collections import deque

from sqlglot import case, and_, or_, func
from sqlglot.expressions import Paren, Is, null, column as col

from operator import ge, lt
from sqlglot.optimizer.normalize import normalize

from sklearn.ensemble import HistGradientBoostingClassifier


def _is_null(arg):
    return Is(this=arg, expression=null())


def get_min_leaf(tree):
    if "leaf" in tree:
        return tree["leaf"]

    return min(get_min_leaf(child) for child in tree["children"])


def get_max_leaf(tree):
    if "leaf" in tree:
        return tree["leaf"]

    return max(get_min_leaf(child) for child in tree["children"])


def booster2sql(regressor, columns, threshold):
    trees = regressor.get_booster().get_dump(dump_format="json")
    mapping = {column.alias_or_name: column for column in columns}
    case_trees = []

    trees = [json.loads(tree) for tree in trees]
    trees.sort(key=get_min_leaf, reverse=True)
    for tree in trees:
        print(get_min_leaf(tree), get_max_leaf(tree))

    # for tree in trees:
    #     root = json.loads(tree)
    #
    #     stack = deque()
    #
    #     stack.append((root, []))
    #
    #     cases = []
    #     while stack:
    #         cursor, expressions = stack.popleft()
    #
    #         if "leaf" in cursor:  # is a leaf
    #             cases.append([and_(*expressions), cursor["leaf"]])
    #             continue
    #
    #         yes_id = cursor["yes"]
    #         no_id = cursor["no"]
    #         split = cursor["split"]
    #         split_condition = cursor["split_condition"]
    #
    #         column = mapping.get(split, col(split))
    #         yes_expression = (
    #             lt(column, split_condition)
    #             if mapping.get(split)
    #             else f"{split} < {split_condition}"
    #         )
    #         no_expression = or_(
    #             _is_null(column), ge(column, split_condition)
    #         )
    #
    #         for child in cursor["children"]:
    #             if child["nodeid"] == yes_id:
    #                 stack.appendleft((child, expressions + [yes_expression]))
    #             elif child["nodeid"] == no_id:
    #                 stack.appendleft((child, expressions + [no_expression]))
    #
    #     case_tree = case()
    #     for condition, then in cases:
    #         case_tree = case_tree.when(condition, then)
    #
    #     case_trees.append(case_tree)
    #     break
    #
    # head, *tail = (Paren(this=exp) for exp in case_trees)
    # prediction = sum(tail, start=head)
    # return prediction
