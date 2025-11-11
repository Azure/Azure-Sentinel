# ADR: Codeless Connector Framework (CCF) Architecture Adoption

**Status:** Accepted
**Date:** 2025-09-15
**Context:** Lookout Mobile Risk API v2 solution architecture decision for data ingestion method

## Context

The Lookout solution needed to migrate from the deprecated HTTP Data Collector API to a modern, scalable data ingestion architecture while supporting enhanced v2 API capabilities with 5x more data fields and new event types (SMISHING_ALERT, AUDIT).

## Decision

Adopt Azure's Codeless Connector Framework (CCF) with Data Collection Rules (DCR) for the Lookout Mobile Risk API v2 solution.

## Rationale

### Technical Factors
- **Modern Architecture**: CCF replaces deprecated HTTP Data Collector API
- **Enhanced Transformation**: DCR provides sophisticated field transformation capabilities
- **Scalability**: Native Azure scaling and performance optimization
- **Field Expansion**: Supports 50+ fields vs. previous 11 basic fields
- **Event Type Support**: Handles all v2 API event types (THREAT, DEVICE, AUDIT, SMISHING_ALERT)

### Operational Benefits
- **Reduced Maintenance**: Azure-managed infrastructure
- **Better Monitoring**: Native Azure monitoring and alerting
- **Cost Optimization**: More efficient resource utilization
- **Security**: Enhanced security controls and compliance

### Trade-offs Considered
- **Migration Complexity**: Requires careful migration from legacy connector
- **Learning Curve**: Teams need to understand DCR configuration
- **Dependency**: Increased dependency on Azure-specific technologies

## Consequences

### Positive Impacts
- **Future-Proof Architecture**: Aligned with Microsoft's strategic direction
- **Enhanced Capabilities**: Support for complex data transformations
- **Better Performance**: Optimized for Azure Log Analytics
- **Comprehensive Monitoring**: Native Azure monitoring integration

### Negative Impacts
- **Migration Risk**: Potential disruption during transition
- **Complexity**: More sophisticated configuration requirements
- **Vendor Lock-in**: Increased dependency on Azure ecosystem

### Mitigation Strategies
- **Backward Compatibility**: Maintain existing functionality during transition
- **Comprehensive Testing**: Extensive validation framework
- **Documentation**: Complete deployment and troubleshooting guides
- **Gradual Rollout**: Phased deployment approach