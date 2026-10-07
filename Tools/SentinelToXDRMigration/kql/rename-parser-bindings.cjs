const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

let language;
function loadLanguage() {
  if (!language) {
    const root = path.dirname(require.resolve('@kusto/language-service-next/package.json'));
    for (const file of ['bridge.js', 'Kusto.Language.Bridge.js']) {
      vm.runInThisContext(fs.readFileSync(path.join(root, file), 'utf8'), { filename: file });
    }
    language = Kusto.Language;
  }
  return language;
}

function descendants(node, nodes = []) {
  if (node) {
    nodes.push(node);
    for (let index = 0; index < node.ChildCount; index++) {
      descendants(node.GetChild(index), nodes);
    }
  }
  return nodes;
}

function items(collection) {
  const values = [];
  const iterator = Bridge.getEnumerator(collection);
  while (iterator.moveNext()) values.push(iterator.Current);
  return values;
}

function tableShapes(nodes, kusto) {
  return nodes.filter(node => node.ResultType && Bridge.is(node.ResultType, kusto.Symbols.TableSymbol))
    .map(node => items(node.ResultType.Columns).map(column => [column.Name, column.Type.Name]));
}

function comments(nodes) {
  return nodes.filter(node => typeof node.Trivia === 'string')
    .flatMap(node => node.Trivia.match(/\/\/[^\r\n]*|\/\*[\s\S]*?\*\//g) || []);
}

function renameParserBindings(query, reservedNames) {
  if (typeof query !== 'string' || !Array.isArray(reservedNames) ||
      reservedNames.some(name => typeof name !== 'string' || !name)) {
    throw new Error('Expected query text and an array of nonempty parser names.');
  }
  if (reservedNames.length === 0) return { query, renames: [] };

  const kusto = loadLanguage();
  const reserved = new Set(reservedNames);
  const parsed = kusto.KustoCode.Parse(query);
  const candidates = descendants(parsed.Syntax).filter(node =>
    Bridge.is(node, kusto.Syntax.LetStatement) && reserved.has(node.Name.SimpleName));
  if (candidates.length === 0) return { query, renames: [] };
  const syntaxErrors = items(parsed.GetSyntaxDiagnostics());
  if (syntaxErrors.length) {
    throw new Error(`Cannot rename parser bindings in invalid KQL: ${syntaxErrors[0].Message}`);
  }

  const code = kusto.KustoCode.ParseAndAnalyze(query);
  const nodes = descendants(code.Syntax);
  const names = nodes.filter(node =>
    Bridge.is(node, kusto.Syntax.NameDeclaration) || Bridge.is(node, kusto.Syntax.NameReference));
  const occupied = new Set([...reserved, ...names.map(node => node.SimpleName)]);
  const replacements = new Map();
  const renames = [];
  for (const node of nodes) {
    if (!Bridge.is(node, kusto.Syntax.LetStatement) || !reserved.has(node.Name.SimpleName)) continue;
    const symbol = node.Name.ReferencedSymbol;
    if (!symbol) throw new Error(`Cannot resolve local parser binding '${node.Name.SimpleName}'.`);
    const base = `__xdr_inline_${node.Name.SimpleName.replace(/[^A-Za-z0-9_]/g, '_')}`;
    let target = base;
    for (let suffix = 2; occupied.has(target); suffix++) target = `${base}_${suffix}`;
    occupied.add(target);
    replacements.set(symbol, target);
    renames.push({ from: node.Name.SimpleName, to: target });
  }

  for (const node of nodes) {
    if (Bridge.is(node, kusto.Syntax.WildcardedName)) {
      const pattern = new RegExp('^' + node.SimpleName.split('*')
        .map(part => part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('.*') + '$');
      if (renames.some(rename => pattern.test(rename.from) || pattern.test(rename.to))) {
        throw new Error('Cannot safely rename a parser binding selected by a wildcard; use explicit inputs.');
      }
    }
    const symbol = node.ReferencedSymbol;
    if (symbol && Bridge.is(symbol, kusto.Symbols.GroupSymbol) &&
        items(symbol.Members).some(member => replacements.has(member))) {
      throw new Error('Cannot safely rename a parser binding selected by a wildcard; use explicit inputs.');
    }
    if (Bridge.is(node, kusto.Syntax.NamedParameter) &&
        ['withsource', 'with_source'].includes(node.Name.SimpleName)) {
      throw new Error('Cannot safely rename parser bindings with union source labels; use explicit source labels.');
    }
  }

  const edits = names.filter(node => replacements.has(node.ReferencedSymbol))
    .map(node => ({
      start: node.TextStart,
      length: node.Width,
      text: replacements.get(node.ReferencedSymbol),
      declaration: Bridge.is(node, kusto.Syntax.NameDeclaration)
    }))
    .sort((left, right) => left.start - right.start);
  let rewritten = '';
  let offset = 0;
  for (const edit of edits) {
    rewritten += query.slice(offset, edit.start) + edit.text;
    offset = edit.start + edit.length;
  }
  rewritten += query.slice(offset);

  const checked = kusto.KustoCode.ParseAndAnalyze(rewritten);
  if (items(checked.GetSyntaxDiagnostics()).length) {
    throw new Error('Parser binding rewrite produced invalid KQL.');
  }
  const checkedNodes = descendants(checked.Syntax);
  if (JSON.stringify(comments(nodes)) !== JSON.stringify(comments(checkedNodes))) {
    throw new Error('Parser binding rename would remove an embedded comment; move it outside the identifier.');
  }
  if (JSON.stringify(tableShapes(nodes, kusto)) !== JSON.stringify(tableShapes(checkedNodes, kusto))) {
    throw new Error('Parser binding rename changes inferred output columns; add explicit column aliases.');
  }
  const checkedNames = new Map(checkedNodes.filter(node =>
    Bridge.is(node, kusto.Syntax.NameDeclaration) || Bridge.is(node, kusto.Syntax.NameReference))
    .map(node => [node.TextStart, node]));
  const declarations = new Map();
  let delta = 0;
  for (const edit of edits) {
    const node = checkedNames.get(edit.start + delta);
    if (!node || node.SimpleName !== edit.text || !node.ReferencedSymbol) {
      throw new Error(`Could not verify renamed binding '${edit.text}'.`);
    }
    if (edit.declaration) declarations.set(edit.text, node.ReferencedSymbol);
    else if (node.ReferencedSymbol !== declarations.get(edit.text)) {
      throw new Error(`Renaming '${edit.text}' changed its binding scope.`);
    }
    delta += edit.text.length - edit.length;
  }
  return { query: rewritten, renames };
}

module.exports = { renameParserBindings };

if (require.main === module) {
  try {
    const input = JSON.parse(fs.readFileSync(0, 'utf8').replace(/^\uFEFF/, ''));
    process.stdout.write(JSON.stringify(renameParserBindings(input.query, input.reservedNames)));
  } catch (error) {
    process.stderr.write(`Parser binding normalization failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
