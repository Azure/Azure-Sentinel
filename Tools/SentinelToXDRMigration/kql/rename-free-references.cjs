const fs = require('node:fs');
const { loadLanguage, descendants, items } = require('./rename-parser-bindings.cjs');

// Syntax positions where an unresolved name denotes a table-like source or a function call,
// never a column. A name resolved by the binder (let, column, parameter) is never renamed.
const SOURCE_PARENTS = new Set([
  'ParenthesizedExpression', 'LetStatement', 'ExpressionStatement', 'FunctionBody',
  'JoinOperator', 'LookupOperator', 'UnionOperator', 'FindOperator', 'SearchOperator',
]);

function typeName(node) {
  return node ? Bridge.getTypeName(node).split('`')[0].split('.').pop() : '';
}

// With unknown tables the binder may type a pipe source as a column; a column is never a pipe source.
function isUnresolved(node, kusto) {
  const symbol = node.ReferencedSymbol;
  if (!symbol) return true;
  return Bridge.is(symbol, kusto.Symbols.ColumnSymbol) &&
    typeName(node.Parent) === 'PipeExpression' && node.Parent.Expression === node;
}

function isSourcePosition(node) {
  const parent = node.Parent;
  const parentType = typeName(parent);
  if (parentType === 'PipeExpression') return parent.Expression === node;
  if (parentType === 'FunctionCallExpression') return parent.Name === node;
  if (SOURCE_PARENTS.has(parentType)) return true;
  if (parentType === 'SeparatedElement') {
    for (let ancestor = parent.Parent, depth = 0; ancestor && depth < 3; ancestor = ancestor.Parent, depth++) {
      const type = typeName(ancestor);
      if (type === 'UnionOperator') return true;
      if (type === 'FindOperator' || type === 'SearchOperator') return true;
    }
  }
  return false;
}

// Rename unresolved references to the given names; declared names (let, columns, parameters) win.
function renameFreeReferences(query, mapping) {
  if (typeof query !== 'string' || !mapping || typeof mapping !== 'object') {
    throw new Error('Expected query text and a name mapping object.');
  }
  const names = Object.keys(mapping);
  if (names.length === 0) return { query, renamed: [] };
  const kusto = loadLanguage();
  const parsed = kusto.KustoCode.Parse(query);
  const syntaxErrors = items(parsed.GetSyntaxDiagnostics());
  if (syntaxErrors.length) {
    throw new Error(`Cannot inline parsers into invalid KQL: ${syntaxErrors[0].Message}`);
  }
  const code = kusto.KustoCode.ParseAndAnalyze(query);
  const edits = descendants(code.Syntax)
    .filter(node => Bridge.is(node, kusto.Syntax.NameReference) &&
      Object.prototype.hasOwnProperty.call(mapping, node.SimpleName) &&
      isUnresolved(node, kusto) && isSourcePosition(node))
    .map(node => ({ start: node.TextStart, length: node.Width, from: node.SimpleName, text: mapping[node.SimpleName] }))
    .sort((left, right) => left.start - right.start);
  let rewritten = '';
  let offset = 0;
  for (const edit of edits) {
    rewritten += query.slice(offset, edit.start) + edit.text;
    offset = edit.start + edit.length;
  }
  rewritten += query.slice(offset);
  if (edits.length && items(kusto.KustoCode.Parse(rewritten).GetSyntaxDiagnostics()).length) {
    throw new Error('Parser inlining rewrite produced invalid KQL.');
  }
  return { query: rewritten, renamed: [...new Set(edits.map(edit => edit.from))] };
}

module.exports = { renameFreeReferences };

if (require.main === module) {
  try {
    const input = JSON.parse(fs.readFileSync(0, 'utf8').replace(/^\uFEFF/, ''));
    process.stdout.write(JSON.stringify(renameFreeReferences(input.query, input.mapping)));
  } catch (error) {
    process.stderr.write(`Parser inlining failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
