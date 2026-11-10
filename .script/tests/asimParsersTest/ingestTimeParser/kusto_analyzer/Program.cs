using System.Text.Json;
using System.Text.Json.Serialization;
using Kusto.Language;
using Kusto.Language.Syntax;

namespace AsimKustoAnalyzer;

internal sealed record AnalyzerRequest(
    [property: JsonPropertyName("query")] string Query);

internal sealed record LocationFact(
    [property: JsonPropertyName("start")] int Start,
    [property: JsonPropertyName("length")] int Length,
    [property: JsonPropertyName("line")] int Line,
    [property: JsonPropertyName("column")] int Column,
    [property: JsonPropertyName("text")] string Text,
    [property: JsonPropertyName("normalizedText")] string NormalizedText);

internal sealed record DiagnosticFact(
    [property: JsonPropertyName("code")] string Code,
    [property: JsonPropertyName("severity")] string Severity,
    [property: JsonPropertyName("message")] string Message,
    [property: JsonPropertyName("start")] int Start,
    [property: JsonPropertyName("length")] int Length,
    [property: JsonPropertyName("line")] int Line,
    [property: JsonPropertyName("column")] int Column);

internal sealed record SyntaxFact(
    [property: JsonPropertyName("type")] string Type,
    [property: JsonPropertyName("kind")] string Kind,
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("ownerOperator")]
    string? OwnerOperator,
    [property: JsonPropertyName("location")] LocationFact Location);

internal sealed record StatementFact(
    [property: JsonPropertyName("type")] string Type,
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("hasPipe")] bool HasPipe,
    [property: JsonPropertyName("expressionRootType")]
    string? ExpressionRootType,
    [property: JsonPropertyName("expressionRootText")]
    string? ExpressionRootText,
    [property: JsonPropertyName("location")] LocationFact Location);

internal sealed record AssignmentFact(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("expressionType")] string ExpressionType,
    [property: JsonPropertyName("expressionKind")] string ExpressionKind,
    [property: JsonPropertyName("isStringLiteral")] bool IsStringLiteral,
    [property: JsonPropertyName("stringValue")] string? StringValue,
    [property: JsonPropertyName("ownerOperator")]
    string? OwnerOperator,
    [property: JsonPropertyName("location")] LocationFact Location);

internal sealed record SourceReferenceFact(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("context")] string Context,
    [property: JsonPropertyName("location")] LocationFact Location);

internal sealed record PipelineFact(
    [property: JsonPropertyName("rootType")] string? RootType,
    [property: JsonPropertyName("rootKind")] string? RootKind,
    [property: JsonPropertyName("rootText")] string? RootText,
    [property: JsonPropertyName("operators")]
    IReadOnlyList<SyntaxFact> Operators);

internal sealed record AnalyzerResponse(
    [property: JsonPropertyName("version")] int Version,
    [property: JsonPropertyName("diagnostics")]
    IReadOnlyList<DiagnosticFact> Diagnostics,
    [property: JsonPropertyName("statements")]
    IReadOnlyList<StatementFact> Statements,
    [property: JsonPropertyName("pipeline")] PipelineFact? Pipeline,
    [property: JsonPropertyName("operators")]
    IReadOnlyList<SyntaxFact> Operators,
    [property: JsonPropertyName("functions")]
    IReadOnlyList<SyntaxFact> Functions,
    [property: JsonPropertyName("constructs")]
    IReadOnlyList<SyntaxFact> Constructs,
    [property: JsonPropertyName("assignments")]
    IReadOnlyList<AssignmentFact> Assignments,
    [property: JsonPropertyName("sourceReferences")]
    IReadOnlyList<SourceReferenceFact> SourceReferences);

internal static class Program
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    };

    private static readonly HashSet<string> PolicyNodeTypes =
    [
        "DynamicExpression",
        "ExternalDataExpression",
        "MaterializeExpression",
        "ToScalarExpression",
        "WildcardedName",
    ];

    private static readonly HashSet<string> PolicyNodeKinds =
    [
        "HasAllExpression",
        "HasAnyExpression",
        "InCsExpression",
        "NotInCsExpression",
        "BetweenExpression",
        "NotBetweenExpression",
    ];

    public static int Main()
    {
        try
        {
            var input = Console.In.ReadToEnd();
            var request = JsonSerializer.Deserialize<AnalyzerRequest>(
                input,
                JsonOptions)
                ?? throw new InvalidOperationException(
                    "Analyzer request must be a JSON object.");
            var response = Analyze(request.Query ?? string.Empty);
            Console.Out.Write(JsonSerializer.Serialize(response, JsonOptions));
            return 0;
        }
        catch (Exception exception)
        {
            Console.Error.WriteLine(exception);
            return 1;
        }
    }

    private static AnalyzerResponse Analyze(string query)
    {
        var code = KustoCode.Parse(query);
        var operators = new List<SyntaxFact>();
        var functions = new List<SyntaxFact>();
        var constructs = new List<SyntaxFact>();
        var assignments = new List<AssignmentFact>();

        code.Syntax.WalkNodes(node =>
        {
            switch (node)
            {
                case QueryOperator queryOperator:
                    operators.Add(CreateFact(query, queryOperator));
                    break;
                case FunctionCallExpression function:
                    functions.Add(
                        CreateFact(
                            query,
                            function,
                            function.Name.SimpleName));
                    break;
                case SimpleNamedExpression namedExpression:
                    assignments.Add(
                        CreateAssignmentFact(query, namedExpression));
                    break;
                case LetStatement letStatement:
                    assignments.Add(
                        CreateAssignmentFact(query, letStatement));
                    break;
                default:
                    var typeName = node.GetType().Name;
                    if (
                        PolicyNodeTypes.Contains(typeName)
                        || PolicyNodeKinds.Contains(node.Kind.ToString()))
                    {
                        constructs.Add(CreateFact(query, node));
                    }
                    else if (
                        node is NameReference nameReference
                        && nameReference.SimpleName.StartsWith(
                            "_ASIM_",
                            StringComparison.OrdinalIgnoreCase))
                    {
                        constructs.Add(
                            CreateFact(
                                query,
                                nameReference,
                                nameReference.SimpleName));
                    }
                    break;
            }
        });

        var sourceReferences = GetSourceReferences(query, code.Syntax);
        var statements = new List<StatementFact>();
        PipelineFact? pipeline = null;
        if (code.Syntax is QueryBlock queryBlock)
        {
            foreach (var separatedStatement in queryBlock.Statements)
            {
                var statement = separatedStatement.Element;
                var name = statement is LetStatement letStatement
                    ? letStatement.Name.SimpleName
                    : null;
                var expression = statement switch
                {
                    LetStatement letNode => letNode.Expression,
                    ExpressionStatement expressionNode =>
                        expressionNode.Expression,
                    _ => null,
                };
                var statementPipeline = expression is not null
                    ? CreatePipeline(query, expression)
                    : null;
                statements.Add(
                    new StatementFact(
                        statement.GetType().Name,
                        name,
                        expression is not null
                            && ContainsPipeExpression(expression),
                        statementPipeline?.RootType,
                        statementPipeline?.RootText,
                        CreateLocation(query, statement)));
            }

            var finalStatement = queryBlock.Statements.Count > 0
                ? queryBlock.Statements[
                    queryBlock.Statements.Count - 1].Element
                : null;
            if (finalStatement is ExpressionStatement expressionStatement)
            {
                pipeline = CreatePipeline(
                    query,
                    expressionStatement.Expression);
            }
        }

        var diagnostics = code.GetSyntaxDiagnostics()
            .Select(diagnostic =>
            {
                var (line, column) = GetLineAndColumn(
                    query,
                    diagnostic.Start);
                return new DiagnosticFact(
                    diagnostic.Code,
                    diagnostic.Severity,
                    diagnostic.Message,
                    diagnostic.Start,
                    diagnostic.Length,
                    line,
                    column);
            })
            .ToArray();

        return new AnalyzerResponse(
            2,
            diagnostics,
            statements,
            pipeline,
            operators,
            functions,
            constructs,
            assignments,
            sourceReferences);
    }

    private static AssignmentFact CreateAssignmentFact(
        string query,
        SimpleNamedExpression assignment)
    {
        var stringValue = assignment.Expression.LiteralValue as string;
        return new AssignmentFact(
            assignment.Name.SimpleName,
            assignment.Expression.GetType().Name,
            assignment.Expression.Kind.ToString(),
            stringValue is not null,
            stringValue,
            GetOwnerOperator(assignment),
            CreateLocation(query, assignment));
    }

    private static AssignmentFact CreateAssignmentFact(
        string query,
        LetStatement assignment)
    {
        var stringValue = assignment.Expression.LiteralValue as string;
        return new AssignmentFact(
            assignment.Name.SimpleName,
            assignment.Expression.GetType().Name,
            assignment.Expression.Kind.ToString(),
            stringValue is not null,
            stringValue,
            null,
            CreateLocation(query, assignment));
    }

    private static IReadOnlyList<SourceReferenceFact> GetSourceReferences(
        string query,
        SyntaxNode syntax)
    {
        var references = new List<SourceReferenceFact>();
        var locations = new HashSet<(int Start, int Length)>();
        syntax.WalkNodes(node =>
        {
            switch (node)
            {
                case PipeExpression pipe:
                    AddSourceReferences(
                        query,
                        pipe,
                        "pipelineRoot",
                        references,
                        locations);
                    break;
                case UnionOperator union:
                    AddUnionSourceReferences(
                        query,
                        union,
                        references,
                        locations);
                    break;
                case FunctionBody functionBody:
                    AddSourceReferences(
                        query,
                        functionBody.Expression,
                        "functionBody",
                        references,
                        locations);
                    break;
                case LetStatement letStatement:
                    AddSourceReferences(
                        query,
                        letStatement.Expression,
                        "letExpression",
                        references,
                        locations);
                    break;
                case ExpressionStatement expressionStatement:
                    AddSourceReferences(
                        query,
                        expressionStatement.Expression,
                        "statementExpression",
                        references,
                        locations);
                    break;
            }
        });
        return references;
    }

    private static void AddUnionSourceReferences(
        string query,
        UnionOperator union,
        List<SourceReferenceFact> references,
        HashSet<(int Start, int Length)> locations)
    {
        foreach (var separatedExpression in union.Expressions)
        {
            AddSourceReferences(
                query,
                separatedExpression.Element,
                "unionOperand",
                references,
                locations);
        }
    }

    private static void AddSourceReferences(
        string query,
        Expression? expression,
        string context,
        List<SourceReferenceFact> references,
        HashSet<(int Start, int Length)> locations)
    {
        if (expression is null)
        {
            return;
        }
        var root = GetPipelineRoot(expression);
        if (root is ParenthesizedExpression parenthesized)
        {
            AddSourceReferences(
                query,
                parenthesized.Expression,
                context,
                references,
                locations);
            return;
        }
        if (root is UnionOperator union)
        {
            AddUnionSourceReferences(
                query,
                union,
                references,
                locations);
            return;
        }
        if (
            root is NameReference nameReference
            && locations.Add(
                (nameReference.TextStart, nameReference.Width)))
        {
            references.Add(
                new SourceReferenceFact(
                    nameReference.SimpleName,
                    context,
                    CreateLocation(query, nameReference)));
        }
    }

    private static Expression GetPipelineRoot(Expression expression)
    {
        var root = expression;
        while (root is PipeExpression pipe)
        {
            root = pipe.Expression;
        }
        return root;
    }

    private static bool ContainsPipeExpression(Expression expression)
    {
        var containsPipe = false;
        expression.WalkNodes(node =>
        {
            if (node is PipeExpression)
            {
                containsPipe = true;
            }
        });
        return containsPipe;
    }

    private static PipelineFact CreatePipeline(
        string query,
        Expression expression)
    {
        var pipelineOperators = new List<SyntaxFact>();
        var root = expression;
        while (root is PipeExpression pipe)
        {
            pipelineOperators.Add(CreateFact(query, pipe.Operator));
            root = pipe.Expression;
        }
        pipelineOperators.Reverse();

        return new PipelineFact(
            root.GetType().Name,
            root.Kind.ToString(),
            GetText(query, root),
            pipelineOperators);
    }

    private static SyntaxFact CreateFact(
        string query,
        SyntaxNode node,
        string? name = null)
    {
        return new SyntaxFact(
            node.GetType().Name,
            node.Kind.ToString(),
            name,
            GetOwnerOperator(node),
            CreateLocation(query, node));
    }

    private static string? GetOwnerOperator(SyntaxNode node)
    {
        var current = node.Parent;
        while (current is not null)
        {
            if (current is QueryOperator queryOperator)
            {
                return queryOperator.GetType().Name;
            }
            current = current.Parent;
        }
        return null;
    }

    private static LocationFact CreateLocation(
        string query,
        SyntaxElement element)
    {
        var (line, column) = GetLineAndColumn(query, element.TextStart);
        return new LocationFact(
            element.TextStart,
            element.Width,
            line,
            column,
            GetText(query, element),
            string.Join(
                " ",
                element.GetTokens(false).Select(token => token.Text)));
    }

    private static string GetText(string query, SyntaxElement element)
    {
        if (
            element.TextStart < 0
            || element.TextStart >= query.Length
            || element.Width <= 0)
        {
            return string.Empty;
        }
        var length = Math.Min(element.Width, query.Length - element.TextStart);
        return query.Substring(element.TextStart, length);
    }

    private static (int Line, int Column) GetLineAndColumn(
        string query,
        int position)
    {
        var safePosition = Math.Clamp(position, 0, query.Length);
        var line = 1;
        var column = 1;
        for (var index = 0; index < safePosition; index++)
        {
            if (query[index] == '\n')
            {
                line++;
                column = 1;
            }
            else
            {
                column++;
            }
        }
        return (line, column);
    }
}
