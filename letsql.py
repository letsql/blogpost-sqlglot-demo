from collections import deque

import xgboost as xgb
import json
from itertools import accumulate

from util import get_min_leaf
import sqlglot as sg

from sqlglot.dialects import Postgres
from sqlglot.expressions import and_, or_, Paren, Is, null, case, column as col
from operator import ge, lt


def _is_null(arg):
    return Is(this=arg, expression=null())


def _get_and_prune_trees(model: xgb.XGBRegressor, threshold=None) -> list:
    # get base_score
    config = json.loads(model.get_booster().save_config())
    base_score = float(config["learner"]["learner_model_param"]["base_score"])

    # get trees
    trees = model.get_booster().get_dump(dump_format="json")
    trees = [json.loads(tree) for tree in trees]

    # sort
    sorted_trees = sorted(trees, key=get_min_leaf, reverse=True)

    if threshold is None:
        return sorted_trees

    # do a cumulative sum to find the splitting point in O(1)
    cumulative_sum = list(accumulate(map(get_min_leaf, sorted_trees), initial=base_score))

    # find the splitting point if any
    i = 0
    for i, s in enumerate(cumulative_sum):
        if s >= threshold and cumulative_sum[-1] - cumulative_sum[i] > 0:
            break

    return sorted_trees[:i]


def _extract_predict_function(node):
    g = (expression for expression in node.find_all(sg.exp.Anonymous) if expression.this == "predict_xgb")
    return next(g, None)  # only the first one is required


def _get_model(predict_expression: sg.expressions.Anonymous):
    # load the model assuming is the first argument of the predict_expression
    model = xgb.XGBRegressor()
    model.load_model(predict_expression.expressions[0].this)
    return model


def _extract_prediction_threshold(predict_expression: sg.expressions.Anonymous):
    # extract the threshold assuming is greater than (GT) expression
    if isinstance(predict_expression.parent, sg.expressions.GT):
        return float(str(predict_expression.parent.expression))


def _transform_to_case_expressions(trees, table="patients"):

    case_trees = []
    for tree in trees:
        stack = deque()
        stack.append((tree, []))

        cases = []
        while stack:
            cursor, expressions = stack.popleft()

            if "leaf" in cursor:  # is a leaf
                cases.append([and_(*expressions), cursor["leaf"]])
                continue

            yes_id = cursor["yes"]
            no_id = cursor["no"]
            split = cursor["split"]
            split_condition = cursor["split_condition"]

            column = col(split, table=table)
            yes_expression = (
                lt(column, split_condition)
                if column
                else f"{split} < {split_condition}"
            )
            no_expression = or_(
                _is_null(column), ge(column, split_condition)
            )

            for child in cursor["children"]:
                if child["nodeid"] == yes_id:
                    stack.appendleft((child, expressions + [yes_expression]))
                elif child["nodeid"] == no_id:
                    stack.appendleft((child, expressions + [no_expression]))

        case_tree = case()
        for condition, then in cases:
            case_tree = case_tree.when(condition, then)

        case_trees.append(case_tree)
    return case_trees


def _transform_and_prune_branch(e: sg.expressions.Case, cons):
    identifier, value, klass = cons

    to_find = None
    if klass == sg.expressions.LT:
        to_find = sg.exp.GTE

    ifs = []
    for i in e.args["ifs"]:
        no_contradiction = True
        for g in i.find_all(to_find):
            if str(g.this.this) == identifier and float(str(g.expression)) >= value:
                no_contradiction = False
                break
        if no_contradiction:
            ifs.append(i)

    e.args["ifs"] = ifs
    return e


def _prune_branches(case_expressions: list, predict_expression: sg.expressions.Anonymous) -> list:

    # since the expression is known we use shortcut, for general applicability a more complex algorithm is needed
    constraint = predict_expression.parent.parent.expression
    identifier = str(constraint.this.this)
    value = float(str(constraint.expression))
    klass = type(constraint)
    return [_transform_and_prune_branch(e, cons=(identifier, value, klass)) for e in case_expressions]


def _inline_trees(node, case_expressions):

    def _inline_sum(a: sg.expressions.Anonymous, model=None):
        if isinstance(a, sg.expressions.Anonymous) and a.this == "predict_xgb":
            return model
        return a

    head, *tail = (Paren(this=exp) for exp in case_expressions)
    inlined_model = sum(tail, start=head)

    return node.transform(_inline_sum, model=inlined_model)


def transpile_predict(sql):

    node = sg.parse_one(sql, dialect=Postgres)
    predict_expression = _extract_predict_function(node)
    if predict_expression is not None:
        model = _get_model(predict_expression)
        threshold = _extract_prediction_threshold(predict_expression)
        trees = _get_and_prune_trees(model, threshold=threshold)
        if len(trees) < 5:  # the model is simple enough
            case_expressions = _transform_to_case_expressions(trees)
            case_expressions = _prune_branches(case_expressions, predict_expression)
            return _inline_trees(node, case_expressions).sql(pretty=True)
        else:
            pass  # TODO implement model splitting
    else:
        return sql



