const assert = require('node:assert/strict');
const test = require('node:test');
const crypto = require('node:crypto');
const fixtures = require('../tests/fixtures/parser_collisions.json');
const { renameParserBindings: rename } = require('./rename-parser-bindings.cjs');

test('renames a tabular binding, not a same-named column or literal', () => {
  const query = "let Parser = datatable(Parser:string)['Parser']; Parser | project Parser";
  assert.equal(rename(query, ['Parser']).query,
    "let XdrInlineParser = datatable(Parser:string)['Parser']; XdrInlineParser | project Parser");
});

test('preserves comments, escaped strings, verbatim strings, and Unicode offsets', () => {
  const query = "// \u{1f512} Parser\nlet Parser = datatable(Value:string)['Parser', @'a\\Parser', 'can\\'t Parser'];\nParser // Parser";
  assert.equal(rename(query, ['Parser']).query, query
    .replace('let Parser', 'let XdrInlineParser')
    .replace('\nParser //', '\nXdrInlineParser //'));
});

test('a parameter shadows the outer binding and keeps its own references', () => {
  const query = "let Parser = datatable(x:string)['x']; let f = (Parser:string) { print Value=Parser }; Parser";
  assert.equal(rename(query, ['Parser']).query,
    "let XdrInlineParser = datatable(x:string)['x']; let f = (Parser:string) { print Value=Parser }; XdrInlineParser");
});

test('nested let bindings get distinct names with references in the right scopes', () => {
  const query = "let Parser = datatable(x:string)['outer']; let f = () { let Parser = datatable(x:string)['inner']; Parser }; union Parser, f()";
  assert.equal(rename(query, ['Parser']).query,
    "let XdrInlineParser = datatable(x:string)['outer']; let f = () { let XdrInlineParser_2 = datatable(x:string)['inner']; XdrInlineParser_2 }; union XdrInlineParser, f()");
});

test('renames parser functions and their calls', () => {
  const query = "let Parser = () { datatable(x:long)[1] }; Parser() | where x > 0";
  assert.equal(rename(query, ['Parser']).query,
    "let XdrInlineParser = () { datatable(x:long)[1] }; XdrInlineParser() | where x > 0");
});

test('supports arbitrary parser names and dependencies between bindings', () => {
  const query = 'let VendorA = datatable(x:long)[1]; let VendorB = VendorA; union VendorA, VendorB';
  assert.equal(rename(query, ['VendorA', 'VendorB']).query,
    'let XdrInlineVendorA = datatable(x:long)[1]; let XdrInlineVendorB = XdrInlineVendorA; union XdrInlineVendorA, XdrInlineVendorB');
});

test('refuses to discard comments embedded inside a quoted identifier', () => {
  const query = "let ['Parser' // preserve\n] = datatable(x:long)[1]; ['Parser']";
  assert.throws(() => rename(query, ['Parser']), /embedded comment/);
});

test('handles bracketed identifiers without editing bracketed column names', () => {
  const query = "let ['Parser'] = datatable(['Parser']:long)[1]; ['Parser'] | project ['Parser']";
  assert.equal(rename(query, ['Parser']).query,
    "let XdrInlineParser = datatable(['Parser']:long)[1]; XdrInlineParser | project ['Parser']");
});

test('avoids existing identifiers and reserved aliases; normalization is idempotent', () => {
  const query = "let XdrInlineParser=1; let Parser=datatable(x:long)[1]; Parser";
  const result = rename(query, ['Parser', 'XdrInlineParser_2']);
  assert.equal(result.renames[0].to, 'XdrInlineParser_3');
  assert.deepEqual(rename(result.query, ['Parser', 'XdrInlineParser_2']),
    { query: result.query, renames: [] });
});

test('renames only declared local symbols, not a saved parser call in the initializer', () => {
  const query = "let Parser = Parser(); Parser";
  assert.equal(rename(query, ['Parser']).query,
    "let XdrInlineParser = Parser(); XdrInlineParser");
});

test('does not rewrite unrelated bindings or an external parser reference', () => {
  for (const query of ['Parser() | take 1', 'let Other=1; print Value=Other', "// let Parser=1;\nprint Value='Parser'"]) {
    assert.deepEqual(rename(query, ['Parser']), { query, renames: [] });
  }
});

test('supports scalar local references when the output alias is explicit', () => {
  assert.equal(rename('let Parser=1; print Value=Parser', ['Parser']).query,
    'let XdrInlineParser=1; print Value=XdrInlineParser');
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
    assert.equal(result.query, fixture.query.replaceAll(fixture.parser, `XdrInline${fixture.parser}`));
    assert.equal(result.renames.length, 1);
    assert.deepEqual(rename(result.query, [fixture.parser]), { query: result.query, renames: [] });
  });
}
