import os
import json
import typing

from collections import Counter
from itertools import chain
from contextlib import ExitStack
from typing import Tuple, List, Dict, Set, Generator, Any


def read(paths: List[str]) -> Generator[Dict[str, Any], None, None]:
    """
    Generate instances for one or many files
    :param paths: [path1, path2,..., pathn], [path1] is ok
    :return: yield instance
    """
    with ExitStack() as stack:
        files = chain(stack.enter_context(open(fname, 'r')) for fname in paths)
        for f in files:
            data = json.load(f)
            for ins in data:
                yield ins


def pass1(path: List[str]) -> Tuple[Dict[str, int], Set[str], Dict[str, Dict[str, typing.Counter[str]]]]:
    """
    The first pass of all data.
    Calculating (1) relation counter (2) shared entity type (3) all entity types for each relation
    We will remove the shared entity type later in remove_shared_types
    :param path: [train_path, test_path], the original dataset path
    :return: (1) relation counter (2) shared entity type (3) all entity types for each relation
    """
    relation_counter: Dict[str, int] = {}
    relation_entity_type: Dict[str, Dict[str, typing.Counter[str]]] = {}
    shared_entity_type: Set[str] = set()

    for i, ins in enumerate(read(path)):
        ins_relation = ins['relation']  # type: str
        relation_counter.setdefault(ins_relation, 0)
        relation_counter[ins_relation] += 1

        head_type = set(ins['head']['type'].split(','))
        tail_type = set(ins['tail']['type'].split(','))

        relation_entity_type.setdefault(ins_relation, {'head': Counter(head_type), 'tail': Counter(tail_type)})

        relation_entity_type[ins_relation]['head'].update(head_type)
        relation_entity_type[ins_relation]['tail'].update(tail_type)

        if i == 0:
            shared_entity_type = set(head_type & tail_type)
        else:
            shared_entity_type &= set(head_type & tail_type)

    return relation_counter, shared_entity_type, relation_entity_type


def entity_type_count2set_type(relation_entity_type: Dict[str, Dict[str, typing.Counter[str]]])\
        -> Tuple[Dict[str, Dict[str, int]], Dict[str, Dict[str, int]]]:
    """
    After pass1, turn {'relation': {'head':Counter({'person':2...}), 'tail'...}} to
    {'relation': {'head':len(set(Counter))}}
    :param relation_entity_type: relation_entity_type
    :return: all_set_type, imbalanced_set_type
    {'relation': {'head':len(set(Counter))}}, {'relation': {'head':len(set(Counter))}}
    """
    set_type: Dict[str, Dict[str, int]] = {k: {'head': 0, 'tail': 0} for k in relation_entity_type}
    imbalanced_set_type: Dict[str, Dict[str, int]] = {k: {'head': 0, 'tail': 0} for k in relation_entity_type}
    for r in relation_entity_type:
        head = len(relation_entity_type[r]['head'].keys())
        tail = len(relation_entity_type[r]['tail'].keys())
        set_type[r]['head'] = head
        set_type[r]['tail'] = tail
        if head / tail < 0.2 or head / tail > 5 or head == 1 or tail == 1:
            imbalanced_set_type[r]['head'] = head
            imbalanced_set_type[r]['tail'] = tail
    for r in list(imbalanced_set_type.keys()):
        if imbalanced_set_type[r]['head'] == imbalanced_set_type[r]['tail'] == 0:
            imbalanced_set_type.pop(r)
    return set_type, imbalanced_set_type


def rel2id(path: str) -> Dict[str, int]:
    """
    Return the rel2id dict.
    In NYT, this dict contains all the relations in **train.json**
    :param path:
    :return: Dict[str, int]
    """
    with open(os.path.join(path, 'rel2id.json'), 'r') as f:
        rel = json.load(f)
        return rel


def remove_shared_types(relation_entity_type: Dict[str, Dict[str, typing.Counter[str]]], shared_entity_type: Set[str]) \
        -> Dict[str, Dict[str, typing.Counter[str]]]:
    """
    After pass1, remove the entity types which appeared everywhere.
    {'/common/topic'} in NYT

    :param relation_entity_type: one of the output of pass1,
    :param shared_entity_type: one of the output of pass1
    :return: removed Dict[str, Dict[str, typing.Counter[str]]]
    """
    delete_types = list(shared_entity_type)
    for rel, entities in relation_entity_type.items():
        # shared_types:  {'/common/topic'} is the only shared type in NYT
        for d_type in delete_types:
            del entities['head'][d_type]
            del entities['tail'][d_type]

    return relation_entity_type


def generate_one_type(path: List[str],  relation_entity_type: Dict[str, Dict[str, typing.Counter[str]]]) \
        -> List[Dict[str, Any]]:
    """
    After pass1, we have counted all types. Here we select the most common entity type for every entity mentions.

    :param path: [train.json] or [test.json] or [train.json, test.json].
    :param relation_entity_type: The counted dict
    :return: processed dataset with only one type for every entity
    """
    one: List[Dict[str, Any]] = []
    for i, ins in enumerate(read(path)):
        ins_relation = ins['relation']  # type: str

        head = relation_entity_type[ins_relation]['head']
        tail = relation_entity_type[ins_relation]['tail']

        head_one = Counter({k: head[k] for k in set(ins['head']['type'].split(','))})
        tail_one = Counter({k: tail[k] for k in set(ins['tail']['type'].split(','))})

        # ins['head']['type'] = head_one.most_common(1)[0][0]
        # ins['tail']['type'] = tail_one.most_common(1)[0][0]

        ins['head']['type'] = sorted(sorted(head_one), key=head_one.get, reverse=True)[0]
        ins['tail']['type'] = sorted(sorted(tail_one), key=tail_one.get, reverse=True)[0]
        
        one.append(ins)

    return one


def pass2(paths: List[str]) -> Dict[str, Dict[str, typing.Counter[str]]]:
    """
    After pass1, count entity type for each relation
    Note that every entity have only one type now
    :param paths: [train_one_type_path, train_one_type_path]
    :return: counted entity type for each relation
    """
    relation_entity_type: Dict[str, Dict[str, typing.Counter[str]]] = {}
    for i, ins in enumerate(read(paths)):
        ins_relation = ins['relation']  # type: str

        head_type = set(ins['head']['type'].split(','))
        tail_type = set(ins['tail']['type'].split(','))

        relation_entity_type.setdefault(ins_relation, {'head': Counter(head_type), 'tail': Counter(tail_type)})

        relation_entity_type[ins_relation]['head'].update(head_type)
        relation_entity_type[ins_relation]['tail'].update(tail_type)

    return relation_entity_type


def reverse_entity_relation(out_pass2_stats: Dict[str, Dict[str, typing.Counter[str]]]) -> Dict[str, Dict[str, int]]:
    reverse_rel: Dict[str, Dict[str, int]] = {}

    for r in out_pass2_stats:
        head = out_pass2_stats[r]['head'].keys()
        tail = out_pass2_stats[r]['tail'].keys()
        for h in head:
            reverse_rel.setdefault(h, {'head': 0, 'tail': 0})
            reverse_rel[h]['head'] += 1
        for t in tail:
            reverse_rel.setdefault(t, {'head': 0, 'tail': 0})
            reverse_rel[t]['tail'] += 1
    return reverse_rel


if __name__ == '__main__':
    root_path = '../nyt'
    train_path = os.path.join(root_path, 'train.json')
    test_path = os.path.join(root_path, 'test.json')

    train_one_type_path = os.path.join(root_path, 'train_one.json')
    test_one_type_path = os.path.join(root_path, 'test_one.json')

    rel_counter_path = os.path.join(root_path, 'rel_counter.json')
    out_pass2_stats_path = os.path.join(root_path, 'one_entity_stats.json')

    rel_entity_type_path = os.path.join(root_path, 'rel_entity_type.json')
    imba_set_count_path = os.path.join(root_path, 'imba_set_count_path.json')

    reverse_problem_path = os.path.join(root_path, 'reverse_problem.json')
    # paths

    rel_counter, shared_t, rel_entity_type = pass1([train_path, test_path])
    rel_train = rel2id(root_path)

    print('relation(train | test) - relation(train): ', set(rel_counter.keys()) - set(rel_train.keys()))
    print('shared_types: ', shared_t)
    rel_entity_type = remove_shared_types(rel_entity_type, shared_t)

    entity_set_count, imba_set_count = entity_type_count2set_type(rel_entity_type)
    json.dump(entity_set_count, open(rel_entity_type_path, 'w'))
    json.dump(imba_set_count, open(imba_set_count_path, 'w'))

    train_one_type = generate_one_type([train_path], rel_entity_type)
    test_one_type = generate_one_type([test_path], rel_entity_type)

    json.dump(rel_counter, open(rel_counter_path, 'w'))

    json.dump(train_one_type, open(train_one_type_path, 'w'))
    json.dump(test_one_type, open(test_one_type_path, 'w'))

    pass2_rel_entity_type = pass2([train_one_type_path, test_one_type_path])
    pass2_rel_entity_type_train = pass2([train_one_type_path])
    print('diff types:\n', set(reverse_entity_relation(pass2_rel_entity_type))-set(reverse_entity_relation(pass2_rel_entity_type_train)))
    # pass2_rel_entity_cnt, _ = entity_type_count2set_type(pass2_rel_entity_type)

    json.dump(pass2_rel_entity_type, open(out_pass2_stats_path, 'w'))

    reverse_problem = reverse_entity_relation(pass2_rel_entity_type)
    print('after 1 most normalization, there are %d entity types' % len(reverse_problem))

    json.dump(reverse_problem, open(reverse_problem_path, 'w'))



