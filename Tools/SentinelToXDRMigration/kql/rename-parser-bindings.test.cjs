const assert = require('node:assert/strict');
const test = require('node:test');
const crypto = require('node:crypto');
const fixtures = require('../tests/fixtures/parser_collisions.json');
const { renameParserBindings: rename } = require('./rename-parser-bindings.cjs');

test('renames a tabular binding, not a same-named column or literal', () => {
  const query = "let Parser = datatable(Parser:string)['Parser']; Parser | project Parser";
  assert.equal(rename(query, ['Parser']).query,
    "let __xdr_inline_Parser = datatable(Parser:string)['Parser']; __xdr_inline_Parser | project Parser");
});

test('preserves comments, escaped strings, verbatim strings, and Unicode offsets', () => {
  const query = "// \u{1f512} Parser\nlet Parser = datatable(Value:string)['Parser', @'a\\Parser', 'can\\'t Parser'];\nParser // Parser";
  assert.equal(rename(query, ['Parser']).query, query
    .replace('let Parser', 'let __xdr_inline_Parser')
    .replace('\nParser //', '\n__xdr_inline_Parser //'));
});

test('a parameter shadows the outer binding and keeps its own references', () => {
  const query = "let Parser = datatable(x:string)['x']; let f = (Parser:string) { print Value=Parser }; Parser";
  assert.equal(rename(query, ['Parser']).query,
    "let __xdr_inline_Parser = datatable(x:string)['x']; let f = (Parser:string) { print Value=Parser }; __xdr_inline_Parser");
});

test('nested let bindings get distinct names with references in the right scopes', () => {
  const query = "let Parser = datatable(x:string)['outer']; let f = () { let Parser = datatable(x:string)['inner']; Parser }; union Parser, f()";
  assert.equal(rename(query, ['Parser']).query,
    "let __xdr_inline_Parser = datatable(x:string)['outer']; let f = () { let __xdr_inline_Parser_2 = datatable(x:string)['inner']; __xdr_inline_Parser_2 }; union __xdr_inline_Parser, f()");
});

test('renames parser functions and their calls', () => {
  const query = "let Parser = () { datatable(x:long)[1] }; Parser() | where x > 0";
  assert.equal(rename(query, ['Parser']).query,
    "let __xdr_inline_Parser = () { datatable(x:long)[1] }; __xdr_inline_Parser() | where x > 0");
});

test('supports arbitrary parser names and dependencies between bindings', () => {
  const query = 'let VendorA = datatable(x:long)[1]; let VendorB = VendorA; union VendorA, VendorB';
  assert.equal(rename(query, ['VendorA', 'VendorB']).query,
    'let __xdr_inline_VendorA = datatable(x:long)[1]; let __xdr_inline_VendorB = __xdr_inline_VendorA; union __xdr_inline_VendorA, __xdr_inline_VendorB');
});

test('refuses to discard comments embedded inside a quoted identifier', () => {
  const query = "let ['Parser' // preserve\n] = datatable(x:long)[1]; ['Parser']";
  assert.throws(() => rename(query, ['Parser']), /embedded comment/);
});

test('handles bracketed identifiers without editing bracketed column names', () => {
  const query = "let ['Parser'] = datatable(['Parser']:long)[1]; ['Parser'] | project ['Parser']";
  assert.equal(rename(query, ['Parser']).query,
    "let __xdr_inline_Parser = datatable(['Parser']:long)[1]; __xdr_inline_Parser | project ['Parser']");
});

test('avoids existing identifiers and reserved aliases; normalization is idempotent', () => {
  const query = "let __xdr_inline_Parser=1; let Parser=datatable(x:long)[1]; Parser";
  const result = rename(query, ['Parser', '__xdr_inline_Parser_2']);
  assert.equal(result.renames[0].to, '__xdr_inline_Parser_3');
  assert.deepEqual(rename(result.query, ['Parser', '__xdr_inline_Parser_2']),
    { query: result.query, renames: [] });
});

test('renames only declared local symbols, not a saved parser call in the initializer', () => {
  const query = "let Parser = Parser(); Parser";
  assert.equal(rename(query, ['Parser']).query,
    "let __xdr_inline_Parser = Parser(); __xdr_inline_Parser");
});

test('does not rewrite unrelated bindings or an external parser reference', () => {
  for (const query of ['Parser() | take 1', 'let Other=1; print Value=Other', "// let Parser=1;\nprint Value='Parser'"]) {
    assert.deepEqual(rename(query, ['Parser']), { query, renames: [] });
  }
});

test('supports scalar local references when the output alias is explicit', () => {
  assert.equal(rename('let Parser=1; print Value=Parser', ['Parser']).query,
    'let __xdr_inline_Parser=1; print Value=__xdr_inline_Parser');
});

test('refuses an implicit output-column change', () => {
  assert.throws(() => rename('let Parser=1; datatable(x:long)[1] | project Parser', ['Parser']), /output columns/);
});

test('refuses invalid syntax in a query needing a rename', () => {
  assert.throws(() => rename('let Parser = ; Parser', ['Parser']), /invalid KQL/);
});

test('refuses wildcard selection that would lose the renamed binding', () => {
  assert.throws(() => rename('let Parser=datatable(x:long)[1]; union Parser*', ['Parser']), /wildcard/);
});

test('refuses withsource because renaming would change source-label values', () => {
  assert.throws(() => rename('let Parser=datatable(x:long)[1]; union withsource=Source Parser', ['Parser']), /source labels/);
});

test('refuses indirect table lookup when its inferred binding would change', () => {
  assert.throws(() => rename("let Parser=UnknownTable; table('Parser')", ['Parser']), /output columns/);
});

for (const fixture of fixtures) {
  test(`original PR query: ${fixture.name}`, () => {
    assert.equal(crypto.createHash('sha256').update(fixture.query).digest('hex'), fixture.sourceSha256);
    assert.equal(fixture.query.split(fixture.parser).length - 1, 2);
    const result = rename(fixture.query, [fixture.parser]);
    assert.equal(result.query, fixture.query.replaceAll(fixture.parser, `__xdr_inline_${fixture.parser}`));
    assert.equal(result.renames.length, 1);
    assert.deepEqual(rename(result.query, [fixture.parser]), { query: result.query, renames: [] });
  });
}
