"""Validate catalog, reviewed import decisions, and stable legacy identities (stdlib only)."""
import collections
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT/path).read_text())

def blocked(q):
    return (q.get('assessmentStatus') == 'unresolved' or bool(q.get('contextWarning')) or
            any(re.search(r'aus Prüfung ausschließen|keine eindeutige Bewertung|manuell prüfen|abgeschnitten|zusammengezogen|nicht automatisch benoten|unvollständig/fragmentarisch', f) for f in q['flags']))

def eligible(q):
    return not blocked(q) and len(q['options']) == 4 and len(q['answers']) == q['correctCount'] and 1 <= q['correctCount'] <= 3

def object_hash(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()

def validate_schema(value, schema, location='$'):
    """Small dependency-free interpreter for the keywords used in our schema.

    Fail closed for unknown keywords so schema changes cannot silently skip tests.
    Cross-record and legacy invariants are checked separately below.
    """
    supported = {'$schema', 'title', 'type', 'minItems', 'maxItems', 'items', 'required',
                 'properties', 'additionalProperties', 'minimum', 'maximum', 'minLength',
                 'uniqueItems', 'enum', 'const'}
    assert set(schema) <= supported, f'Unsupported schema keywords at {location}'
    types = {'array': list, 'object': dict, 'integer': int, 'string': str}
    if 'type' in schema:
        assert type(value) is types[schema['type']], f'{location}: expected {schema["type"]}'
    if 'enum' in schema:
        assert value in schema['enum'], f'{location}: enum'
    if 'const' in schema:
        assert value == schema['const'], f'{location}: const'
    for key, predicate in [('minimum', lambda x: value >= x), ('maximum', lambda x: value <= x),
                           ('minLength', lambda x: len(value) >= x), ('minItems', lambda x: len(value) >= x),
                           ('maxItems', lambda x: len(value) <= x)]:
        if key in schema:
            assert predicate(schema[key]), f'{location}: {key}'
    if schema.get('uniqueItems'):
        assert len({json.dumps(x, sort_keys=True) for x in value}) == len(value), f'{location}: duplicate items'
    if isinstance(value, list) and 'items' in schema:
        for i, item in enumerate(value):
            validate_schema(item, schema['items'], f'{location}[{i}]')
    if isinstance(value, dict):
        assert set(schema.get('required', [])) <= set(value), f'{location}: missing required field'
        for key, child in schema.get('properties', {}).items():
            if key in value:
                validate_schema(value[key], child, f'{location}.{key}')


def validate():
    catalog = load('questions.json')
    validate_schema(catalog, load('schemas/questions.schema.json'))
    audit = load('data/question-catalog-audit.json')
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    check(isinstance(catalog, list), 'questions.json must be an array')
    ids = [q['id'] for q in catalog]
    check(len(set(ids)) == len(ids), 'Duplicate question IDs')
    known_chapters = {q['chapter'] for q in audit['baseline']['questions']}
    by_id = {q['id']: q for q in catalog}
    for q in catalog:
        name = '#'+str(q['id'])
        for field, typ in {'id': int, 'chapter': str, 'page': int, 'text': str, 'correctCount': int,
                           'options': list, 'answers': list, 'sourceAnswer': str, 'explanation': str, 'flags': list}.items():
            check(field in q and type(q[field]) is typ, name+' invalid '+field)
        check(q['id'] > 0 and q['page'] >= 0, name+' invalid id/page')
        check(q['text'].strip() and q['chapter'] in known_chapters, name+' missing text/chapter')
        check(3 <= len(q['options']) <= 5, name+' invalid option count')
        check(all(isinstance(o, str) and o.strip() for o in q['options']), name+' blank option')
        check(all(isinstance(f, str) for f in q['flags']), name+' invalid flag')
        check(all(type(a) is int and 0 <= a < len(q['options']) for a in q['answers']), name+' invalid answer index')
        check(len(set(q['answers'])) == len(q['answers']), name+' repeated answer index')
        if not blocked(q):
            check(0 < len(q['answers']) == q['correctCount'] < len(q['options']), name+' invalid solution/count')
            check(not any(re.search(r'\[\?+\]|\?\?\?', o) for o in q['options']), name+' unresolved placeholder eligible')
            normalized = [re.sub(r'\W+', '', o.lower()) for o in q['options']]
            check(len(set(normalized)) == len(normalized), name+' duplicate options without quarantine')
    old_ids = {q['id'] for q in audit['baseline']['questions']}
    changed = {c['existingId']: c for c in audit['changes'] if c['existingId'] is not None}
    check(old_ids <= set(ids), 'Legacy question removed')
    for old in audit['baseline']['questions']:
        current = by_id.get(old['id'])
        if current is None:
            continue
        check(current['options'] == old['options'], f"#{old['id']} legacy options reordered/replaced")
        check(current['chapter'] == old['chapter'], f"#{old['id']} legacy statistics reassigned")
        if old['id'] not in changed:
            check(object_hash(current) == old['objectSha256'], f"#{old['id']} undocumented mutation")
        else:
            check(changed[old['id']]['after'] == current, f"#{old['id']} audit after-image stale")
            check(object_hash(changed[old['id']]['before']) == old['objectSha256'], 'Audit before-image wrong')
    rows = audit['questions']
    raw_import = load(audit['sources']['import']['path'])['questions']
    check([r['importIndex'] for r in rows] == list(range(1, len(raw_import)+1)), 'Import decisions not exhaustive/ordered')
    import_hash = hashlib.sha256((ROOT/audit['sources']['import']['path']).read_bytes()).hexdigest()
    check(import_hash == audit['originalImportSha256'], 'Original import changed')
    for r, raw in zip(rows, raw_import):
        check(r['raw'] == raw, 'Raw import audit differs')
        check(r['category'] in 'ABCDEF' and len(r['category']) == 1, 'Invalid classification')
        check(bool(r['reason']) and all(s in audit['sources'] for s in r['sources']), 'Missing review evidence')
        if r['category'] == 'E':
            q = by_id.get(r['newId'])
            check(q is not None and q['id'] > max(old_ids), 'New ID collision')
            if q:
                check(q['options'] == r['normalized']['options'], 'New import options altered')
                check(q['text'] == r['normalized']['text'], 'New import wording altered')
                check(q['answers'] == r['normalized']['answers'], 'New unrecorded key change')
                check(q.get('assessmentStatus') == 'verified' and q.get('auditSources'), 'New question not verified')
                check(q.get('source', {}).get('index') == r['importIndex'], 'New question source mismatch')
                check(q.get('source', {}).get('answerIds') == r['normalized']['originalAnswerIds'], 'New answer IDs differ from source')
        else:
            check(r['existingId'] in old_ids and r['newId'] is None, 'Missing legacy relation')
    # Added duplicate detection is order-insensitive; legacy variants remain ID-stable.
    signatures = collections.defaultdict(list)
    for q in catalog:
        norm = lambda s: re.sub(r'\W+', '', s.lower())
        signature = (norm(q['text']), tuple(sorted(norm(o) for o in q['options'])))
        signatures[signature].append(q['id'])
    duplicates = [group for group in signatures.values() if len(group) > 1]
    check(not any(any(i not in old_ids for i in group) for group in duplicates), 'New duplicate introduced')
    chapter_counts = dict(collections.Counter(q['chapter'] for q in catalog if eligible(q)))
    check(len(chapter_counts) == 12 and min(chapter_counts.values()) >= 4, 'Exam chapter coverage insufficient')
    counts = dict(sorted(collections.Counter(r['category'] for r in rows).items()))
    check(counts == audit['summary']['categories'], 'Stale classification counts')
    check(len(catalog) == audit['summary']['final'], 'Stale final count')
    if errors:
        raise AssertionError('\n'.join(errors))
    result = {'status': 'passed', 'catalogCount': len(catalog), 'legacyIdsPreserved': len(old_ids),
              'newIds': sorted(set(ids)-old_ids), 'eligibleCount': sum(eligible(q) for q in catalog),
              'readingOnlyCount': sum(not eligible(q) for q in catalog), 'examChapterCounts': chapter_counts,
              'classifications': counts, 'originalImportSha256': import_hash,
              'exactDuplicateGroups': duplicates, 'realBrowserDataTested': False}
    (ROOT/'reports/question-catalog-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result

if __name__ == '__main__':
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
