using System;
using System.Collections.Generic;
using System.Linq;
using Varonis.Sentinel.Functions.Helpers;
using Varonis.Sentinel.Functions.Search.Model;

namespace Varonis.Sentinel.Functions.Search
{
    internal class AlertSearchQueryBuilder
    {
        private readonly List<Filter> _searchQueryFilters = new();

        public SearchQuery Build()
        {
            return CreateAlertQuery();
        }

        public AlertSearchQueryBuilder WithSeverity(IReadOnlyCollection<string> severities)
        {
            if (severities != null && severities.Any())
            {
                _searchQueryFilters.Add(new Filter
                {
                    Operator = EmOperator.In,
                    Path = AlertAttributes.RuleSeverityId,
                    Values = ParametersToValuesConverter.CreateMappedFilterValuesList(severities, AlertExtensions.SeverityMap)
                });
            }

            return this;
        }

        public AlertSearchQueryBuilder WithDateRange(DateTime? from, DateTime? to, string pathName)
        {
            if (from is not null && to is not null)
            {
                const string datetimeFormat = "yyyy-MM-ddTHH:mm:ss";
                _searchQueryFilters.Add(new Filter
                {
                    Operator = EmOperator.Between,
                    Path = pathName,
                    Values = new object[]
                    {
                        new
                        {
                            StartDate = from.Value.ToUniversalTime().ToString(datetimeFormat),
                            EndDate = to.Value.ToUniversalTime().ToString(datetimeFormat)
                        }
                    }
                }); ;
            }

            return this;
        }

        public AlertSearchQueryBuilder WithRules(IReadOnlyCollection<int> rules)
        {
            if (rules != null && rules.Any())
            {
                _searchQueryFilters.Add(new Filter
                {
                    Operator = EmOperator.In,
                    Path = AlertAttributes.RuleId,
                    Values = ParametersToValuesConverter.CreateValuesListFromList(rules)
                });
            }

            return this;
        }

        public AlertSearchQueryBuilder WithStatuses(IReadOnlyCollection<string> statuses)
        {
            if (statuses != null && statuses.Any())
            {
                _searchQueryFilters.Add(new Filter
                {
                    Operator = EmOperator.In,
                    Path = AlertAttributes.StatusId,
                    Values = ParametersToValuesConverter.CreateMappedFilterValuesList(statuses, AlertExtensions.StatusesMap)
                });
            }

            return this;
        }

        public AlertSearchQueryBuilder WithAlertIds(IReadOnlyCollection<Guid> ids)
        {
            if (ids != null && ids.Any())
            {
                _searchQueryFilters.Add(new Filter
                {
                    Operator = EmOperator.In,
                    Path = AlertAttributes.Id,
                    Values = ParametersToValuesConverter.CreateValuesListFromList(ids)
                });
            }

            return this;
        }

        public AlertSearchQueryBuilder WithLastDays(int? lastDays)
        {
            if (lastDays is not null)
            {
                _searchQueryFilters.Add(new Filter
                {
                    Operator = EmOperator.LastDays,
                    Path = AlertAttributes.Time,
                    Values = ParametersToValuesConverter.CreateValuesListFromParameter(lastDays)
                });
            }

            return this;
        }

        public AlertSearchQueryBuilder WithSidIds(IList<int> sidIds)
        {
            if (sidIds != null && sidIds.Any())
            {
                _searchQueryFilters.Add(new Filter
                {
                    Operator = EmOperator.In,
                    Path = AlertAttributes.SidId,
                    Values = ParametersToValuesConverter.CreateValuesListFromList(sidIds)
                });
            }

            return this;
        }

        public AlertSearchQueryBuilder WithDeviceName(IList<string> deviceNames)
        {
            if (deviceNames != null && deviceNames.Any())
            {
                _searchQueryFilters.Add(new Filter
                {
                    Operator = EmOperator.In,
                    Path = AlertAttributes.DeviceHostname,
                    Values = ParametersToValuesConverter.CreateValuesListFromList(deviceNames)
                });
            }

            return this;
        }

        public AlertSearchQueryBuilder WithAggregations()
        {
            const string value = "1";

            _searchQueryFilters.Add(new Filter
            {
                Operator = EmOperator.Equals,
                Path = AlertAttributes.Aggregate,
                Values = new List<dynamic>
                {
                    new
                    {
                        DisplayValue = AlertAttributes.Aggregate,
                        Value = value
                    }
                }
            });

            return this;
        }

        private SearchQuery CreateAlertQuery()
        {
            return new SearchQuery
            {
                EntityName = "Alert",
                Filter = new FilterGroup
                {
                    FilterOperator = FilterOperator.And,
                    Filters = _searchQueryFilters
                }
            };
        }
    }
}
