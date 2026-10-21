const assert = require('node:assert/strict');
const test = require('node:test');
const { renameFreeReferences: rename } = require('./rename-free-references.cjs');

const map = { Parser: 'XdrInlineParser' };

test('renames bare, call, join, union and parenthesized references', () => {
  const result = rename(
    'Parser | join (Parser) on Id | union Parser, Other | extend x = 1\n;\nlet y = Parser(1); y', map);
  assert.deepEqual(result.renamed, ['Parser']);
  assert.equal(result.query.match(/XdrInlineParser/g).length, 4);
  assert.ok(!/\bParser\b/.test(result.query));
  assert.equal(rename('T | where a in (Parser | project a)', map).query,
    'T | where a in (XdrInlineParser | project a)');
});

test('does not touch columns, strings, comments, let bindings or parameters', () => {
  const query = [
    "let T = datatable(Parser:long)[1];",
    "let Query = T | where Parser == 1 | extend s = 'Parser' | project Parser; // Parser",
    'let Local = (Parser:long) { Parser + 1 };',
    'print Local(1)',
  ].join('\n');
  assert.equal(rename(query, map).query, query);
  const shadow = 'let Parser = datatable(a:int)[1]; Parser | take 1';
  assert.equal(rename(shadow, map).query, shadow);
});

test('rejects invalid KQL', () => {
  assert.throws(() => rename('Parser | where (', map), /invalid KQL/);
});
