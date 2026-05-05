# Solution Analyzer — Selection-Criteria Association Impact

Selection-criteria (filter-field) predicates are used by `map_solutions_connectors_tables.py` to associate connectors with items (ASIM parsers and standalone / GitHub-only content items). A connector matches a target when (a) they share at least one table, and (b) the connector's per-table filter values are a **subset** of the target's (an unfiltered connector matches any target on the shared table).

Each association is rendered as a block with shared tables and both sides' predicates on separate lines, so wide filter strings remain readable. An association is correct iff every connector predicate (per shared table) appears verbatim in the target's predicates. Connector tables come from `solutions_connectors_tables_mapping_simplified.csv`; target tables come from each entity's `tables` column.

## Summary

| Target CSV | Before pairs | After pairs | Added | Removed |
|------------|--------------|-------------|-------|---------|
| `asim_parsers.csv`  | 260 | 306 | 74 | 28 |
| `content_items.csv` | 752 | 500 | 33 | 285 |

## ASIM parsers

- Items with at least one association: **before 135, after 150**
- (item, connector) pairs: **before 260, after 306** (delta +46)

## ASIM — Added associations

#### parser: [`ASimAuditEventAWSCloudTrail`](<../../../sentinelninja/Solutions Docs/asim/asimauditeventawscloudtrail.md>) ↔ [`AWS`](<../../../sentinelninja/Solutions Docs/connectors/aws.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `AWSCloudTrail.EventName in "AcceptAddressTransfer,AcceptCapacityReservationBillingOwnership,AcceptReservedInstancesExchangeQuote,AcceptTransitGatewayMulticastDomainAssociations,AcceptTransitGatewayPeeringAttachment,AcceptTransitGatewayVpcAttachment,AcceptVpcEndpointConnections,AcceptVpcPeeringConnection,AdvertiseByoipCidr,AllocateAddress,AllocateHosts,AllocateIpamPoolCidr,ApplySecurityGroupsToClientVpnTargetNetwork,AssignIpv6Addresses,AssignPrivateIpAddresses,AssignPrivateNatGatewayAddress,AssociateAddress,AssociateCapacityReservationBillingOwner,AssociateClientVpnTargetNetwork,AssociateDhcpOptions,AssociateEnclaveCertificateIamRole,AssociateIamInstanceProfile,AssociateInstanceEventWindow,AssociateIpamByoasn,AssociateIpamResourceDiscovery,AssociateNatGatewayAddress,AssociateRouteServer,AssociateRouteTable,AssociateSecurityGroupVpc,AssociateSubnetCidrBlock,AssociateTransitGatewayMulticastDomain,AssociateTransitGatewayPolicyTable,AssociateTransitGatewayRouteTable,AssociateTrunkInterface,AssociateVpcCidrBlock,AttachClassicLinkVpc,AttachInternetGateway,AttachNetworkInterface,AttachVerifiedAccessTrustProvider,AttachVolume,AttachVpnGateway,AuthorizeClientVpnIngress,AuthorizeSecurityGroupEgress,AuthorizeSecurityGroupIngress,BundleInstance,CancelBundleTask,CancelCapacityReservation,CancelCapacityReservationFleets,CancelConversionTask,CancelDeclarativePoliciesReport,CancelExportTask,CancelImageLaunchPermission,CancelImportTask,CancelReservedInstancesListing,CancelSpotFleetRequests,CancelSpotInstanceRequests,ConfirmProductInstance,CopyFpgaImage,CopyImage,CopySnapshot,CopyVolumes,CreateCapacityManagerDataExport,CreateCapacityReservation,CreateCapacityReservationBySplitting,CreateCapacityReservationFleet,CreateCarrierGateway,CreateClientVpnEndpoint,CreateClientVpnRoute,CreateCoipCidr,CreateCoipPool,CreateCustomerGateway,CreateDefaultSubnet,CreateDefaultVpc,CreateDelegateMacVolumeOwnershipTask,CreateDhcpOptions,CreateEgressOnlyInternetGateway,CreateFleet,CreateFlowLogs,CreateFpgaImage,CreateImage,CreateImageUsageReport,CreateInstanceConnectEndpoint,CreateInstanceEventWindow,CreateInstanceExportTask,CreateInternetGateway,CreateInterruptibleCapacityReservationAllocation,CreateIpam,CreateIpamExternalResourceVerificationToken,CreateIpamPolicy,CreateIpamPool,CreateIpamPrefixListResolver,CreateIpamPrefixListResolverTarget,CreateIpamResourceDiscovery,CreateIpamScope,CreateKeyPair,CreateLaunchTemplate,CreateLaunchTemplateVersion,CreateLocalGatewayRoute,CreateLocalGatewayRouteTable,CreateLocalGatewayRouteTableVirtualInterfaceGroupAssociation,CreateLocalGatewayRouteTableVpcAssociation,CreateLocalGatewayVirtualInterface,CreateLocalGatewayVirtualInterfaceGroup,CreateMacSystemIntegrityProtectionModificationTask,CreateManagedPrefixList,CreateNatGateway,CreateNetworkAcl,CreateNetworkAclEntry,CreateNetworkInsightsAccessScope,CreateNetworkInsightsPath,CreateNetworkInterface,CreateNetworkInterfacePermission,CreatePlacementGroup,CreatePublicIpv4Pool,CreateReplaceRootVolumeTask,CreateReservedInstancesListing,CreateRestoreImageTask,CreateRoute,CreateRouteServer,CreateRouteServerEndpoint,CreateRouteServerPeer,CreateRouteTable,CreateSecondaryNetwork,CreateSecondarySubnet,CreateSecurityGroup,CreateSnapshot,CreateSnapshots,CreateSpotDatafeedSubscription,CreateStoreImageTask,CreateSubnet,CreateSubnetCidrReservation,CreateTags,CreateTrafficMirrorFilter,CreateTrafficMirrorFilterRule,CreateTrafficMirrorSession,CreateTrafficMirrorTarget,CreateTransitGateway,CreateTransitGatewayConnect,CreateTransitGatewayConnectPeer,CreateTransitGatewayMeteringPolicy,CreateTransitGatewayMeteringPolicyEntry,CreateTransitGatewayMulticastDomain,CreateTransitGatewayPeeringAttachment,CreateTransitGatewayPolicyTable,CreateTransitGatewayPrefixListReference,CreateTransitGatewayRoute,CreateTransitGatewayRouteTable,CreateTransitGatewayRouteTableAnnouncement,CreateTransitGatewayVpcAttachment,CreateVerifiedAccessEndpoint,CreateVerifiedAccessGroup,CreateVerifiedAccessInstance,CreateVerifiedAccessTrustProvider,CreateVolume,CreateVpc,CreateVpcBlockPublicAccessExclusion,CreateVpcEncryptionControl,CreateVpcEndpoint,CreateVpcEndpointConnectionNotification,CreateVpcEndpointServiceConfiguration,CreateVpcPeeringConnection,CreateVpnConcentrator,CreateVpnConnection,CreateVpnConnectionRoute,CreateVpnGateway,DeleteCapacityManagerDataExport,DeleteCarrierGateway,DeleteClientVpnEndpoint,DeleteClientVpnRoute,DeleteCoipCidr,DeleteCoipPool,DeleteCustomerGateway,DeleteDhcpOptions,DeleteEgressOnlyInternetGateway,DeleteFleets,DeleteFlowLogs,DeleteFpgaImage,DeleteImageUsageReport,DeleteInstanceConnectEndpoint,DeleteInstanceEventWindow,DeleteInternetGateway,DeleteIpam,DeleteIpamExternalResourceVerificationToken,DeleteIpamPolicy,DeleteIpamPool,DeleteIpamPrefixListResolver,DeleteIpamPrefixListResolverTarget,DeleteIpamResourceDiscovery,DeleteIpamScope,DeleteKeyPair,DeleteLaunchTemplate,DeleteLaunchTemplateVersions,DeleteLocalGatewayRoute,DeleteLocalGatewayRouteTable,DeleteLocalGatewayRouteTableVirtualInterfaceGroupAssociation,DeleteLocalGatewayRouteTableVpcAssociation,DeleteLocalGatewayVirtualInterface,DeleteLocalGatewayVirtualInterfaceGroup,DeleteManagedPrefixList,DeleteNatGateway,DeleteNetworkAcl,DeleteNetworkAclEntry,DeleteNetworkInsightsAccessScope,DeleteNetworkInsightsAccessScopeAnalysis,DeleteNetworkInsightsAnalysis,DeleteNetworkInsightsPath,DeleteNetworkInterface,DeleteNetworkInterfacePermission,DeletePlacementGroup,DeletePublicIpv4Pool,DeleteQueuedReservedInstances,DeleteRoute,DeleteRouteServer,DeleteRouteServerEndpoint,DeleteRouteServerPeer,DeleteRouteTable,DeleteSecondaryNetwork,DeleteSecondarySubnet,DeleteSecurityGroup,DeleteSnapshot,DeleteSpotDatafeedSubscription,DeleteSubnet,DeleteSubnetCidrReservation,DeleteTags,DeleteTrafficMirrorFilter,DeleteTrafficMirrorFilterRule,DeleteTrafficMirrorSession,DeleteTrafficMirrorTarget,DeleteTransitGateway,DeleteTransitGatewayConnect,DeleteTransitGatewayConnectPeer,DeleteTransitGatewayMeteringPolicy,DeleteTransitGatewayMeteringPolicyEntry,DeleteTransitGatewayMulticastDomain,DeleteTransitGatewayPeeringAttachment,DeleteTransitGatewayPolicyTable,DeleteTransitGatewayPrefixListReference,DeleteTransitGatewayRoute,DeleteTransitGatewayRouteTable,DeleteTransitGatewayRouteTableAnnouncement,DeleteTransitGatewayVpcAttachment,DeleteVerifiedAccessEndpoint,DeleteVerifiedAccessGroup,DeleteVerifiedAccessInstance,DeleteVerifiedAccessTrustProvider,DeleteVolume,DeleteVpc,DeleteVpcBlockPublicAccessExclusion,DeleteVpcEncryptionControl,DeleteVpcEndpointConnectionNotifications,DeleteVpcEndpointServiceConfigurations,DeleteVpcEndpoints,DeleteVpcPeeringConnection,DeleteVpnConcentrator,DeleteVpnConnection,DeleteVpnConnectionRoute,DeleteVpnGateway,DeprovisionByoipCidr,DeprovisionIpamByoasn,DeprovisionIpamPoolCidr,DeprovisionPublicIpv4PoolCidr,DeregisterImage,DeregisterInstanceEventNotificationAttributes,DeregisterTransitGatewayMulticastGroupMembers,DeregisterTransitGatewayMulticastGroupSources,DescribeAccountAttributes,DescribeAddressTransfers,DescribeAddresses,DescribeAddressesAttribute,DescribeAggregateIdFormat,DescribeAvailabilityZones,DescribeAwsNetworkPerformanceMetricSubscriptions,DescribeBundleTasks,DescribeByoipCidrs,DescribeCapacityBlockExtensionHistory,DescribeCapacityBlockExtensionOfferings,DescribeCapacityBlockOfferings,DescribeCapacityBlockStatus,DescribeCapacityBlocks,DescribeCapacityManagerDataExports,DescribeCapacityReservationBillingRequests,DescribeCapacityReservationFleets,DescribeCapacityReservationTopology,DescribeCapacityReservations,DescribeCarrierGateways,DescribeClassicLinkInstances,DescribeClientVpnAuthorizationRules,DescribeClientVpnConnections,DescribeClientVpnEndpoints,DescribeClientVpnRoutes,DescribeClientVpnTargetNetworks,DescribeCoipPools,DescribeConversionTasks,DescribeCustomerGateways,DescribeDeclarativePoliciesReports,DescribeDhcpOptions,DescribeEgressOnlyInternetGateways,DescribeElasticGpus,DescribeExportImageTasks,DescribeExportTasks,DescribeFastLaunchImages,DescribeFastSnapshotRestores,DescribeFleetHistory,DescribeFleetInstances,DescribeFleets,DescribeFlowLogs,DescribeFpgaImageAttribute,DescribeFpgaImages,DescribeHostReservationOfferings,DescribeHostReservations,DescribeHosts,DescribeIamInstanceProfileAssociations,DescribeIdFormat,DescribeIdentityIdFormat,DescribeImageAttribute,DescribeImageReferences,DescribeImageUsageReportEntries,DescribeImageUsageReports,DescribeImages,DescribeImportImageTasks,DescribeImportSnapshotTasks,DescribeInstanceAttribute,DescribeInstanceConnectEndpoints,DescribeInstanceCreditSpecifications,DescribeInstanceEventNotificationAttributes,DescribeInstanceEventWindows,DescribeInstanceImageMetadata,DescribeInstanceSqlHaHistoryStates,DescribeInstanceSqlHaStates,DescribeInstanceStatus,DescribeInstanceTopology,DescribeInstanceTypeOfferings,DescribeInstanceTypes,DescribeInstances,DescribeInternetGateways,DescribeIpamByoasn,DescribeIpamExternalResourceVerificationTokens,DescribeIpamPolicies,DescribeIpamPools,DescribeIpamPrefixListResolverTargets,DescribeIpamPrefixListResolvers,DescribeIpamResourceDiscoveries,DescribeIpamResourceDiscoveryAssociations,DescribeIpamScopes,DescribeIpams,DescribeIpv6Pools,DescribeKeyPairs,DescribeLaunchTemplateVersions,DescribeLaunchTemplates,DescribeLocalGatewayRouteTableVirtualInterfaceGroupAssociations,DescribeLocalGatewayRouteTableVpcAssociations,DescribeLocalGatewayRouteTables,DescribeLocalGatewayVirtualInterfaceGroups,DescribeLocalGatewayVirtualInterfaces,DescribeLocalGateways,DescribeLockedSnapshots,DescribeMacHosts,DescribeMacModificationTasks,DescribeManagedPrefixLists,DescribeMovingAddresses,DescribeNatGateways,DescribeNetworkAcls,DescribeNetworkInsightsAccessScopeAnalyses,DescribeNetworkInsightsAccessScopes,DescribeNetworkInsightsAnalyses,DescribeNetworkInsightsPaths,DescribeNetworkInterfaceAttribute,DescribeNetworkInterfacePermissions,DescribeNetworkInterfaces,DescribeOutpostLags,DescribePlacementGroups,DescribePrefixLists,DescribePrincipalIdFormat,DescribePublicIpv4Pools,DescribeRegions,DescribeReplaceRootVolumeTasks,DescribeReservedInstances,DescribeReservedInstancesListings,DescribeReservedInstancesModifications,DescribeReservedInstancesOfferings,DescribeRouteServerEndpoints,DescribeRouteServerPeers,DescribeRouteServers,DescribeRouteTables,DescribeScheduledInstanceAvailability,DescribeScheduledInstances,DescribeSecondaryInterfaces,DescribeSecondaryNetworks,DescribeSecondarySubnets,DescribeSecurityGroupReferences,DescribeSecurityGroupRules,DescribeSecurityGroupVpcAssociations,DescribeSecurityGroups,DescribeServiceLinkVirtualInterfaces,DescribeSnapshotAttribute,DescribeSnapshotTierStatus,DescribeSnapshots,DescribeSpotDatafeedSubscription,DescribeSpotFleetInstances,DescribeSpotFleetRequestHistory,DescribeSpotFleetRequests,DescribeSpotInstanceRequests,DescribeSpotPriceHistory,DescribeStaleSecurityGroups,DescribeStoreImageTasks,DescribeSubnets,DescribeTags,DescribeTrafficMirrorFilterRules,DescribeTrafficMirrorFilters,DescribeTrafficMirrorSessions,DescribeTrafficMirrorTargets,DescribeTransitGatewayAttachments,DescribeTransitGatewayConnectPeers,DescribeTransitGatewayConnects,DescribeTransitGatewayMeteringPolicies,DescribeTransitGatewayMulticastDomains,DescribeTransitGatewayPeeringAttachments,DescribeTransitGatewayPolicyTables,DescribeTransitGatewayRouteTableAnnouncements,DescribeTransitGatewayRouteTables,DescribeTransitGatewayVpcAttachments,DescribeTransitGateways,DescribeTrunkInterfaceAssociations,DescribeVerifiedAccessEndpoints,DescribeVerifiedAccessGroups,DescribeVerifiedAccessInstanceLoggingConfigurations,DescribeVerifiedAccessInstances,DescribeVerifiedAccessTrustProviders,DescribeVolumeAttribute,DescribeVolumeStatus,DescribeVolumes,DescribeVolumesModifications,DescribeVpcAttribute,DescribeVpcBlockPublicAccessExclusions,DescribeVpcBlockPublicAccessOptions,DescribeVpcClassicLink,DescribeVpcClassicLinkDnsSupport,DescribeVpcEncryptionControls,DescribeVpcEndpointAssociations,DescribeVpcEndpointConnectionNotifications,DescribeVpcEndpointConnections,DescribeVpcEndpointServiceConfigurations,DescribeVpcEndpointServicePermissions,DescribeVpcEndpointServices,DescribeVpcEndpoints,DescribeVpcPeeringConnections,DescribeVpcs,DescribeVpnConcentrators,DescribeVpnConnections,DescribeVpnGateways,DetachClassicLinkVpc,DetachInternetGateway,DetachNetworkInterface,DetachVerifiedAccessTrustProvider,DetachVolume,DetachVpnGateway,DisableAddressTransfer,DisableAllowedImagesSettings,DisableAwsNetworkPerformanceMetricSubscription,DisableCapacityManager,DisableEbsEncryptionByDefault,DisableFastLaunch,DisableFastSnapshotRestores,DisableImage,DisableImageBlockPublicAccess,DisableImageDeprecation,DisableImageDeregistrationProtection,DisableInstanceSqlHaStandbyDetections,DisableIpamOrganizationAdminAccount,DisableIpamPolicy,DisableRouteServerPropagation,DisableSerialConsoleAccess,DisableSnapshotBlockPublicAccess,DisableTransitGatewayRouteTablePropagation,DisableVgwRoutePropagation,DisableVpcClassicLink,DisableVpcClassicLinkDnsSupport,DisassociateAddress,DisassociateCapacityReservationBillingOwner,DisassociateClientVpnTargetNetwork,DisassociateEnclaveCertificateIamRole,DisassociateIamInstanceProfile,DisassociateInstanceEventWindow,DisassociateIpamByoasn,DisassociateIpamResourceDiscovery,DisassociateNatGatewayAddress,DisassociateRouteServer,DisassociateRouteTable,DisassociateSecurityGroupVpc,DisassociateSubnetCidrBlock,DisassociateTransitGatewayMulticastDomain,DisassociateTransitGatewayPolicyTable,DisassociateTransitGatewayRouteTable,DisassociateTrunkInterface,DisassociateVpcCidrBlock,EnableAddressTransfer,EnableAllowedImagesSettings,EnableAwsNetworkPerformanceMetricSubscription,EnableCapacityManager,EnableEbsEncryptionByDefault,EnableFastLaunch,EnableFastSnapshotRestores,EnableImage,EnableImageBlockPublicAccess,EnableImageDeprecation,EnableImageDeregistrationProtection,EnableInstanceSqlHaStandbyDetections,EnableIpamOrganizationAdminAccount,EnableIpamPolicy,EnableRouteServerPropagation,EnableSerialConsoleAccess,EnableSnapshotBlockPublicAccess,EnableTransitGatewayRouteTablePropagation,EnableVgwRoutePropagation,EnableVolumeIO,EnableVpcClassicLink,EnableVpcClassicLinkDnsSupport,ExportClientVpnClientCertificateRevocationList,ExportClientVpnClientConfiguration,ExportImage,ExportTransitGatewayRoutes,ExportVerifiedAccessInstanceClientConfiguration,GetActiveVpnTunnelStatus,GetAllowedImagesSettings,GetAssociatedEnclaveCertificateIamRoles,GetAssociatedIpv6PoolCidrs,GetAwsNetworkPerformanceData,GetCapacityManagerAttributes,GetCapacityManagerMetricData,GetCapacityManagerMetricDimensions,GetCapacityReservationUsage,GetCoipPoolUsage,GetConsoleOutput,GetConsoleScreenshot,GetDeclarativePoliciesReportSummary,GetDefaultCreditSpecification,GetEbsDefaultKmsKeyId,GetEbsEncryptionByDefault,GetEnabledIpamPolicy,GetFlowLogsIntegrationTemplate,GetGroupsForCapacityReservation,GetHostReservationPurchasePreview,GetImageAncestry,GetImageBlockPublicAccessState,GetInstanceMetadataDefaults,GetInstanceTpmEkPub,GetInstanceTypesFromInstanceRequirements,GetInstanceUefiData,GetIpamAddressHistory,GetIpamDiscoveredAccounts,GetIpamDiscoveredPublicAddresses,GetIpamDiscoveredResourceCidrs,GetIpamPolicyAllocationRules,GetIpamPolicyOrganizationTargets,GetIpamPoolAllocations,GetIpamPoolCidrs,GetIpamPrefixListResolverRules,GetIpamPrefixListResolverVersionEntries,GetIpamPrefixListResolverVersions,GetIpamResourceCidrs,GetLaunchTemplateData,GetManagedPrefixListAssociations,GetManagedPrefixListEntries,GetNetworkInsightsAccessScopeAnalysisFindings,GetNetworkInsightsAccessScopeContent,GetPasswordData,GetReservedInstancesExchangeQuote,GetRouteServerAssociations,GetRouteServerPropagations,GetRouteServerRoutingDatabase,GetSecurityGroupsForVpc,GetSerialConsoleAccessStatus,GetSnapshotBlockPublicAccessState,GetSpotPlacementScores,GetSubnetCidrReservations,GetTransitGatewayAttachmentPropagations,GetTransitGatewayMeteringPolicyEntries,GetTransitGatewayMulticastDomainAssociations,GetTransitGatewayPolicyTableAssociations,GetTransitGatewayPolicyTableEntries,GetTransitGatewayPrefixListReferences,GetTransitGatewayRouteTableAssociations,GetTransitGatewayRouteTablePropagations,GetVerifiedAccessEndpointPolicy,GetVerifiedAccessEndpointTargets,GetVerifiedAccessGroupPolicy,GetVpcResourcesBlockingEncryptionEnforcement,GetVpnConnectionDeviceSampleConfiguration,GetVpnConnectionDeviceTypes,GetVpnTunnelReplacementStatus,ImportClientVpnClientCertificateRevocationList,ImportImage,ImportInstance,ImportKeyPair,ImportSnapshot,ImportVolume,ListImagesInRecycleBin,ListSnapshotsInRecycleBin,ListVolumesInRecycleBin,LockSnapshot,ModifyAddressAttribute,ModifyAvailabilityZoneGroup,ModifyCapacityReservation,ModifyCapacityReservationFleet,ModifyClientVpnEndpoint,ModifyDefaultCreditSpecification,ModifyEbsDefaultKmsKeyId,ModifyFleet,ModifyFpgaImageAttribute,ModifyHosts,ModifyIdFormat,ModifyIdentityIdFormat,ModifyImageAttribute,ModifyInstanceAttribute,ModifyInstanceCapacityReservationAttributes,ModifyInstanceConnectEndpoint,ModifyInstanceCpuOptions,ModifyInstanceCreditSpecification,ModifyInstanceEventStartTime,ModifyInstanceEventWindow,ModifyInstanceMaintenanceOptions,ModifyInstanceMetadataDefaults,ModifyInstanceMetadataOptions,ModifyInstanceNetworkPerformanceOptions,ModifyInstancePlacement,ModifyIpam,ModifyIpamPolicyAllocationRules,ModifyIpamPool,ModifyIpamPrefixListResolver,ModifyIpamPrefixListResolverTarget,ModifyIpamResourceCidr,ModifyIpamResourceDiscovery,ModifyIpamScope,ModifyLaunchTemplate,ModifyLocalGatewayRoute,ModifyManagedPrefixList,ModifyNetworkInterfaceAttribute,ModifyPrivateDnsNameOptions,ModifyPublicIpDnsNameOptions,ModifyReservedInstances,ModifyRouteServer,ModifySecurityGroupRules,ModifySnapshotAttribute,ModifySnapshotTier,ModifySpotFleetRequest,ModifySubnetAttribute,ModifyTrafficMirrorFilterNetworkServices,ModifyTrafficMirrorFilterRule,ModifyTrafficMirrorSession,ModifyTransitGateway,ModifyTransitGatewayMeteringPolicy,ModifyTransitGatewayPrefixListReference,ModifyTransitGatewayVpcAttachment,ModifyVerifiedAccessEndpoint,ModifyVerifiedAccessEndpointPolicy,ModifyVerifiedAccessGroup,ModifyVerifiedAccessGroupPolicy,ModifyVerifiedAccessInstance,ModifyVerifiedAccessInstanceLoggingConfiguration,ModifyVerifiedAccessTrustProvider,ModifyVolume,ModifyVolumeAttribute,ModifyVpcAttribute,ModifyVpcBlockPublicAccessExclusion,ModifyVpcBlockPublicAccessOptions,ModifyVpcEncryptionControl,ModifyVpcEndpoint,ModifyVpcEndpointConnectionNotification,ModifyVpcEndpointServiceConfiguration,ModifyVpcEndpointServicePayerResponsibility,ModifyVpcEndpointServicePermissions,ModifyVpcPeeringConnectionOptions,ModifyVpcTenancy,ModifyVpnConnection,ModifyVpnConnectionOptions,ModifyVpnTunnelCertificate,ModifyVpnTunnelOptions,MonitorInstances,MoveAddressToVpc,MoveByoipCidrToIpam,MoveCapacityReservationInstances,ProvisionByoipCidr,ProvisionIpamByoasn,ProvisionIpamPoolCidr,ProvisionPublicIpv4PoolCidr,PurchaseCapacityBlock,PurchaseCapacityBlockExtension,PurchaseHostReservation,PurchaseReservedInstancesOffering,PurchaseScheduledInstances,RebootInstances,RegisterImage,RegisterInstanceEventNotificationAttributes,RegisterTransitGatewayMulticastGroupMembers,RegisterTransitGatewayMulticastGroupSources,RejectCapacityReservationBillingOwnership,RejectTransitGatewayMulticastDomainAssociations,RejectTransitGatewayPeeringAttachment,RejectTransitGatewayVpcAttachment,RejectVpcEndpointConnections,RejectVpcPeeringConnection,ReleaseAddress,ReleaseHosts,ReleaseIpamPoolAllocation,ReplaceIamInstanceProfileAssociation,ReplaceImageCriteriaInAllowedImagesSettings,ReplaceNetworkAclAssociation,ReplaceNetworkAclEntry,ReplaceRoute,ReplaceRouteTableAssociation,ReplaceTransitGatewayRoute,ReplaceVpnTunnel,ReportInstanceStatus,RequestSpotFleet,RequestSpotInstances,ResetAddressAttribute,ResetEbsDefaultKmsKeyId,ResetFpgaImageAttribute,ResetImageAttribute,ResetInstanceAttribute,ResetNetworkInterfaceAttribute,ResetSnapshotAttribute,RestoreAddressToClassic,RestoreImageFromRecycleBin,RestoreManagedPrefixListVersion,RestoreSnapshotFromRecycleBin,RestoreSnapshotTier,RestoreVolumeFromRecycleBin,RevokeClientVpnIngress,RevokeSecurityGroupEgress,RevokeSecurityGroupIngress,RunInstances,RunScheduledInstances,SearchLocalGatewayRoutes,SearchTransitGatewayMulticastGroups,SearchTransitGatewayRoutes,SendDiagnosticInterrupt,StartDeclarativePoliciesReport,StartInstances,StartNetworkInsightsAccessScopeAnalysis,StartNetworkInsightsAnalysis,StartVpcEndpointServicePrivateDnsVerification,StopInstances,TerminateClientVpnConnections,TerminateInstances,UnassignIpv6Addresses,UnassignPrivateIpAddresses,UnassignPrivateNatGatewayAddress,UnlockSnapshot,UnmonitorInstances,UpdateCapacityManagerOrganizationsAccess,UpdateInterruptibleCapacityReservationAllocation,UpdateSecurityGroupRuleDescriptionsEgress,UpdateSecurityGroupRuleDescriptionsIngress,WithdrawByoipCidr"`
  - `AWSCloudTrail.EventSource == "ec2.amazonaws.com"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuditEventBarracudaCEF`](<../../../sentinelninja/Solutions Docs/asim/asimauditeventbarracudacef.md>) ↔ [`Barracuda`](<../../../sentinelninja/Solutions Docs/connectors/barracuda.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct in "WAAS,WAF"`
  - `CommonSecurityLog.DeviceVendor startswith "Barracuda"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceVendor == "Barracuda"`

#### parser: [`ASimAuditEventCrowdStrikeFalconHost`](<../../../sentinelninja/Solutions Docs/asim/asimauditeventcrowdstrikefalconhost.md>) ↔ [`CrowdStrikeFalconEndpointProtection`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikefalconendpointprotection.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "UserActivityAuditEvent"`
  - `CommonSecurityLog.DeviceProduct == "FalconHost"`
  - `CommonSecurityLog.DeviceVendor == "CrowdStrike"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct == "FalconHost"`
  - `CommonSecurityLog.DeviceVendor == "CrowdStrike"`
  - `_Computed.DeviceCustomDate1Label in "DNS Request Time,DocAccessTimestamp,Document Accessed Timestamp,ExeWrittenTimestamp,Network Access Timestamp"`
  - `_Computed.DeviceCustomDate2Label in "HashSpreadingEventTime,HashSpreadingSensorEventTime"`
  - `_Computed.DeviceCustomNumber2Label == "ProcessId"`
  - `_Computed.DeviceCustomNumber3Label == "Offset"`
  - `_Computed.DeviceCustomString2Label in "AccessedDocFileName,QuarantineFileSHA256,ScanResultEngine,WrittenExeFileName"`
  - `_Computed.DeviceCustomString3Label in "AccessedDocFilePath,QuarantineFilePath,WrittenExeFilePath"`
  - `_Computed.DeviceCustomString4Label == "ScanResultVersion"`
  - `_Computed.DeviceCustomString5Label == "CommandLine"`
  - `_Computed.DeviceCustomString6Label == "FalconHostLink"`
  - `_Computed.LogSeverity in "1,2,3,4,5"`

#### parser: [`ASimAuditEventCrowdStrikeFalconHost`](<../../../sentinelninja/Solutions Docs/asim/asimauditeventcrowdstrikefalconhost.md>) ↔ [`CrowdStrikeFalconEndpointProtectionAma`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikefalconendpointprotectionama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "UserActivityAuditEvent"`
  - `CommonSecurityLog.DeviceProduct == "FalconHost"`
  - `CommonSecurityLog.DeviceVendor == "CrowdStrike"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "FalconHost"`
  - `CommonSecurityLog.DeviceVendor =~ "CrowdStrike"`
  - `_Computed.DeviceCustomDate1Label in "DNS Request Time,DocAccessTimestamp,Document Accessed Timestamp,ExeWrittenTimestamp,Network Access Timestamp"`
  - `_Computed.DeviceCustomDate2Label in "HashSpreadingEventTime,HashSpreadingSensorEventTime"`
  - `_Computed.DeviceCustomNumber2Label == "ProcessId"`
  - `_Computed.DeviceCustomNumber3Label == "Offset"`
  - `_Computed.DeviceCustomString2Label in "AccessedDocFileName,QuarantineFileSHA256,ScanResultEngine,WrittenExeFileName"`
  - `_Computed.DeviceCustomString3Label in "AccessedDocFilePath,QuarantineFilePath,WrittenExeFilePath"`
  - `_Computed.DeviceCustomString4Label == "ScanResultVersion"`
  - `_Computed.DeviceCustomString5Label == "CommandLine"`
  - `_Computed.DeviceCustomString6Label == "FalconHostLink"`
  - `_Computed.LogSeverity in "1,2,3,4,5"`

#### parser: [`ASimAuditEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimauditeventnative.md>) ↔ [`SynqlyIntegrationConnector`](<../../../sentinelninja/Solutions Docs/connectors/synqlyintegrationconnector.md>)

- **Shared tables:** asimauditeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationBarracudaWAF`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationbarracudawaf.md>) ↔ [`Barracuda`](<../../../sentinelninja/Solutions Docs/connectors/barracuda.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct in "WAAS,WAF"`
  - `CommonSecurityLog.DeviceVendor startswith "Barracuda"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceVendor == "Barracuda"`

#### parser: [`ASimAuthenticationCiscoIOS`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationciscoios.md>) ↔ [`SyslogAma`](<../../../sentinelninja/Solutions Docs/connectors/syslogama.md>)

- **Shared tables:** syslog
- **Target predicates:**
  - `Syslog.SyslogMessage has "%SEC_LOGIN-4-LOGIN_FAILED"`
  - `Syslog.SyslogMessage has "%SEC_LOGIN-5-LOGIN_SUCCESS"`
  - `Syslog.SyslogMessage has "%SYS-6-LOGOUT"`
- **Connector predicates:**
  - `Syslog.Facility != "cron"`

#### parser: [`ASimAuthenticationCiscoISEAdministrator`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationciscoiseadministrator.md>) ↔ [`SyslogAma`](<../../../sentinelninja/Solutions Docs/connectors/syslogama.md>)

- **Shared tables:** syslog
- **Target predicates:**
  - `Syslog.ProcessName has "CISE_Administrative_and_Operational_Audit"`
  - `Syslog.SyslogMessage has "Administrator-Login"`
- **Connector predicates:**
  - `Syslog.Facility != "cron"`

#### parser: [`ASimAuthenticationCrowdStrikeFalconHost`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationcrowdstrikefalconhost.md>) ↔ [`CrowdStrikeFalconEndpointProtection`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikefalconendpointprotection.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID in "twoFactorAuthenticate,userAuthenticate"`
  - `CommonSecurityLog.DeviceProduct == "FalconHost"`
  - `CommonSecurityLog.DeviceVendor == "CrowdStrike"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct == "FalconHost"`
  - `CommonSecurityLog.DeviceVendor == "CrowdStrike"`
  - `_Computed.DeviceCustomDate1Label in "DNS Request Time,DocAccessTimestamp,Document Accessed Timestamp,ExeWrittenTimestamp,Network Access Timestamp"`
  - `_Computed.DeviceCustomDate2Label in "HashSpreadingEventTime,HashSpreadingSensorEventTime"`
  - `_Computed.DeviceCustomNumber2Label == "ProcessId"`
  - `_Computed.DeviceCustomNumber3Label == "Offset"`
  - `_Computed.DeviceCustomString2Label in "AccessedDocFileName,QuarantineFileSHA256,ScanResultEngine,WrittenExeFileName"`
  - `_Computed.DeviceCustomString3Label in "AccessedDocFilePath,QuarantineFilePath,WrittenExeFilePath"`
  - `_Computed.DeviceCustomString4Label == "ScanResultVersion"`
  - `_Computed.DeviceCustomString5Label == "CommandLine"`
  - `_Computed.DeviceCustomString6Label == "FalconHostLink"`
  - `_Computed.LogSeverity in "1,2,3,4,5"`

#### parser: [`ASimAuthenticationCrowdStrikeFalconHost`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationcrowdstrikefalconhost.md>) ↔ [`CrowdStrikeFalconEndpointProtectionAma`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikefalconendpointprotectionama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID in "twoFactorAuthenticate,userAuthenticate"`
  - `CommonSecurityLog.DeviceProduct == "FalconHost"`
  - `CommonSecurityLog.DeviceVendor == "CrowdStrike"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "FalconHost"`
  - `CommonSecurityLog.DeviceVendor =~ "CrowdStrike"`
  - `_Computed.DeviceCustomDate1Label in "DNS Request Time,DocAccessTimestamp,Document Accessed Timestamp,ExeWrittenTimestamp,Network Access Timestamp"`
  - `_Computed.DeviceCustomDate2Label in "HashSpreadingEventTime,HashSpreadingSensorEventTime"`
  - `_Computed.DeviceCustomNumber2Label == "ProcessId"`
  - `_Computed.DeviceCustomNumber3Label == "Offset"`
  - `_Computed.DeviceCustomString2Label in "AccessedDocFileName,QuarantineFileSHA256,ScanResultEngine,WrittenExeFileName"`
  - `_Computed.DeviceCustomString3Label in "AccessedDocFilePath,QuarantineFilePath,WrittenExeFilePath"`
  - `_Computed.DeviceCustomString4Label == "ScanResultVersion"`
  - `_Computed.DeviceCustomString5Label == "CommandLine"`
  - `_Computed.DeviceCustomString6Label == "FalconHostLink"`
  - `_Computed.LogSeverity in "1,2,3,4,5"`

#### parser: [`ASimAuthenticationFortinetFortigate`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationfortinetfortigate.md>) ↔ [`CefAma`](<../../../sentinelninja/Solutions Docs/connectors/cefama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID !in "0100022949,0100022952"`
  - `CommonSecurityLog.DeviceProduct has "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.status in "failed,success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationFortinetFortigate`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationfortinetfortigate.md>) ↔ [`Fortinet`](<../../../sentinelninja/Solutions Docs/connectors/fortinet.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID !in "0100022949,0100022952"`
  - `CommonSecurityLog.DeviceProduct has "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.status in "failed,success"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`

#### parser: [`ASimAuthenticationFortinetFortigate`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationfortinetfortigate.md>) ↔ [`FortinetAma`](<../../../sentinelninja/Solutions Docs/connectors/fortinetama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID !in "0100022949,0100022952"`
  - `CommonSecurityLog.DeviceProduct has "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.status in "failed,success"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "Fortigate"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`

#### parser: [`ASimAuthenticationFortinetFortigate`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationfortinetfortigate.md>) ↔ [`VirtualMetricDirectorProxy`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricdirectorproxy.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID !in "0100022949,0100022952"`
  - `CommonSecurityLog.DeviceProduct has "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.status in "failed,success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationFortinetFortigate`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationfortinetfortigate.md>) ↔ [`VirtualMetricMSSentinelConnector`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricmssentinelconnector.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID !in "0100022949,0100022952"`
  - `CommonSecurityLog.DeviceProduct has "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.status in "failed,success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationFortinetFortigate`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationfortinetfortigate.md>) ↔ [`VirtualMetricMSSentinelDataLakeConnector`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricmssentineldatalakeconnector.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID !in "0100022949,0100022952"`
  - `CommonSecurityLog.DeviceProduct has "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.status in "failed,success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationGoogleWorkspace`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationgoogleworkspace.md>) ↔ [`GoogleWorkspaceReportsAPI`](<../../../sentinelninja/Solutions Docs/connectors/googleworkspacereportsapi.md>)

- **Shared tables:** gworkspace_reportsapi_login_cl
- **Target predicates:**
  - `_Computed.event_name_s in "login_challenge,login_verification,suspicious_login,suspicious_login_less_secure_app,suspicious_programmatic_login,user_signed_out_due_to_suspicious_session_cookie"`
  - `_Computed.login_challenge_status_s in "incorrect_answer_entered,passed"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationNative`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationnative.md>) ↔ [`SynqlyIntegrationConnector`](<../../../sentinelninja/Solutions Docs/connectors/synqlyintegrationconnector.md>)

- **Shared tables:** asimauthenticationeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationPaloAltoCortexDataLake`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpaloaltocortexdatalake.md>) ↔ [`PaloAltoCDL`](<../../../sentinelninja/Solutions Docs/connectors/paloaltocdl.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "AUTH"`
  - `CommonSecurityLog.DeviceProduct == "LF"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.EventMessage has "Invalid Certificate"`
  - `_Computed.FieldDeviceCustomNumber1 in "1,2,3"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "LF"`
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
  - `_Computed.DeviceCustomIPv6Address2Label == "Source IPv6 Address"`
  - `_Computed.DeviceCustomIPv6Address3Label == "Destination IPv6 Address"`
  - `_Computed.DeviceCustomNumber1Label == "SessionID"`
  - `_Computed.DeviceCustomNumber2Label == "PacketsTotal"`
  - `_Computed.DeviceCustomNumber3Label == "SessionDuration"`
  - `_Computed.DeviceCustomString4Label == "FromZone"`
  - `_Computed.DeviceCustomString5Label == "Zone"`

#### parser: [`ASimAuthenticationPaloAltoCortexDataLake`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpaloaltocortexdatalake.md>) ↔ [`PaloAltoCDLAma`](<../../../sentinelninja/Solutions Docs/connectors/paloaltocdlama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "AUTH"`
  - `CommonSecurityLog.DeviceProduct == "LF"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.EventMessage has "Invalid Certificate"`
  - `_Computed.FieldDeviceCustomNumber1 in "1,2,3"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "LF"`
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
  - `_Computed.DeviceCustomIPv6Address2Label == "Source IPv6 Address"`
  - `_Computed.DeviceCustomIPv6Address3Label == "Destination IPv6 Address"`
  - `_Computed.DeviceCustomNumber1Label == "SessionID"`
  - `_Computed.DeviceCustomNumber2Label == "PacketsTotal"`
  - `_Computed.DeviceCustomNumber3Label == "SessionDuration"`
  - `_Computed.DeviceCustomString4Label == "FromZone"`
  - `_Computed.DeviceCustomString5Label == "Zone"`

#### parser: [`ASimAuthenticationPaloAltoGlobalProtect`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpaloaltoglobalprotect.md>) ↔ [`CefAma`](<../../../sentinelninja/Solutions Docs/connectors/cefama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "GLOBALPROTECT"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.EventResult == "Success"`
  - `_Computed.PanOSAuthMethod in~ "Cookie,Kerberos,LDAP,RADIUS,SAML,TACACS+,certificate,local-database"`
  - `_Computed.PanOSEventID in~ "gateway-auth,gateway-connected,gateway-login,gateway-logout,portal-auth,portal-prelogin"`
  - `_Computed.PanOSEventStatus in~ "failure,success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationPaloAltoGlobalProtect`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpaloaltoglobalprotect.md>) ↔ [`VirtualMetricDirectorProxy`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricdirectorproxy.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "GLOBALPROTECT"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.EventResult == "Success"`
  - `_Computed.PanOSAuthMethod in~ "Cookie,Kerberos,LDAP,RADIUS,SAML,TACACS+,certificate,local-database"`
  - `_Computed.PanOSEventID in~ "gateway-auth,gateway-connected,gateway-login,gateway-logout,portal-auth,portal-prelogin"`
  - `_Computed.PanOSEventStatus in~ "failure,success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationPaloAltoGlobalProtect`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpaloaltoglobalprotect.md>) ↔ [`VirtualMetricMSSentinelConnector`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricmssentinelconnector.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "GLOBALPROTECT"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.EventResult == "Success"`
  - `_Computed.PanOSAuthMethod in~ "Cookie,Kerberos,LDAP,RADIUS,SAML,TACACS+,certificate,local-database"`
  - `_Computed.PanOSEventID in~ "gateway-auth,gateway-connected,gateway-login,gateway-logout,portal-auth,portal-prelogin"`
  - `_Computed.PanOSEventStatus in~ "failure,success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationPaloAltoGlobalProtect`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpaloaltoglobalprotect.md>) ↔ [`VirtualMetricMSSentinelDataLakeConnector`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricmssentineldatalakeconnector.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "GLOBALPROTECT"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.EventResult == "Success"`
  - `_Computed.PanOSAuthMethod in~ "Cookie,Kerberos,LDAP,RADIUS,SAML,TACACS+,certificate,local-database"`
  - `_Computed.PanOSEventID in~ "gateway-auth,gateway-connected,gateway-login,gateway-logout,portal-auth,portal-prelogin"`
  - `_Computed.PanOSEventStatus in~ "failure,success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationPaloAltoPanOS`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpaloaltopanos.md>) ↔ [`CefAma`](<../../../sentinelninja/Solutions Docs/connectors/cefama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID startswith "auth"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.EventResult in "Failure,Success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationPaloAltoPanOS`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpaloaltopanos.md>) ↔ [`VirtualMetricDirectorProxy`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricdirectorproxy.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID startswith "auth"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.EventResult in "Failure,Success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationPaloAltoPanOS`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpaloaltopanos.md>) ↔ [`VirtualMetricMSSentinelConnector`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricmssentinelconnector.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID startswith "auth"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.EventResult in "Failure,Success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationPaloAltoPanOS`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpaloaltopanos.md>) ↔ [`VirtualMetricMSSentinelDataLakeConnector`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricmssentineldatalakeconnector.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID startswith "auth"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.EventResult in "Failure,Success"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationPostgreSQL`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationpostgresql.md>) ↔ [`PostgreSQL`](<../../../sentinelninja/Solutions Docs/connectors/postgresql.md>)

- **Shared tables:** postgresql_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationSalesforceSC`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationsalesforcesc.md>) ↔ [`SalesforceServiceCloud`](<../../../sentinelninja/Solutions Docs/connectors/salesforceservicecloud.md>)

- **Shared tables:** salesforceservicecloud_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationVMwareVCenter`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationvmwarevcenter.md>) ↔ [`CustomlogsviaAMA`](<../../../sentinelninja/Solutions Docs/connectors/customlogsviaama.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimAuthenticationVMwareVCenter`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationvmwarevcenter.md>) ↔ [`VMwarevCenter`](<../../../sentinelninja/Solutions Docs/connectors/vmwarevcenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimDhcpEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimdhcpeventnative.md>) ↔ [`SynqlyIntegrationConnector`](<../../../sentinelninja/Solutions Docs/connectors/synqlyintegrationconnector.md>)

- **Shared tables:** asimdhcpeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimDnsFortinetFortiGate`](<../../../sentinelninja/Solutions Docs/asim/asimdnsfortinetfortigate.md>) ↔ [`Fortinet`](<../../../sentinelninja/Solutions Docs/connectors/fortinet.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID endswith "54000"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54200"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54400"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54401"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54600"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54601"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54800"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54801"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54802"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54803"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54804"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54805"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.DnsQueryTypeName == "Unknown"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`

#### parser: [`ASimDnsFortinetFortiGate`](<../../../sentinelninja/Solutions Docs/asim/asimdnsfortinetfortigate.md>) ↔ [`FortinetAma`](<../../../sentinelninja/Solutions Docs/connectors/fortinetama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID endswith "54000"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54200"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54400"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54401"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54600"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54601"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54800"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54801"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54802"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54803"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54804"`
  - `CommonSecurityLog.DeviceEventClassID endswith "54805"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.DnsQueryTypeName == "Unknown"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "Fortigate"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`

#### parser: [`ASimDnsGcp`](<../../../sentinelninja/Solutions Docs/asim/asimdnsgcp.md>) ↔ [`GCPDNSDataConnector`](<../../../sentinelninja/Solutions Docs/connectors/gcpdnsdataconnector.md>)

- **Shared tables:** gcp_dns_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimDnsNative`](<../../../sentinelninja/Solutions Docs/asim/asimdnsnative.md>) ↔ [`SynqlyIntegrationConnector`](<../../../sentinelninja/Solutions Docs/connectors/synqlyintegrationconnector.md>)

- **Shared tables:** asimdnsactivitylogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimFileEventAWSCloudTrail`](<../../../sentinelninja/Solutions Docs/asim/asimfileeventawscloudtrail.md>) ↔ [`AWS`](<../../../sentinelninja/Solutions Docs/connectors/aws.md>)

- **Shared tables:** awscloudtrail
- **Target predicates:**
  - `AWSCloudTrail.EventSource == "s3.amazonaws.com"`
  - `_Computed.type in "AWS::S3::Bucket,AWS::S3::Object"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimFileEventGoogleWorkspace`](<../../../sentinelninja/Solutions Docs/asim/asimfileeventgoogleworkspace.md>) ↔ [`GoogleWorkspaceReportsAPI`](<../../../sentinelninja/Solutions Docs/connectors/googleworkspacereportsapi.md>)

- **Shared tables:** gworkspace_reportsapi_drive_cl
- **Target predicates:**
  - `_Computed.TargetFileMimeType == "folder"`
  - `_Computed.event_name_s in "add_lock,add_to_folder,approval_canceled,approval_comment_added,approval_completed,approval_decisions_reset,approval_due_time_change,approval_requested,approval_reviewer_change,approval_reviewer_responded,copy,create,create_comment,delete,delete_comment,deny_access_request,download,edit,edit_comment,expire_access_request,move,preview,print,reassign_comment,remove_from_folder,remove_lock,rename,reopen_comment,request_access,resolve_comment,source_copy,trash,untrash,upload,view"`
  - `_Computed.event_name_s has "source_copy"`
  - `_Computed.event_name_s has_any "move"`
  - `_Computed.event_name_s has_any "rename"`
  - `_Computed.id_applicationName_s == "drive"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimFileEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimfileeventnative.md>) ↔ [`SynqlyIntegrationConnector`](<../../../sentinelninja/Solutions Docs/connectors/synqlyintegrationconnector.md>)

- **Shared tables:** asimfileeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimNetworkSessionBarracudaCEF`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionbarracudacef.md>) ↔ [`Barracuda`](<../../../sentinelninja/Solutions Docs/connectors/barracuda.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct in "WAAS,WAF"`
  - `CommonSecurityLog.DeviceVendor startswith "Barracuda"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceVendor == "Barracuda"`

#### parser: [`ASimNetworkSessionCheckPointSmartDefense`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessioncheckpointsmartdefense.md>) ↔ [`CefAma`](<../../../sentinelninja/Solutions Docs/connectors/cefama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct == "SmartDefense"`
  - `CommonSecurityLog.DeviceVendor == "Check Point"`
  - `_Computed.CommunicationDirection in "0,1"`
  - `_Computed.DeviceCustomString1Label == "Threat Prevention Rule Name"`
  - `_Computed.DeviceCustomString2Label == "Protection ID"`
  - `_Computed.DeviceCustomString3Label == "Protection Type"`
  - `_Computed.DeviceCustomString4Label in "Protection Name,Threat Prevention Rule ID"`
  - `_Computed.DvcAction == "Allow"`
  - `_Computed.FlexNumber1Label == "Confidence"`
  - `_Computed.FlexNumber2Label == "Performance Impact"`
  - `_Computed.FlexString2Label == "Attack Information"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimNetworkSessionCheckPointSmartDefense`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessioncheckpointsmartdefense.md>) ↔ [`VirtualMetricDirectorProxy`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricdirectorproxy.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct == "SmartDefense"`
  - `CommonSecurityLog.DeviceVendor == "Check Point"`
  - `_Computed.CommunicationDirection in "0,1"`
  - `_Computed.DeviceCustomString1Label == "Threat Prevention Rule Name"`
  - `_Computed.DeviceCustomString2Label == "Protection ID"`
  - `_Computed.DeviceCustomString3Label == "Protection Type"`
  - `_Computed.DeviceCustomString4Label in "Protection Name,Threat Prevention Rule ID"`
  - `_Computed.DvcAction == "Allow"`
  - `_Computed.FlexNumber1Label == "Confidence"`
  - `_Computed.FlexNumber2Label == "Performance Impact"`
  - `_Computed.FlexString2Label == "Attack Information"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimNetworkSessionCheckPointSmartDefense`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessioncheckpointsmartdefense.md>) ↔ [`VirtualMetricMSSentinelConnector`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricmssentinelconnector.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct == "SmartDefense"`
  - `CommonSecurityLog.DeviceVendor == "Check Point"`
  - `_Computed.CommunicationDirection in "0,1"`
  - `_Computed.DeviceCustomString1Label == "Threat Prevention Rule Name"`
  - `_Computed.DeviceCustomString2Label == "Protection ID"`
  - `_Computed.DeviceCustomString3Label == "Protection Type"`
  - `_Computed.DeviceCustomString4Label in "Protection Name,Threat Prevention Rule ID"`
  - `_Computed.DvcAction == "Allow"`
  - `_Computed.FlexNumber1Label == "Confidence"`
  - `_Computed.FlexNumber2Label == "Performance Impact"`
  - `_Computed.FlexString2Label == "Attack Information"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimNetworkSessionCheckPointSmartDefense`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessioncheckpointsmartdefense.md>) ↔ [`VirtualMetricMSSentinelDataLakeConnector`](<../../../sentinelninja/Solutions Docs/connectors/virtualmetricmssentineldatalakeconnector.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct == "SmartDefense"`
  - `CommonSecurityLog.DeviceVendor == "Check Point"`
  - `_Computed.CommunicationDirection in "0,1"`
  - `_Computed.DeviceCustomString1Label == "Threat Prevention Rule Name"`
  - `_Computed.DeviceCustomString2Label == "Protection ID"`
  - `_Computed.DeviceCustomString3Label == "Protection Type"`
  - `_Computed.DeviceCustomString4Label in "Protection Name,Threat Prevention Rule ID"`
  - `_Computed.DvcAction == "Allow"`
  - `_Computed.FlexNumber1Label == "Confidence"`
  - `_Computed.FlexNumber2Label == "Performance Impact"`
  - `_Computed.FlexString2Label == "Attack Information"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimNetworkSessionCrowdStrikeFalconHost`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessioncrowdstrikefalconhost.md>) ↔ [`CrowdStrikeFalconEndpointProtection`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikefalconendpointprotection.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID in "FirewallMatchEvent,Network Access In A Detection Summary Event"`
  - `CommonSecurityLog.DeviceEventClassID has "Network Access In A Detection Summary Event"`
  - `CommonSecurityLog.DeviceProduct == "FalconHost"`
  - `CommonSecurityLog.DeviceVendor == "CrowdStrike"`
  - `_Computed.DstIpAddr contains "."`
  - `_Computed.DstIpAddr contains ":"`
  - `_Computed.Hostname matchesregex "(([0-9]{1,3})\\.([0-9]{1,3})\\.([0-9]{1,3})\\.(([0-9]{1,3})))"`
  - `_Computed.connectionDirection in "1,2"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct == "FalconHost"`
  - `CommonSecurityLog.DeviceVendor == "CrowdStrike"`
  - `_Computed.DeviceCustomDate1Label in "DNS Request Time,DocAccessTimestamp,Document Accessed Timestamp,ExeWrittenTimestamp,Network Access Timestamp"`
  - `_Computed.DeviceCustomDate2Label in "HashSpreadingEventTime,HashSpreadingSensorEventTime"`
  - `_Computed.DeviceCustomNumber2Label == "ProcessId"`
  - `_Computed.DeviceCustomNumber3Label == "Offset"`
  - `_Computed.DeviceCustomString2Label in "AccessedDocFileName,QuarantineFileSHA256,ScanResultEngine,WrittenExeFileName"`
  - `_Computed.DeviceCustomString3Label in "AccessedDocFilePath,QuarantineFilePath,WrittenExeFilePath"`
  - `_Computed.DeviceCustomString4Label == "ScanResultVersion"`
  - `_Computed.DeviceCustomString5Label == "CommandLine"`
  - `_Computed.DeviceCustomString6Label == "FalconHostLink"`
  - `_Computed.LogSeverity in "1,2,3,4,5"`

#### parser: [`ASimNetworkSessionCrowdStrikeFalconHost`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessioncrowdstrikefalconhost.md>) ↔ [`CrowdStrikeFalconEndpointProtectionAma`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikefalconendpointprotectionama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID in "FirewallMatchEvent,Network Access In A Detection Summary Event"`
  - `CommonSecurityLog.DeviceEventClassID has "Network Access In A Detection Summary Event"`
  - `CommonSecurityLog.DeviceProduct == "FalconHost"`
  - `CommonSecurityLog.DeviceVendor == "CrowdStrike"`
  - `_Computed.DstIpAddr contains "."`
  - `_Computed.DstIpAddr contains ":"`
  - `_Computed.Hostname matchesregex "(([0-9]{1,3})\\.([0-9]{1,3})\\.([0-9]{1,3})\\.(([0-9]{1,3})))"`
  - `_Computed.connectionDirection in "1,2"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "FalconHost"`
  - `CommonSecurityLog.DeviceVendor =~ "CrowdStrike"`
  - `_Computed.DeviceCustomDate1Label in "DNS Request Time,DocAccessTimestamp,Document Accessed Timestamp,ExeWrittenTimestamp,Network Access Timestamp"`
  - `_Computed.DeviceCustomDate2Label in "HashSpreadingEventTime,HashSpreadingSensorEventTime"`
  - `_Computed.DeviceCustomNumber2Label == "ProcessId"`
  - `_Computed.DeviceCustomNumber3Label == "Offset"`
  - `_Computed.DeviceCustomString2Label in "AccessedDocFileName,QuarantineFileSHA256,ScanResultEngine,WrittenExeFileName"`
  - `_Computed.DeviceCustomString3Label in "AccessedDocFilePath,QuarantineFilePath,WrittenExeFilePath"`
  - `_Computed.DeviceCustomString4Label == "ScanResultVersion"`
  - `_Computed.DeviceCustomString5Label == "CommandLine"`
  - `_Computed.DeviceCustomString6Label == "FalconHostLink"`
  - `_Computed.LogSeverity in "1,2,3,4,5"`

#### parser: [`ASimNetworkSessionFortinetFortiGate`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionfortinetfortigate.md>) ↔ [`Fortinet`](<../../../sentinelninja/Solutions Docs/connectors/fortinet.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.EventResult == "Success"`
  - `_Computed._UtmAction == "allow"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`

#### parser: [`ASimNetworkSessionFortinetFortiGate`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionfortinetfortigate.md>) ↔ [`FortinetAma`](<../../../sentinelninja/Solutions Docs/connectors/fortinetama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.EventResult == "Success"`
  - `_Computed._UtmAction == "allow"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "Fortigate"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`

#### parser: [`ASimNetworkSessionNative`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionnative.md>) ↔ [`SynqlyIntegrationConnector`](<../../../sentinelninja/Solutions Docs/connectors/synqlyintegrationconnector.md>)

- **Shared tables:** asimnetworksessionlogs
- **Target predicates:**
  - `ASimNetworkSessionLogs.EventType in "EndpointNetworkSession,L2NetworkSession"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimNetworkSessionPaloAltoCortexDataLake`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionpaloaltocortexdatalake.md>) ↔ [`PaloAltoCDL`](<../../../sentinelninja/Solutions Docs/connectors/paloaltocdl.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "TRAFFIC"`
  - `CommonSecurityLog.DeviceProduct == "LF"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.DstIpAddr contains "."`
  - `_Computed.DstIpAddr contains ":"`
  - `_Computed.PanOSIsClienttoServer == "true"`
  - `_Computed.PanOSIsSaaSApplication in "false,true"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "LF"`
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
  - `_Computed.DeviceCustomIPv6Address2Label == "Source IPv6 Address"`
  - `_Computed.DeviceCustomIPv6Address3Label == "Destination IPv6 Address"`
  - `_Computed.DeviceCustomNumber1Label == "SessionID"`
  - `_Computed.DeviceCustomNumber2Label == "PacketsTotal"`
  - `_Computed.DeviceCustomNumber3Label == "SessionDuration"`
  - `_Computed.DeviceCustomString4Label == "FromZone"`
  - `_Computed.DeviceCustomString5Label == "Zone"`

#### parser: [`ASimNetworkSessionPaloAltoCortexDataLake`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionpaloaltocortexdatalake.md>) ↔ [`PaloAltoCDLAma`](<../../../sentinelninja/Solutions Docs/connectors/paloaltocdlama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "TRAFFIC"`
  - `CommonSecurityLog.DeviceProduct == "LF"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.DstIpAddr contains "."`
  - `_Computed.DstIpAddr contains ":"`
  - `_Computed.PanOSIsClienttoServer == "true"`
  - `_Computed.PanOSIsSaaSApplication in "false,true"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "LF"`
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
  - `_Computed.DeviceCustomIPv6Address2Label == "Source IPv6 Address"`
  - `_Computed.DeviceCustomIPv6Address3Label == "Destination IPv6 Address"`
  - `_Computed.DeviceCustomNumber1Label == "SessionID"`
  - `_Computed.DeviceCustomNumber2Label == "PacketsTotal"`
  - `_Computed.DeviceCustomNumber3Label == "SessionDuration"`
  - `_Computed.DeviceCustomString4Label == "FromZone"`
  - `_Computed.DeviceCustomString5Label == "Zone"`

#### parser: [`ASimNetworkSessionZscalerZIA`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionzscalerzia.md>) ↔ [`CloudNSSFWLogs_ccp`](<../../../sentinelninja/Solutions Docs/connectors/cloudnssfwlogs-ccp.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct == "NSSFWlog"`
  - `CommonSecurityLog.DeviceVendor == "Zscaler"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct == "NSSFWlog"`

#### parser: [`ASimProcessEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimprocesseventnative.md>) ↔ [`SynqlyIntegrationConnector`](<../../../sentinelninja/Solutions Docs/connectors/synqlyintegrationconnector.md>)

- **Shared tables:** asimprocesseventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimRegistryEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimregistryeventnative.md>) ↔ [`SynqlyIntegrationConnector`](<../../../sentinelninja/Solutions Docs/connectors/synqlyintegrationconnector.md>)

- **Shared tables:** asimregistryeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimUserManagementAWSCloudTrail`](<../../../sentinelninja/Solutions Docs/asim/asimusermanagementawscloudtrail.md>) ↔ [`AWS`](<../../../sentinelninja/Solutions Docs/connectors/aws.md>)

- **Shared tables:** awscloudtrail
- **Target predicates:**
  - `AWSCloudTrail.EventSource in "cognito-idp.amazonaws.com,iam.amazonaws.com"`
  - `_Computed.TargetUserId startswith "AIDA"`
  - `_Computed.TargetUserId startswith "AROA"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimUserManagementNative`](<../../../sentinelninja/Solutions Docs/asim/asimusermanagementnative.md>) ↔ [`SynqlyIntegrationConnector`](<../../../sentinelninja/Solutions Docs/connectors/synqlyintegrationconnector.md>)

- **Shared tables:** asimusermanagementactivitylogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimWebSessionApacheHTTPServer`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionapachehttpserver.md>) ↔ [`ApacheHTTPServer`](<../../../sentinelninja/Solutions Docs/connectors/apachehttpserver.md>)

- **Shared tables:** apachehttpserver_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimWebSessionBarracudaCEF`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionbarracudacef.md>) ↔ [`Barracuda`](<../../../sentinelninja/Solutions Docs/connectors/barracuda.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct in "WAAS,WAF"`
  - `CommonSecurityLog.DeviceVendor startswith "Barracuda"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceVendor == "Barracuda"`

#### parser: [`ASimWebSessionCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionciscomeraki.md>) ↔ [`CiscoUCS`](<../../../sentinelninja/Solutions Docs/connectors/ciscoucs.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `_Computed.Dst has "."`
  - `_Computed.DvcAction in "Allow,Deny"`
  - `_Computed.LogType == "urls"`
  - `_Computed.disposition == "malicious"`
  - `_Computed.src has "."`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimWebSessionCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionciscomeraki.md>) ↔ [`CitrixADC`](<../../../sentinelninja/Solutions Docs/connectors/citrixadc.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `_Computed.Dst has "."`
  - `_Computed.DvcAction in "Allow,Deny"`
  - `_Computed.LogType == "urls"`
  - `_Computed.disposition == "malicious"`
  - `_Computed.src has "."`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimWebSessionCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionciscomeraki.md>) ↔ [`RSASecurIDAM`](<../../../sentinelninja/Solutions Docs/connectors/rsasecuridam.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `_Computed.Dst has "."`
  - `_Computed.DvcAction in "Allow,Deny"`
  - `_Computed.LogType == "urls"`
  - `_Computed.disposition == "malicious"`
  - `_Computed.src has "."`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimWebSessionCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionciscomeraki.md>) ↔ [`WatchguardFirebox`](<../../../sentinelninja/Solutions Docs/connectors/watchguardfirebox.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `_Computed.Dst has "."`
  - `_Computed.DvcAction in "Allow,Deny"`
  - `_Computed.LogType == "urls"`
  - `_Computed.disposition == "malicious"`
  - `_Computed.src has "."`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimWebSessionCiscoUmbrella`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionciscoumbrella.md>) ↔ [`CiscoUmbrellaDataConnector`](<../../../sentinelninja/Solutions Docs/connectors/ciscoumbrelladataconnector.md>)

- **Shared tables:** cisco_umbrella_proxy_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimWebSessionCiscoUmbrella`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionciscoumbrella.md>) ↔ [`CiscoUmbrellaDataConnectorelasticpremium`](<../../../sentinelninja/Solutions Docs/connectors/ciscoumbrelladataconnectorelasticpremium.md>)

- **Shared tables:** cisco_umbrella_proxy_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimWebSessionF5ASM`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionf5asm.md>) ↔ [`F5`](<../../../sentinelninja/Solutions Docs/connectors/f5.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct == "ASM"`
  - `CommonSecurityLog.DeviceVendor == "F5"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceVendor == "F5"`

#### parser: [`ASimWebSessionF5ASM`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionf5asm.md>) ↔ [`F5Ama`](<../../../sentinelninja/Solutions Docs/connectors/f5ama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct == "ASM"`
  - `CommonSecurityLog.DeviceVendor == "F5"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "F5"`

#### parser: [`ASimWebSessionFortinetFortiGate`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionfortinetfortigate.md>) ↔ [`Fortinet`](<../../../sentinelninja/Solutions Docs/connectors/fortinet.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.direction in "incoming,outgoing"`
  - `_Computed.severity in "high,info,low,medium"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`

#### parser: [`ASimWebSessionFortinetFortiGate`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionfortinetfortigate.md>) ↔ [`FortinetAma`](<../../../sentinelninja/Solutions Docs/connectors/fortinetama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
  - `_Computed.direction in "incoming,outgoing"`
  - `_Computed.severity in "high,info,low,medium"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "Fortigate"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`

#### parser: [`ASimWebSessionNative`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionnative.md>) ↔ [`SynqlyIntegrationConnector`](<../../../sentinelninja/Solutions Docs/connectors/synqlyintegrationconnector.md>)

- **Shared tables:** asimwebsessionlogs
- **Target predicates:**
  - `ASimWebSessionLogs.EventType in "EndpointNetworkSession,HTTPSession"`
- **Connector predicates:**
  - *(empty)*

#### parser: [`ASimWebSessionPaloAltoCEF`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionpaloaltocef.md>) ↔ [`PaloAltoNetworks`](<../../../sentinelninja/Solutions Docs/connectors/paloaltonetworks.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.Activity == "THREAT"`
  - `CommonSecurityLog.DeviceEventClassID == "url"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.FlexString2 in "client-to-server,server-to-client"`
  - `_Computed.NetworkDirection in "Inbound,Outbound"`
  - `_Computed.ThreatField in "DstIpAddr,SrcIpAddr"`
- **Connector predicates:**
  - `CommonSecurityLog.Activity == "THREAT"`
  - `CommonSecurityLog.DeviceProduct has "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`

#### parser: [`ASimWebSessionPaloAltoCEF`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionpaloaltocef.md>) ↔ [`PaloAltoNetworksAma`](<../../../sentinelninja/Solutions Docs/connectors/paloaltonetworksama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.Activity == "THREAT"`
  - `CommonSecurityLog.DeviceEventClassID == "url"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.FlexString2 in "client-to-server,server-to-client"`
  - `_Computed.NetworkDirection in "Inbound,Outbound"`
  - `_Computed.ThreatField in "DstIpAddr,SrcIpAddr"`
- **Connector predicates:**
  - `CommonSecurityLog.Activity == "THREAT"`
  - `CommonSecurityLog.DeviceProduct =~ "PAN-OS"`
  - `CommonSecurityLog.DeviceProduct has "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`

#### parser: [`ASimWebSessionPaloAltoCortexDataLake`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionpaloaltocortexdatalake.md>) ↔ [`PaloAltoCDL`](<../../../sentinelninja/Solutions Docs/connectors/paloaltocdl.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "THREAT"`
  - `CommonSecurityLog.DeviceProduct == "LF"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.DstIpAddr contains "."`
  - `_Computed.DstIpAddr contains ":"`
  - `_Computed.PanOSIsClienttoServer == "true"`
  - `_Computed.PanOSIsSaaSApplication in "false,true"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "LF"`
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
  - `_Computed.DeviceCustomIPv6Address2Label == "Source IPv6 Address"`
  - `_Computed.DeviceCustomIPv6Address3Label == "Destination IPv6 Address"`
  - `_Computed.DeviceCustomNumber1Label == "SessionID"`
  - `_Computed.DeviceCustomNumber2Label == "PacketsTotal"`
  - `_Computed.DeviceCustomNumber3Label == "SessionDuration"`
  - `_Computed.DeviceCustomString4Label == "FromZone"`
  - `_Computed.DeviceCustomString5Label == "Zone"`

#### parser: [`ASimWebSessionPaloAltoCortexDataLake`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionpaloaltocortexdatalake.md>) ↔ [`PaloAltoCDLAma`](<../../../sentinelninja/Solutions Docs/connectors/paloaltocdlama.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID == "THREAT"`
  - `CommonSecurityLog.DeviceProduct == "LF"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
  - `_Computed.DstIpAddr contains "."`
  - `_Computed.DstIpAddr contains ":"`
  - `_Computed.PanOSIsClienttoServer == "true"`
  - `_Computed.PanOSIsSaaSApplication in "false,true"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "LF"`
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
  - `_Computed.DeviceCustomIPv6Address2Label == "Source IPv6 Address"`
  - `_Computed.DeviceCustomIPv6Address3Label == "Destination IPv6 Address"`
  - `_Computed.DeviceCustomNumber1Label == "SessionID"`
  - `_Computed.DeviceCustomNumber2Label == "PacketsTotal"`
  - `_Computed.DeviceCustomNumber3Label == "SessionDuration"`
  - `_Computed.DeviceCustomString4Label == "FromZone"`
  - `_Computed.DeviceCustomString5Label == "Zone"`

## ASIM — Removed associations

#### parser: [`ASimAuditEventCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimauditeventciscomeraki.md>) ↔ [`CiscoMeraki(usingRESTAPI)`](<../../../sentinelninja/Solutions Docs/connectors/ciscomeraki-usingrestapi.md>)

- **Shared tables:** meraki_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### parser: [`ASimAuditEventCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimauditeventciscomeraki.md>) ↔ [`CiscoMerakiNativePoller`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakinativepoller.md>)

- **Shared tables:** meraki_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### parser: [`ASimAuditEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimauditeventnative.md>) ↔ [`CiscoMerakiMultiRule`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakimultirule.md>)

- **Shared tables:** asimauditeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimAuditEventLogs.EventProduct == "Meraki"`
  - `ASimAuditEventLogs.EventVendor == "Cisco"`

#### parser: [`ASimAuditEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimauditeventnative.md>) ↔ [`CrowdstrikeReplicatorv2`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikereplicatorv2.md>)

- **Shared tables:** asimauditeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimUserManagementLogs_CL.EventProduct == "Falcon Data Replicator"`
  - `ASimUserManagementLogs_CL.EventVendor == "CrowdStrike"`

#### parser: [`ASimAuditEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimauditeventnative.md>) ↔ [`WorkdayCCPDefinition`](<../../../sentinelninja/Solutions Docs/connectors/workdayccpdefinition.md>)

- **Shared tables:** asimauditeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimAuditEventLogs.EventProduct == "Workday"`

#### parser: [`ASimAuthenticationCiscoASA`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationciscoasa.md>) ↔ [`CiscoASA`](<../../../sentinelninja/Solutions Docs/connectors/ciscoasa.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct == "ASA"`
  - `CommonSecurityLog.DeviceVendor =~ "Cisco"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct == "ASA"`
  - `CommonSecurityLog.DeviceVendor =~ "Cisco"`
  - `CommonSecurityLog.SimplifiedDeviceAction == "Deny"`

#### parser: [`ASimAuthenticationCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationciscomeraki.md>) ↔ [`CiscoMeraki(usingRESTAPI)`](<../../../sentinelninja/Solutions Docs/connectors/ciscomeraki-usingrestapi.md>)

- **Shared tables:** meraki_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### parser: [`ASimAuthenticationCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationciscomeraki.md>) ↔ [`CiscoMerakiNativePoller`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakinativepoller.md>)

- **Shared tables:** meraki_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### parser: [`ASimAuthenticationNative`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationnative.md>) ↔ [`CrowdstrikeReplicatorv2`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikereplicatorv2.md>)

- **Shared tables:** asimauthenticationeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimUserManagementLogs_CL.EventProduct == "Falcon Data Replicator"`
  - `ASimUserManagementLogs_CL.EventVendor == "CrowdStrike"`

#### parser: [`ASimAuthenticationNative`](<../../../sentinelninja/Solutions Docs/asim/asimauthenticationnative.md>) ↔ [`carbonBlackAWSS3`](<../../../sentinelninja/Solutions Docs/connectors/carbonblackawss3.md>)

- **Shared tables:** asimauthenticationeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimAuthenticationEventLogs.EventProduct == "Carbon Black Cloud"`
  - `ASimAuthenticationEventLogs.EventVendor == "VMWare"`

#### parser: [`ASimDnsMicrosoftNXlog`](<../../../sentinelninja/Solutions Docs/asim/asimdnsmicrosoftnxlog.md>) ↔ [`NXLogDNSLogs`](<../../../sentinelninja/Solutions Docs/connectors/nxlogdnslogs.md>)

- **Shared tables:** nxlog_dns_server_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.DnsResponseCode == "0"`
  - `_Computed.EventResult == "Based on RCODE"`
  - `_Computed.TCP_s == "0"`

#### parser: [`ASimDnsNative`](<../../../sentinelninja/Solutions Docs/asim/asimdnsnative.md>) ↔ [`CrowdstrikeReplicatorv2`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikereplicatorv2.md>)

- **Shared tables:** asimdnsactivitylogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimUserManagementLogs_CL.EventProduct == "Falcon Data Replicator"`
  - `ASimUserManagementLogs_CL.EventVendor == "CrowdStrike"`

#### parser: [`ASimFileEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimfileeventnative.md>) ↔ [`CrowdstrikeReplicatorv2`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikereplicatorv2.md>)

- **Shared tables:** asimfileeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimUserManagementLogs_CL.EventProduct == "Falcon Data Replicator"`
  - `ASimUserManagementLogs_CL.EventVendor == "CrowdStrike"`

#### parser: [`ASimFileEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimfileeventnative.md>) ↔ [`carbonBlackAWSS3`](<../../../sentinelninja/Solutions Docs/connectors/carbonblackawss3.md>)

- **Shared tables:** asimfileeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimAuthenticationEventLogs.EventProduct == "Carbon Black Cloud"`
  - `ASimAuthenticationEventLogs.EventVendor == "VMWare"`

#### parser: [`ASimNetworkSessionCiscoASA`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionciscoasa.md>) ↔ [`CiscoASA`](<../../../sentinelninja/Solutions Docs/connectors/ciscoasa.md>)

- **Shared tables:** commonsecuritylog
- **Target predicates:**
  - `CommonSecurityLog.DeviceEventClassID in "106001,106002,106006,106007,106010,106012,106013,106014,106015,106016,106017,106018,106020,106021,106022,106023,106100,302013,302014,302015,302016,302020,302021,710002,710003,710004,710005"`
  - `CommonSecurityLog.DeviceProduct == "ASA"`
  - `CommonSecurityLog.DeviceVendor == "Cisco"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct == "ASA"`
  - `CommonSecurityLog.DeviceVendor =~ "Cisco"`
  - `CommonSecurityLog.SimplifiedDeviceAction == "Deny"`

#### parser: [`ASimNetworkSessionCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionciscomeraki.md>) ↔ [`CiscoMeraki(usingRESTAPI)`](<../../../sentinelninja/Solutions Docs/connectors/ciscomeraki-usingrestapi.md>)

- **Shared tables:** meraki_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### parser: [`ASimNetworkSessionCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionciscomeraki.md>) ↔ [`CiscoMerakiNativePoller`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakinativepoller.md>)

- **Shared tables:** meraki_cl
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### parser: [`ASimNetworkSessionNative`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionnative.md>) ↔ [`CiscoMerakiMultiRule`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakimultirule.md>)

- **Shared tables:** asimnetworksessionlogs
- **Target predicates:**
  - `ASimNetworkSessionLogs.EventType in "EndpointNetworkSession,L2NetworkSession"`
- **Connector predicates:**
  - `ASimAuditEventLogs.EventProduct == "Meraki"`
  - `ASimAuditEventLogs.EventVendor == "Cisco"`

#### parser: [`ASimNetworkSessionNative`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionnative.md>) ↔ [`CrowdstrikeReplicatorv2`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikereplicatorv2.md>)

- **Shared tables:** asimnetworksessionlogs
- **Target predicates:**
  - `ASimNetworkSessionLogs.EventType in "EndpointNetworkSession,L2NetworkSession"`
- **Connector predicates:**
  - `ASimUserManagementLogs_CL.EventProduct == "Falcon Data Replicator"`
  - `ASimUserManagementLogs_CL.EventVendor == "CrowdStrike"`

#### parser: [`ASimNetworkSessionNative`](<../../../sentinelninja/Solutions Docs/asim/asimnetworksessionnative.md>) ↔ [`carbonBlackAWSS3`](<../../../sentinelninja/Solutions Docs/connectors/carbonblackawss3.md>)

- **Shared tables:** asimnetworksessionlogs
- **Target predicates:**
  - `ASimNetworkSessionLogs.EventType in "EndpointNetworkSession,L2NetworkSession"`
- **Connector predicates:**
  - `ASimAuthenticationEventLogs.EventProduct == "Carbon Black Cloud"`
  - `ASimAuthenticationEventLogs.EventVendor == "VMWare"`

#### parser: [`ASimProcessEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimprocesseventnative.md>) ↔ [`CrowdstrikeReplicatorv2`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikereplicatorv2.md>)

- **Shared tables:** asimprocesseventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimUserManagementLogs_CL.EventProduct == "Falcon Data Replicator"`
  - `ASimUserManagementLogs_CL.EventVendor == "CrowdStrike"`

#### parser: [`ASimProcessEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimprocesseventnative.md>) ↔ [`carbonBlackAWSS3`](<../../../sentinelninja/Solutions Docs/connectors/carbonblackawss3.md>)

- **Shared tables:** asimprocesseventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimAuthenticationEventLogs.EventProduct == "Carbon Black Cloud"`
  - `ASimAuthenticationEventLogs.EventVendor == "VMWare"`

#### parser: [`ASimRegistryEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimregistryeventnative.md>) ↔ [`CrowdstrikeReplicatorv2`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikereplicatorv2.md>)

- **Shared tables:** asimregistryeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimUserManagementLogs_CL.EventProduct == "Falcon Data Replicator"`
  - `ASimUserManagementLogs_CL.EventVendor == "CrowdStrike"`

#### parser: [`ASimRegistryEventNative`](<../../../sentinelninja/Solutions Docs/asim/asimregistryeventnative.md>) ↔ [`carbonBlackAWSS3`](<../../../sentinelninja/Solutions Docs/connectors/carbonblackawss3.md>)

- **Shared tables:** asimregistryeventlogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimAuthenticationEventLogs.EventProduct == "Carbon Black Cloud"`
  - `ASimAuthenticationEventLogs.EventVendor == "VMWare"`

#### parser: [`ASimUserManagementNative`](<../../../sentinelninja/Solutions Docs/asim/asimusermanagementnative.md>) ↔ [`CrowdstrikeReplicatorv2`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikereplicatorv2.md>)

- **Shared tables:** asimusermanagementactivitylogs
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ASimUserManagementLogs_CL.EventProduct == "Falcon Data Replicator"`
  - `ASimUserManagementLogs_CL.EventVendor == "CrowdStrike"`

#### parser: [`ASimWebSessionCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionciscomeraki.md>) ↔ [`CiscoMeraki(usingRESTAPI)`](<../../../sentinelninja/Solutions Docs/connectors/ciscomeraki-usingrestapi.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### parser: [`ASimWebSessionCiscoMeraki`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionciscomeraki.md>) ↔ [`CiscoMerakiNativePoller`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakinativepoller.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### parser: [`ASimWebSessionNative`](<../../../sentinelninja/Solutions Docs/asim/asimwebsessionnative.md>) ↔ [`CiscoMerakiMultiRule`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakimultirule.md>)

- **Shared tables:** asimwebsessionlogs
- **Target predicates:**
  - `ASimWebSessionLogs.EventType in "EndpointNetworkSession,HTTPSession"`
- **Connector predicates:**
  - `ASimAuditEventLogs.EventProduct == "Meraki"`
  - `ASimAuditEventLogs.EventVendor == "Cisco"`

## Content items

- Items with at least one association: **before 225, after 212**
- (item, connector) pairs: **before 752, after 500** (delta -252)

## Content — Added associations

#### item: [`042f2801-a375-4cfd-bd29-041fc7ed88a0`](<../../../sentinelninja/Solutions Docs/content/standalone-content-042f2801-a375-4cfd-bd29-041fc7ed88a0-9e43e164.md>) ↔ [`Fortinet`](<../../../sentinelninja/Solutions Docs/connectors/fortinet.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceAction != "Block"`
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
  - `SigninLogs.ResultType == "0"`
  - `SigninLogs.RiskState == "atRisk"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`

#### item: [`042f2801-a375-4cfd-bd29-041fc7ed88a0`](<../../../sentinelninja/Solutions Docs/content/standalone-content-042f2801-a375-4cfd-bd29-041fc7ed88a0-9e43e164.md>) ↔ [`FortinetAma`](<../../../sentinelninja/Solutions Docs/connectors/fortinetama.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceAction != "Block"`
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
  - `SigninLogs.ResultType == "0"`
  - `SigninLogs.RiskState == "atRisk"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "Fortigate"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`

#### item: [`0b9ae89d-8cad-461c-808f-0494f70ad5c4`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b9ae89d-8cad-461c-808f-0494f70ad5c4-66de3be5.md>) ↔ [`CiscoUCS`](<../../../sentinelninja/Solutions Docs/connectors/ciscoucs.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `OfficeActivity.OfficeWorkload == "AzureActiveDirectory"`
  - `Syslog.Facility in "auth,authpriv"`
  - `Syslog.SyslogMessage matchesregex ".*password changed for.*"`
  - `WindowsEvent.EventID in "4723,4724"`
- **Connector predicates:**
  - *(empty)*

#### item: [`0b9ae89d-8cad-461c-808f-0494f70ad5c4`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b9ae89d-8cad-461c-808f-0494f70ad5c4-66de3be5.md>) ↔ [`CitrixADC`](<../../../sentinelninja/Solutions Docs/connectors/citrixadc.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `OfficeActivity.OfficeWorkload == "AzureActiveDirectory"`
  - `Syslog.Facility in "auth,authpriv"`
  - `Syslog.SyslogMessage matchesregex ".*password changed for.*"`
  - `WindowsEvent.EventID in "4723,4724"`
- **Connector predicates:**
  - *(empty)*

#### item: [`0b9ae89d-8cad-461c-808f-0494f70ad5c4`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b9ae89d-8cad-461c-808f-0494f70ad5c4-66de3be5.md>) ↔ [`RSASecurIDAM`](<../../../sentinelninja/Solutions Docs/connectors/rsasecuridam.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `OfficeActivity.OfficeWorkload == "AzureActiveDirectory"`
  - `Syslog.Facility in "auth,authpriv"`
  - `Syslog.SyslogMessage matchesregex ".*password changed for.*"`
  - `WindowsEvent.EventID in "4723,4724"`
- **Connector predicates:**
  - *(empty)*

#### item: [`0b9ae89d-8cad-461c-808f-0494f70ad5c4`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b9ae89d-8cad-461c-808f-0494f70ad5c4-66de3be5.md>) ↔ [`WatchguardFirebox`](<../../../sentinelninja/Solutions Docs/connectors/watchguardfirebox.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `OfficeActivity.OfficeWorkload == "AzureActiveDirectory"`
  - `Syslog.Facility in "auth,authpriv"`
  - `Syslog.SyslogMessage matchesregex ".*password changed for.*"`
  - `WindowsEvent.EventID in "4723,4724"`
- **Connector predicates:**
  - *(empty)*

#### item: [`1ccf0f4e-4f5d-4a46-819b-5ba857394f2a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1ccf0f4e-4f5d-4a46-819b-5ba857394f2a-96cd3aad.md>) ↔ [`PaloAltoNetworks`](<../../../sentinelninja/Solutions Docs/connectors/paloaltonetworks.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.Activity == "THREAT"`
  - `CommonSecurityLog.DeviceEventClassID == "url"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
- **Connector predicates:**
  - `CommonSecurityLog.Activity == "THREAT"`
  - `CommonSecurityLog.DeviceProduct has "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`

#### item: [`1ccf0f4e-4f5d-4a46-819b-5ba857394f2a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1ccf0f4e-4f5d-4a46-819b-5ba857394f2a-96cd3aad.md>) ↔ [`PaloAltoNetworksAma`](<../../../sentinelninja/Solutions Docs/connectors/paloaltonetworksama.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.Activity == "THREAT"`
  - `CommonSecurityLog.DeviceEventClassID == "url"`
  - `CommonSecurityLog.DeviceProduct == "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor == "Palo Alto Networks"`
- **Connector predicates:**
  - `CommonSecurityLog.Activity == "THREAT"`
  - `CommonSecurityLog.DeviceProduct =~ "PAN-OS"`
  - `CommonSecurityLog.DeviceProduct has "PAN-OS"`
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`

#### item: [`1ce5e766-26ab-4616-b7c8-3b33ae321e80`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1ce5e766-26ab-4616-b7c8-3b33ae321e80-abcb91b6.md>) ↔ [`CiscoUCS`](<../../../sentinelninja/Solutions Docs/connectors/ciscoucs.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "from"`
  - `Syslog.SyslogMessage has_any "Accepted,Disconnected,Disconnecting,[preauth],disconnect"`
  - `WindowsEvent.EventID == "4625"`
- **Connector predicates:**
  - *(empty)*

#### item: [`1ce5e766-26ab-4616-b7c8-3b33ae321e80`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1ce5e766-26ab-4616-b7c8-3b33ae321e80-abcb91b6.md>) ↔ [`CitrixADC`](<../../../sentinelninja/Solutions Docs/connectors/citrixadc.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "from"`
  - `Syslog.SyslogMessage has_any "Accepted,Disconnected,Disconnecting,[preauth],disconnect"`
  - `WindowsEvent.EventID == "4625"`
- **Connector predicates:**
  - *(empty)*

#### item: [`1ce5e766-26ab-4616-b7c8-3b33ae321e80`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1ce5e766-26ab-4616-b7c8-3b33ae321e80-abcb91b6.md>) ↔ [`RSASecurIDAM`](<../../../sentinelninja/Solutions Docs/connectors/rsasecuridam.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "from"`
  - `Syslog.SyslogMessage has_any "Accepted,Disconnected,Disconnecting,[preauth],disconnect"`
  - `WindowsEvent.EventID == "4625"`
- **Connector predicates:**
  - *(empty)*

#### item: [`1ce5e766-26ab-4616-b7c8-3b33ae321e80`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1ce5e766-26ab-4616-b7c8-3b33ae321e80-abcb91b6.md>) ↔ [`WatchguardFirebox`](<../../../sentinelninja/Solutions Docs/connectors/watchguardfirebox.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "from"`
  - `Syslog.SyslogMessage has_any "Accepted,Disconnected,Disconnecting,[preauth],disconnect"`
  - `WindowsEvent.EventID == "4625"`
- **Connector predicates:**
  - *(empty)*

#### item: [`2fed0668-6d43-4c78-87e6-510f96f12145`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2fed0668-6d43-4c78-87e6-510f96f12145-0e9ada26.md>) ↔ [`Fortinet`](<../../../sentinelninja/Solutions Docs/connectors/fortinet.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
  - `SecurityAlert.ProviderName in~ "OATP,Office 365 Advanced Threat Protection"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`

#### item: [`2fed0668-6d43-4c78-87e6-510f96f12145`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2fed0668-6d43-4c78-87e6-510f96f12145-0e9ada26.md>) ↔ [`FortinetAma`](<../../../sentinelninja/Solutions Docs/connectors/fortinetama.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
  - `SecurityAlert.ProviderName in~ "OATP,Office 365 Advanced Threat Protection"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "Fortigate"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`

#### item: [`3fdb3c31-d528-4b94-8268-918838cdaee8`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3fdb3c31-d528-4b94-8268-918838cdaee8-81670146.md>) ↔ [`Fortinet`](<../../../sentinelninja/Solutions Docs/connectors/fortinet.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.AdditionalExtensions has "cat=traffic"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`

#### item: [`3fdb3c31-d528-4b94-8268-918838cdaee8`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3fdb3c31-d528-4b94-8268-918838cdaee8-81670146.md>) ↔ [`FortinetAma`](<../../../sentinelninja/Solutions Docs/connectors/fortinetama.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.AdditionalExtensions has "cat=traffic"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "Fortigate"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`

#### item: [`6457ab65-69ea-4444-981d-1ecaf414fda7`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6457ab65-69ea-4444-981d-1ecaf414fda7-e5b81d56.md>) ↔ [`CloudNSSFWLogs_ccp`](<../../../sentinelninja/Solutions Docs/connectors/cloudnssfwlogs-ccp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct == "NSSFWlog"`
  - `CommonSecurityLog.DeviceVendor == "Zscaler"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct == "NSSFWlog"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`Fortinet`](<../../../sentinelninja/Solutions Docs/connectors/fortinet.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
  - `_Computed.Entities has "url"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`FortinetAma`](<../../../sentinelninja/Solutions Docs/connectors/fortinetama.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
  - `_Computed.Entities has "url"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "Fortigate"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`

#### item: [`8ee967a2-a645-4832-85f4-72b635bcb3a6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ee967a2-a645-4832-85f4-72b635bcb3a6-5072f9dd.md>) ↔ [`CiscoUCS`](<../../../sentinelninja/Solutions Docs/connectors/ciscoucs.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "Accepted"`
- **Connector predicates:**
  - *(empty)*

#### item: [`8ee967a2-a645-4832-85f4-72b635bcb3a6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ee967a2-a645-4832-85f4-72b635bcb3a6-5072f9dd.md>) ↔ [`CitrixADC`](<../../../sentinelninja/Solutions Docs/connectors/citrixadc.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "Accepted"`
- **Connector predicates:**
  - *(empty)*

#### item: [`8ee967a2-a645-4832-85f4-72b635bcb3a6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ee967a2-a645-4832-85f4-72b635bcb3a6-5072f9dd.md>) ↔ [`RSASecurIDAM`](<../../../sentinelninja/Solutions Docs/connectors/rsasecuridam.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "Accepted"`
- **Connector predicates:**
  - *(empty)*

#### item: [`8ee967a2-a645-4832-85f4-72b635bcb3a6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ee967a2-a645-4832-85f4-72b635bcb3a6-5072f9dd.md>) ↔ [`WatchguardFirebox`](<../../../sentinelninja/Solutions Docs/connectors/watchguardfirebox.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "Accepted"`
- **Connector predicates:**
  - *(empty)*

#### item: [`959fe0f0-7ac0-467c-944f-5b8c6fdc9e72`](<../../../sentinelninja/Solutions Docs/content/standalone-content-959fe0f0-7ac0-467c-944f-5b8c6fdc9e72-56e135bf.md>) ↔ [`CiscoUCS`](<../../../sentinelninja/Solutions Docs/connectors/ciscoucs.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.ProcessName contains "squid"`
- **Connector predicates:**
  - *(empty)*

#### item: [`959fe0f0-7ac0-467c-944f-5b8c6fdc9e72`](<../../../sentinelninja/Solutions Docs/content/standalone-content-959fe0f0-7ac0-467c-944f-5b8c6fdc9e72-56e135bf.md>) ↔ [`CitrixADC`](<../../../sentinelninja/Solutions Docs/connectors/citrixadc.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.ProcessName contains "squid"`
- **Connector predicates:**
  - *(empty)*

#### item: [`959fe0f0-7ac0-467c-944f-5b8c6fdc9e72`](<../../../sentinelninja/Solutions Docs/content/standalone-content-959fe0f0-7ac0-467c-944f-5b8c6fdc9e72-56e135bf.md>) ↔ [`RSASecurIDAM`](<../../../sentinelninja/Solutions Docs/connectors/rsasecuridam.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.ProcessName contains "squid"`
- **Connector predicates:**
  - *(empty)*

#### item: [`959fe0f0-7ac0-467c-944f-5b8c6fdc9e72`](<../../../sentinelninja/Solutions Docs/content/standalone-content-959fe0f0-7ac0-467c-944f-5b8c6fdc9e72-56e135bf.md>) ↔ [`WatchguardFirebox`](<../../../sentinelninja/Solutions Docs/connectors/watchguardfirebox.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.ProcessName contains "squid"`
- **Connector predicates:**
  - *(empty)*

#### item: [`9862489b-230a-4b70-b45a-8a2771360a86`](<../../../sentinelninja/Solutions Docs/content/standalone-content-9862489b-230a-4b70-b45a-8a2771360a86-4b311a48.md>) ↔ [`Fortinet`](<../../../sentinelninja/Solutions Docs/connectors/fortinet.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.Activity has_all "webfilter"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`

#### item: [`9862489b-230a-4b70-b45a-8a2771360a86`](<../../../sentinelninja/Solutions Docs/content/standalone-content-9862489b-230a-4b70-b45a-8a2771360a86-4b311a48.md>) ↔ [`FortinetAma`](<../../../sentinelninja/Solutions Docs/connectors/fortinetama.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.Activity has_all "webfilter"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor == "Fortinet"`
- **Connector predicates:**
  - `CommonSecurityLog.DeviceProduct =~ "Fortigate"`
  - `CommonSecurityLog.DeviceProduct startswith "Fortigate"`
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`

#### item: [`bac44fe4-c0bc-4e90-aa48-2e346fda803f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bac44fe4-c0bc-4e90-aa48-2e346fda803f-cd84615c.md>) ↔ [`CiscoUCS`](<../../../sentinelninja/Solutions Docs/connectors/ciscoucs.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### item: [`bac44fe4-c0bc-4e90-aa48-2e346fda803f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bac44fe4-c0bc-4e90-aa48-2e346fda803f-cd84615c.md>) ↔ [`CitrixADC`](<../../../sentinelninja/Solutions Docs/connectors/citrixadc.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### item: [`bac44fe4-c0bc-4e90-aa48-2e346fda803f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bac44fe4-c0bc-4e90-aa48-2e346fda803f-cd84615c.md>) ↔ [`RSASecurIDAM`](<../../../sentinelninja/Solutions Docs/connectors/rsasecuridam.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### item: [`bac44fe4-c0bc-4e90-aa48-2e346fda803f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bac44fe4-c0bc-4e90-aa48-2e346fda803f-cd84615c.md>) ↔ [`WatchguardFirebox`](<../../../sentinelninja/Solutions Docs/connectors/watchguardfirebox.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

## Content — Removed associations

#### item: [`0b520385-6a16-4e6f-ba89-c320d857695f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b520385-6a16-4e6f-ba89-c320d857695f-73453df3.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`0b520385-6a16-4e6f-ba89-c320d857695f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b520385-6a16-4e6f-ba89-c320d857695f-73453df3.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`0b520385-6a16-4e6f-ba89-c320d857695f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b520385-6a16-4e6f-ba89-c320d857695f-73453df3.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`0b520385-6a16-4e6f-ba89-c320d857695f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b520385-6a16-4e6f-ba89-c320d857695f-73453df3.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`0b520385-6a16-4e6f-ba89-c320d857695f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b520385-6a16-4e6f-ba89-c320d857695f-73453df3.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`0b520385-6a16-4e6f-ba89-c320d857695f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b520385-6a16-4e6f-ba89-c320d857695f-73453df3.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`0b520385-6a16-4e6f-ba89-c320d857695f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b520385-6a16-4e6f-ba89-c320d857695f-73453df3.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`0b520385-6a16-4e6f-ba89-c320d857695f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b520385-6a16-4e6f-ba89-c320d857695f-73453df3.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`0b520385-6a16-4e6f-ba89-c320d857695f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b520385-6a16-4e6f-ba89-c320d857695f-73453df3.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`0b9ae89d-8cad-461c-808f-0494f70ad5c4`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b9ae89d-8cad-461c-808f-0494f70ad5c4-66de3be5.md>) ↔ [`CiscoMeraki(usingRESTAPI)`](<../../../sentinelninja/Solutions Docs/connectors/ciscomeraki-usingrestapi.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `OfficeActivity.OfficeWorkload == "AzureActiveDirectory"`
  - `Syslog.Facility in "auth,authpriv"`
  - `Syslog.SyslogMessage matchesregex ".*password changed for.*"`
  - `WindowsEvent.EventID in "4723,4724"`
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### item: [`0b9ae89d-8cad-461c-808f-0494f70ad5c4`](<../../../sentinelninja/Solutions Docs/content/standalone-content-0b9ae89d-8cad-461c-808f-0494f70ad5c4-66de3be5.md>) ↔ [`CiscoMerakiNativePoller`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakinativepoller.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `OfficeActivity.OfficeWorkload == "AzureActiveDirectory"`
  - `Syslog.Facility in "auth,authpriv"`
  - `Syslog.SyslogMessage matchesregex ".*password changed for.*"`
  - `WindowsEvent.EventID in "4723,4724"`
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### item: [`11d808a1-32fe-4618-946a-cfd43523347a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-11d808a1-32fe-4618-946a-cfd43523347a-6e43d9d4.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`11d808a1-32fe-4618-946a-cfd43523347a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-11d808a1-32fe-4618-946a-cfd43523347a-6e43d9d4.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`11d808a1-32fe-4618-946a-cfd43523347a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-11d808a1-32fe-4618-946a-cfd43523347a-6e43d9d4.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`11d808a1-32fe-4618-946a-cfd43523347a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-11d808a1-32fe-4618-946a-cfd43523347a-6e43d9d4.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`11d808a1-32fe-4618-946a-cfd43523347a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-11d808a1-32fe-4618-946a-cfd43523347a-6e43d9d4.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`11d808a1-32fe-4618-946a-cfd43523347a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-11d808a1-32fe-4618-946a-cfd43523347a-6e43d9d4.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`11d808a1-32fe-4618-946a-cfd43523347a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-11d808a1-32fe-4618-946a-cfd43523347a-6e43d9d4.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`11d808a1-32fe-4618-946a-cfd43523347a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-11d808a1-32fe-4618-946a-cfd43523347a-6e43d9d4.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`11d808a1-32fe-4618-946a-cfd43523347a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-11d808a1-32fe-4618-946a-cfd43523347a-6e43d9d4.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`1399664f-9434-497c-9cde-42e4d74ae20e`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1399664f-9434-497c-9cde-42e4d74ae20e-492efe69.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`1399664f-9434-497c-9cde-42e4d74ae20e`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1399664f-9434-497c-9cde-42e4d74ae20e-492efe69.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`1399664f-9434-497c-9cde-42e4d74ae20e`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1399664f-9434-497c-9cde-42e4d74ae20e-492efe69.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`1399664f-9434-497c-9cde-42e4d74ae20e`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1399664f-9434-497c-9cde-42e4d74ae20e-492efe69.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`1399664f-9434-497c-9cde-42e4d74ae20e`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1399664f-9434-497c-9cde-42e4d74ae20e-492efe69.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`1399664f-9434-497c-9cde-42e4d74ae20e`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1399664f-9434-497c-9cde-42e4d74ae20e-492efe69.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`1399664f-9434-497c-9cde-42e4d74ae20e`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1399664f-9434-497c-9cde-42e4d74ae20e-492efe69.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`1399664f-9434-497c-9cde-42e4d74ae20e`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1399664f-9434-497c-9cde-42e4d74ae20e-492efe69.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`1399664f-9434-497c-9cde-42e4d74ae20e`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1399664f-9434-497c-9cde-42e4d74ae20e-492efe69.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`186970ee-5001-41c1-8c73-3178f75ce96a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-186970ee-5001-41c1-8c73-3178f75ce96a-995e02ca.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`186970ee-5001-41c1-8c73-3178f75ce96a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-186970ee-5001-41c1-8c73-3178f75ce96a-995e02ca.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`186970ee-5001-41c1-8c73-3178f75ce96a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-186970ee-5001-41c1-8c73-3178f75ce96a-995e02ca.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`186970ee-5001-41c1-8c73-3178f75ce96a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-186970ee-5001-41c1-8c73-3178f75ce96a-995e02ca.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`186970ee-5001-41c1-8c73-3178f75ce96a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-186970ee-5001-41c1-8c73-3178f75ce96a-995e02ca.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`186970ee-5001-41c1-8c73-3178f75ce96a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-186970ee-5001-41c1-8c73-3178f75ce96a-995e02ca.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`186970ee-5001-41c1-8c73-3178f75ce96a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-186970ee-5001-41c1-8c73-3178f75ce96a-995e02ca.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`186970ee-5001-41c1-8c73-3178f75ce96a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-186970ee-5001-41c1-8c73-3178f75ce96a-995e02ca.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`186970ee-5001-41c1-8c73-3178f75ce96a`](<../../../sentinelninja/Solutions Docs/content/standalone-content-186970ee-5001-41c1-8c73-3178f75ce96a-995e02ca.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`1cc0ba27-c5ca-411a-a779-fbc89e26be83`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1cc0ba27-c5ca-411a-a779-fbc89e26be83-22f3f318.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`1cc0ba27-c5ca-411a-a779-fbc89e26be83`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1cc0ba27-c5ca-411a-a779-fbc89e26be83-22f3f318.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`1cc0ba27-c5ca-411a-a779-fbc89e26be83`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1cc0ba27-c5ca-411a-a779-fbc89e26be83-22f3f318.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`1cc0ba27-c5ca-411a-a779-fbc89e26be83`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1cc0ba27-c5ca-411a-a779-fbc89e26be83-22f3f318.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`1cc0ba27-c5ca-411a-a779-fbc89e26be83`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1cc0ba27-c5ca-411a-a779-fbc89e26be83-22f3f318.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`1cc0ba27-c5ca-411a-a779-fbc89e26be83`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1cc0ba27-c5ca-411a-a779-fbc89e26be83-22f3f318.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`1cc0ba27-c5ca-411a-a779-fbc89e26be83`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1cc0ba27-c5ca-411a-a779-fbc89e26be83-22f3f318.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`1ce5e766-26ab-4616-b7c8-3b33ae321e80`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1ce5e766-26ab-4616-b7c8-3b33ae321e80-abcb91b6.md>) ↔ [`CiscoMeraki(usingRESTAPI)`](<../../../sentinelninja/Solutions Docs/connectors/ciscomeraki-usingrestapi.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "from"`
  - `Syslog.SyslogMessage has_any "Accepted,Disconnected,Disconnecting,[preauth],disconnect"`
  - `WindowsEvent.EventID == "4625"`
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### item: [`1ce5e766-26ab-4616-b7c8-3b33ae321e80`](<../../../sentinelninja/Solutions Docs/content/standalone-content-1ce5e766-26ab-4616-b7c8-3b33ae321e80-abcb91b6.md>) ↔ [`CiscoMerakiNativePoller`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakinativepoller.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "from"`
  - `Syslog.SyslogMessage has_any "Accepted,Disconnected,Disconnecting,[preauth],disconnect"`
  - `WindowsEvent.EventID == "4625"`
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### item: [`29a29e5d-354e-4f5e-8321-8b39d25047bf`](<../../../sentinelninja/Solutions Docs/content/standalone-content-29a29e5d-354e-4f5e-8321-8b39d25047bf-66ec9eb0.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`29a29e5d-354e-4f5e-8321-8b39d25047bf`](<../../../sentinelninja/Solutions Docs/content/standalone-content-29a29e5d-354e-4f5e-8321-8b39d25047bf-66ec9eb0.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`29a29e5d-354e-4f5e-8321-8b39d25047bf`](<../../../sentinelninja/Solutions Docs/content/standalone-content-29a29e5d-354e-4f5e-8321-8b39d25047bf-66ec9eb0.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`29a29e5d-354e-4f5e-8321-8b39d25047bf`](<../../../sentinelninja/Solutions Docs/content/standalone-content-29a29e5d-354e-4f5e-8321-8b39d25047bf-66ec9eb0.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`29a29e5d-354e-4f5e-8321-8b39d25047bf`](<../../../sentinelninja/Solutions Docs/content/standalone-content-29a29e5d-354e-4f5e-8321-8b39d25047bf-66ec9eb0.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`29a29e5d-354e-4f5e-8321-8b39d25047bf`](<../../../sentinelninja/Solutions Docs/content/standalone-content-29a29e5d-354e-4f5e-8321-8b39d25047bf-66ec9eb0.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`29a29e5d-354e-4f5e-8321-8b39d25047bf`](<../../../sentinelninja/Solutions Docs/content/standalone-content-29a29e5d-354e-4f5e-8321-8b39d25047bf-66ec9eb0.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`29a29e5d-354e-4f5e-8321-8b39d25047bf`](<../../../sentinelninja/Solutions Docs/content/standalone-content-29a29e5d-354e-4f5e-8321-8b39d25047bf-66ec9eb0.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`2e7cda70-c3cd-4173-945e-6b5c14b05817`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2e7cda70-c3cd-4173-945e-6b5c14b05817-49f2582b.md>) ↔ [`CrowdStrikeFalconAdversaryIntelligence`](<../../../sentinelninja/Solutions Docs/connectors/crowdstrikefalconadversaryintelligence.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ThreatIntelIndicators.SourceSystem == "CrowdStrike Falcon Adversary Intelligence"`

#### item: [`2e7cda70-c3cd-4173-945e-6b5c14b05817`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2e7cda70-c3cd-4173-945e-6b5c14b05817-49f2582b.md>) ↔ [`LumenThreatFeedConnector`](<../../../sentinelninja/Solutions Docs/connectors/lumenthreatfeedconnector.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - *(empty)*

#### item: [`2e7cda70-c3cd-4173-945e-6b5c14b05817`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2e7cda70-c3cd-4173-945e-6b5c14b05817-49f2582b.md>) ↔ [`ThreatIntelligence`](<../../../sentinelninja/Solutions Docs/connectors/threatintelligence.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `ThreatIntelligenceIndicator.ThreatType == "DDoS"`

#### item: [`2fed0668-6d43-4c78-87e6-510f96f12145`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2fed0668-6d43-4c78-87e6-510f96f12145-0e9ada26.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`2fed0668-6d43-4c78-87e6-510f96f12145`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2fed0668-6d43-4c78-87e6-510f96f12145-0e9ada26.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`2fed0668-6d43-4c78-87e6-510f96f12145`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2fed0668-6d43-4c78-87e6-510f96f12145-0e9ada26.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`2fed0668-6d43-4c78-87e6-510f96f12145`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2fed0668-6d43-4c78-87e6-510f96f12145-0e9ada26.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`2fed0668-6d43-4c78-87e6-510f96f12145`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2fed0668-6d43-4c78-87e6-510f96f12145-0e9ada26.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`2fed0668-6d43-4c78-87e6-510f96f12145`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2fed0668-6d43-4c78-87e6-510f96f12145-0e9ada26.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`2fed0668-6d43-4c78-87e6-510f96f12145`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2fed0668-6d43-4c78-87e6-510f96f12145-0e9ada26.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`2fed0668-6d43-4c78-87e6-510f96f12145`](<../../../sentinelninja/Solutions Docs/content/standalone-content-2fed0668-6d43-4c78-87e6-510f96f12145-0e9ada26.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`346d36c9-2e79-4d8f-8c14-1eef73d38737`](<../../../sentinelninja/Solutions Docs/content/standalone-content-346d36c9-2e79-4d8f-8c14-1eef73d38737-8e60a66e.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID == "4624"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`346d36c9-2e79-4d8f-8c14-1eef73d38737`](<../../../sentinelninja/Solutions Docs/content/standalone-content-346d36c9-2e79-4d8f-8c14-1eef73d38737-8e60a66e.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID == "4624"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`346d36c9-2e79-4d8f-8c14-1eef73d38737`](<../../../sentinelninja/Solutions Docs/content/standalone-content-346d36c9-2e79-4d8f-8c14-1eef73d38737-8e60a66e.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID == "4624"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`346d36c9-2e79-4d8f-8c14-1eef73d38737`](<../../../sentinelninja/Solutions Docs/content/standalone-content-346d36c9-2e79-4d8f-8c14-1eef73d38737-8e60a66e.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID == "4624"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`346d36c9-2e79-4d8f-8c14-1eef73d38737`](<../../../sentinelninja/Solutions Docs/content/standalone-content-346d36c9-2e79-4d8f-8c14-1eef73d38737-8e60a66e.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID == "4624"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`346d36c9-2e79-4d8f-8c14-1eef73d38737`](<../../../sentinelninja/Solutions Docs/content/standalone-content-346d36c9-2e79-4d8f-8c14-1eef73d38737-8e60a66e.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID == "4624"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`346d36c9-2e79-4d8f-8c14-1eef73d38737`](<../../../sentinelninja/Solutions Docs/content/standalone-content-346d36c9-2e79-4d8f-8c14-1eef73d38737-8e60a66e.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID == "4624"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`346d36c9-2e79-4d8f-8c14-1eef73d38737`](<../../../sentinelninja/Solutions Docs/content/standalone-content-346d36c9-2e79-4d8f-8c14-1eef73d38737-8e60a66e.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID == "4624"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`346d36c9-2e79-4d8f-8c14-1eef73d38737`](<../../../sentinelninja/Solutions Docs/content/standalone-content-346d36c9-2e79-4d8f-8c14-1eef73d38737-8e60a66e.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID == "4624"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`3a72ba65-00fa-4bbc-b246-be1ff3f73ce1`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3a72ba65-00fa-4bbc-b246-be1ff3f73ce1-a508a239.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`3a72ba65-00fa-4bbc-b246-be1ff3f73ce1`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3a72ba65-00fa-4bbc-b246-be1ff3f73ce1-a508a239.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`3a72ba65-00fa-4bbc-b246-be1ff3f73ce1`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3a72ba65-00fa-4bbc-b246-be1ff3f73ce1-a508a239.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`3a72ba65-00fa-4bbc-b246-be1ff3f73ce1`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3a72ba65-00fa-4bbc-b246-be1ff3f73ce1-a508a239.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`3a72ba65-00fa-4bbc-b246-be1ff3f73ce1`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3a72ba65-00fa-4bbc-b246-be1ff3f73ce1-a508a239.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`3a72ba65-00fa-4bbc-b246-be1ff3f73ce1`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3a72ba65-00fa-4bbc-b246-be1ff3f73ce1-a508a239.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`3a72ba65-00fa-4bbc-b246-be1ff3f73ce1`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3a72ba65-00fa-4bbc-b246-be1ff3f73ce1-a508a239.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`3a72ba65-00fa-4bbc-b246-be1ff3f73ce1`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3a72ba65-00fa-4bbc-b246-be1ff3f73ce1-a508a239.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`3a72ba65-00fa-4bbc-b246-be1ff3f73ce1`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3a72ba65-00fa-4bbc-b246-be1ff3f73ce1-a508a239.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`3b443f22-9be9-4c35-ac70-a94757748439`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3b443f22-9be9-4c35-ac70-a94757748439-95e86d24.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`3b443f22-9be9-4c35-ac70-a94757748439`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3b443f22-9be9-4c35-ac70-a94757748439-95e86d24.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`3b443f22-9be9-4c35-ac70-a94757748439`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3b443f22-9be9-4c35-ac70-a94757748439-95e86d24.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`3b443f22-9be9-4c35-ac70-a94757748439`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3b443f22-9be9-4c35-ac70-a94757748439-95e86d24.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`3b443f22-9be9-4c35-ac70-a94757748439`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3b443f22-9be9-4c35-ac70-a94757748439-95e86d24.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`3b443f22-9be9-4c35-ac70-a94757748439`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3b443f22-9be9-4c35-ac70-a94757748439-95e86d24.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`3b443f22-9be9-4c35-ac70-a94757748439`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3b443f22-9be9-4c35-ac70-a94757748439-95e86d24.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`3b443f22-9be9-4c35-ac70-a94757748439`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3b443f22-9be9-4c35-ac70-a94757748439-95e86d24.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`3b443f22-9be9-4c35-ac70-a94757748439`](<../../../sentinelninja/Solutions Docs/content/standalone-content-3b443f22-9be9-4c35-ac70-a94757748439-95e86d24.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`431cccd3-2dff-46ee-b34b-61933e45f556`](<../../../sentinelninja/Solutions Docs/content/standalone-content-431cccd3-2dff-46ee-b34b-61933e45f556-15327309.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID in "4624,4625,4720,4726,4728,4732,4756,7045"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`431cccd3-2dff-46ee-b34b-61933e45f556`](<../../../sentinelninja/Solutions Docs/content/standalone-content-431cccd3-2dff-46ee-b34b-61933e45f556-15327309.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID in "4624,4625,4720,4726,4728,4732,4756,7045"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`431cccd3-2dff-46ee-b34b-61933e45f556`](<../../../sentinelninja/Solutions Docs/content/standalone-content-431cccd3-2dff-46ee-b34b-61933e45f556-15327309.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID in "4624,4625,4720,4726,4728,4732,4756,7045"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`431cccd3-2dff-46ee-b34b-61933e45f556`](<../../../sentinelninja/Solutions Docs/content/standalone-content-431cccd3-2dff-46ee-b34b-61933e45f556-15327309.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID in "4624,4625,4720,4726,4728,4732,4756,7045"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`431cccd3-2dff-46ee-b34b-61933e45f556`](<../../../sentinelninja/Solutions Docs/content/standalone-content-431cccd3-2dff-46ee-b34b-61933e45f556-15327309.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID in "4624,4625,4720,4726,4728,4732,4756,7045"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`431cccd3-2dff-46ee-b34b-61933e45f556`](<../../../sentinelninja/Solutions Docs/content/standalone-content-431cccd3-2dff-46ee-b34b-61933e45f556-15327309.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID in "4624,4625,4720,4726,4728,4732,4756,7045"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`431cccd3-2dff-46ee-b34b-61933e45f556`](<../../../sentinelninja/Solutions Docs/content/standalone-content-431cccd3-2dff-46ee-b34b-61933e45f556-15327309.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID in "4624,4625,4720,4726,4728,4732,4756,7045"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`431cccd3-2dff-46ee-b34b-61933e45f556`](<../../../sentinelninja/Solutions Docs/content/standalone-content-431cccd3-2dff-46ee-b34b-61933e45f556-15327309.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID in "4624,4625,4720,4726,4728,4732,4756,7045"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`431cccd3-2dff-46ee-b34b-61933e45f556`](<../../../sentinelninja/Solutions Docs/content/standalone-content-431cccd3-2dff-46ee-b34b-61933e45f556-15327309.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SecurityEvent.EventID in "4624,4625,4720,4726,4728,4732,4756,7045"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`4e5914a4-2ccd-429d-a845-fa597f0bd8c5`](<../../../sentinelninja/Solutions Docs/content/standalone-content-4e5914a4-2ccd-429d-a845-fa597f0bd8c5-2c324bc6.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`4e5914a4-2ccd-429d-a845-fa597f0bd8c5`](<../../../sentinelninja/Solutions Docs/content/standalone-content-4e5914a4-2ccd-429d-a845-fa597f0bd8c5-2c324bc6.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`4e5914a4-2ccd-429d-a845-fa597f0bd8c5`](<../../../sentinelninja/Solutions Docs/content/standalone-content-4e5914a4-2ccd-429d-a845-fa597f0bd8c5-2c324bc6.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`4e5914a4-2ccd-429d-a845-fa597f0bd8c5`](<../../../sentinelninja/Solutions Docs/content/standalone-content-4e5914a4-2ccd-429d-a845-fa597f0bd8c5-2c324bc6.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`4e5914a4-2ccd-429d-a845-fa597f0bd8c5`](<../../../sentinelninja/Solutions Docs/content/standalone-content-4e5914a4-2ccd-429d-a845-fa597f0bd8c5-2c324bc6.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`4e5914a4-2ccd-429d-a845-fa597f0bd8c5`](<../../../sentinelninja/Solutions Docs/content/standalone-content-4e5914a4-2ccd-429d-a845-fa597f0bd8c5-2c324bc6.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`4e5914a4-2ccd-429d-a845-fa597f0bd8c5`](<../../../sentinelninja/Solutions Docs/content/standalone-content-4e5914a4-2ccd-429d-a845-fa597f0bd8c5-2c324bc6.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`4e5914a4-2ccd-429d-a845-fa597f0bd8c5`](<../../../sentinelninja/Solutions Docs/content/standalone-content-4e5914a4-2ccd-429d-a845-fa597f0bd8c5-2c324bc6.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`4e5914a4-2ccd-429d-a845-fa597f0bd8c5`](<../../../sentinelninja/Solutions Docs/content/standalone-content-4e5914a4-2ccd-429d-a845-fa597f0bd8c5-2c324bc6.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`5f171045-88ab-4634-baae-a7b6509f483b`](<../../../sentinelninja/Solutions Docs/content/standalone-content-5f171045-88ab-4634-baae-a7b6509f483b-08963161.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`5f171045-88ab-4634-baae-a7b6509f483b`](<../../../sentinelninja/Solutions Docs/content/standalone-content-5f171045-88ab-4634-baae-a7b6509f483b-08963161.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`5f171045-88ab-4634-baae-a7b6509f483b`](<../../../sentinelninja/Solutions Docs/content/standalone-content-5f171045-88ab-4634-baae-a7b6509f483b-08963161.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`5f171045-88ab-4634-baae-a7b6509f483b`](<../../../sentinelninja/Solutions Docs/content/standalone-content-5f171045-88ab-4634-baae-a7b6509f483b-08963161.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`5f171045-88ab-4634-baae-a7b6509f483b`](<../../../sentinelninja/Solutions Docs/content/standalone-content-5f171045-88ab-4634-baae-a7b6509f483b-08963161.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`5f171045-88ab-4634-baae-a7b6509f483b`](<../../../sentinelninja/Solutions Docs/content/standalone-content-5f171045-88ab-4634-baae-a7b6509f483b-08963161.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`5f171045-88ab-4634-baae-a7b6509f483b`](<../../../sentinelninja/Solutions Docs/content/standalone-content-5f171045-88ab-4634-baae-a7b6509f483b-08963161.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`5f171045-88ab-4634-baae-a7b6509f483b`](<../../../sentinelninja/Solutions Docs/content/standalone-content-5f171045-88ab-4634-baae-a7b6509f483b-08963161.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`61a6edc0-e71a-4084-8f3c-05a58e1b9012`](<../../../sentinelninja/Solutions Docs/content/standalone-content-61a6edc0-e71a-4084-8f3c-05a58e1b9012-f842671f.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`61a6edc0-e71a-4084-8f3c-05a58e1b9012`](<../../../sentinelninja/Solutions Docs/content/standalone-content-61a6edc0-e71a-4084-8f3c-05a58e1b9012-f842671f.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`61a6edc0-e71a-4084-8f3c-05a58e1b9012`](<../../../sentinelninja/Solutions Docs/content/standalone-content-61a6edc0-e71a-4084-8f3c-05a58e1b9012-f842671f.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`61a6edc0-e71a-4084-8f3c-05a58e1b9012`](<../../../sentinelninja/Solutions Docs/content/standalone-content-61a6edc0-e71a-4084-8f3c-05a58e1b9012-f842671f.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`61a6edc0-e71a-4084-8f3c-05a58e1b9012`](<../../../sentinelninja/Solutions Docs/content/standalone-content-61a6edc0-e71a-4084-8f3c-05a58e1b9012-f842671f.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`61a6edc0-e71a-4084-8f3c-05a58e1b9012`](<../../../sentinelninja/Solutions Docs/content/standalone-content-61a6edc0-e71a-4084-8f3c-05a58e1b9012-f842671f.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`61a6edc0-e71a-4084-8f3c-05a58e1b9012`](<../../../sentinelninja/Solutions Docs/content/standalone-content-61a6edc0-e71a-4084-8f3c-05a58e1b9012-f842671f.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`61a6edc0-e71a-4084-8f3c-05a58e1b9012`](<../../../sentinelninja/Solutions Docs/content/standalone-content-61a6edc0-e71a-4084-8f3c-05a58e1b9012-f842671f.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`61a6edc0-e71a-4084-8f3c-05a58e1b9012`](<../../../sentinelninja/Solutions Docs/content/standalone-content-61a6edc0-e71a-4084-8f3c-05a58e1b9012-f842671f.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`6267ce44-1e9d-471b-9f1e-ae76a6b7aa84`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6267ce44-1e9d-471b-9f1e-ae76a6b7aa84-9f461680.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `DeviceEvents.ActionType in "FileCreated,FileDownloaded,FileRenamed,UsbDriveMounted"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`6267ce44-1e9d-471b-9f1e-ae76a6b7aa84`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6267ce44-1e9d-471b-9f1e-ae76a6b7aa84-9f461680.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `DeviceEvents.ActionType in "FileCreated,FileDownloaded,FileRenamed,UsbDriveMounted"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`6267ce44-1e9d-471b-9f1e-ae76a6b7aa84`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6267ce44-1e9d-471b-9f1e-ae76a6b7aa84-9f461680.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `DeviceEvents.ActionType in "FileCreated,FileDownloaded,FileRenamed,UsbDriveMounted"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`6267ce44-1e9d-471b-9f1e-ae76a6b7aa84`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6267ce44-1e9d-471b-9f1e-ae76a6b7aa84-9f461680.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `DeviceEvents.ActionType in "FileCreated,FileDownloaded,FileRenamed,UsbDriveMounted"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`6267ce44-1e9d-471b-9f1e-ae76a6b7aa84`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6267ce44-1e9d-471b-9f1e-ae76a6b7aa84-9f461680.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `DeviceEvents.ActionType in "FileCreated,FileDownloaded,FileRenamed,UsbDriveMounted"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`6267ce44-1e9d-471b-9f1e-ae76a6b7aa84`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6267ce44-1e9d-471b-9f1e-ae76a6b7aa84-9f461680.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `DeviceEvents.ActionType in "FileCreated,FileDownloaded,FileRenamed,UsbDriveMounted"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`6267ce44-1e9d-471b-9f1e-ae76a6b7aa84`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6267ce44-1e9d-471b-9f1e-ae76a6b7aa84-9f461680.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `DeviceEvents.ActionType in "FileCreated,FileDownloaded,FileRenamed,UsbDriveMounted"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`6267ce44-1e9d-471b-9f1e-ae76a6b7aa84`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6267ce44-1e9d-471b-9f1e-ae76a6b7aa84-9f461680.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `DeviceEvents.ActionType in "FileCreated,FileDownloaded,FileRenamed,UsbDriveMounted"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`6267ce44-1e9d-471b-9f1e-ae76a6b7aa84`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6267ce44-1e9d-471b-9f1e-ae76a6b7aa84-9f461680.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `DeviceEvents.ActionType in "FileCreated,FileDownloaded,FileRenamed,UsbDriveMounted"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`635cba46-c077-4959-a2d9-b7eb6fecb854`](<../../../sentinelninja/Solutions Docs/content/standalone-content-635cba46-c077-4959-a2d9-b7eb6fecb854-b24b7b1e.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`635cba46-c077-4959-a2d9-b7eb6fecb854`](<../../../sentinelninja/Solutions Docs/content/standalone-content-635cba46-c077-4959-a2d9-b7eb6fecb854-b24b7b1e.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`635cba46-c077-4959-a2d9-b7eb6fecb854`](<../../../sentinelninja/Solutions Docs/content/standalone-content-635cba46-c077-4959-a2d9-b7eb6fecb854-b24b7b1e.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`635cba46-c077-4959-a2d9-b7eb6fecb854`](<../../../sentinelninja/Solutions Docs/content/standalone-content-635cba46-c077-4959-a2d9-b7eb6fecb854-b24b7b1e.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`635cba46-c077-4959-a2d9-b7eb6fecb854`](<../../../sentinelninja/Solutions Docs/content/standalone-content-635cba46-c077-4959-a2d9-b7eb6fecb854-b24b7b1e.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`635cba46-c077-4959-a2d9-b7eb6fecb854`](<../../../sentinelninja/Solutions Docs/content/standalone-content-635cba46-c077-4959-a2d9-b7eb6fecb854-b24b7b1e.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`635cba46-c077-4959-a2d9-b7eb6fecb854`](<../../../sentinelninja/Solutions Docs/content/standalone-content-635cba46-c077-4959-a2d9-b7eb6fecb854-b24b7b1e.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`635cba46-c077-4959-a2d9-b7eb6fecb854`](<../../../sentinelninja/Solutions Docs/content/standalone-content-635cba46-c077-4959-a2d9-b7eb6fecb854-b24b7b1e.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`635cba46-c077-4959-a2d9-b7eb6fecb854`](<../../../sentinelninja/Solutions Docs/content/standalone-content-635cba46-c077-4959-a2d9-b7eb6fecb854-b24b7b1e.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`6962473c-bcb8-421d-a0db-826078cad280`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6962473c-bcb8-421d-a0db-826078cad280-f396ca65.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SigninLogs.OperationName has_any "Add member to role"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`6962473c-bcb8-421d-a0db-826078cad280`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6962473c-bcb8-421d-a0db-826078cad280-f396ca65.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SigninLogs.OperationName has_any "Add member to role"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`6962473c-bcb8-421d-a0db-826078cad280`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6962473c-bcb8-421d-a0db-826078cad280-f396ca65.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SigninLogs.OperationName has_any "Add member to role"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`6962473c-bcb8-421d-a0db-826078cad280`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6962473c-bcb8-421d-a0db-826078cad280-f396ca65.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SigninLogs.OperationName has_any "Add member to role"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`6962473c-bcb8-421d-a0db-826078cad280`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6962473c-bcb8-421d-a0db-826078cad280-f396ca65.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SigninLogs.OperationName has_any "Add member to role"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`6962473c-bcb8-421d-a0db-826078cad280`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6962473c-bcb8-421d-a0db-826078cad280-f396ca65.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SigninLogs.OperationName has_any "Add member to role"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`6962473c-bcb8-421d-a0db-826078cad280`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6962473c-bcb8-421d-a0db-826078cad280-f396ca65.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SigninLogs.OperationName has_any "Add member to role"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`6962473c-bcb8-421d-a0db-826078cad280`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6962473c-bcb8-421d-a0db-826078cad280-f396ca65.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SigninLogs.OperationName has_any "Add member to role"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`6962473c-bcb8-421d-a0db-826078cad280`](<../../../sentinelninja/Solutions Docs/content/standalone-content-6962473c-bcb8-421d-a0db-826078cad280-f396ca65.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `SigninLogs.OperationName has_any "Add member to role"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`7098cae1-c632-4b40-b715-86d6b07720d7`](<../../../sentinelninja/Solutions Docs/content/standalone-content-7098cae1-c632-4b40-b715-86d6b07720d7-58572e04.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`7098cae1-c632-4b40-b715-86d6b07720d7`](<../../../sentinelninja/Solutions Docs/content/standalone-content-7098cae1-c632-4b40-b715-86d6b07720d7-58572e04.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`7098cae1-c632-4b40-b715-86d6b07720d7`](<../../../sentinelninja/Solutions Docs/content/standalone-content-7098cae1-c632-4b40-b715-86d6b07720d7-58572e04.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`7098cae1-c632-4b40-b715-86d6b07720d7`](<../../../sentinelninja/Solutions Docs/content/standalone-content-7098cae1-c632-4b40-b715-86d6b07720d7-58572e04.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`7098cae1-c632-4b40-b715-86d6b07720d7`](<../../../sentinelninja/Solutions Docs/content/standalone-content-7098cae1-c632-4b40-b715-86d6b07720d7-58572e04.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`7098cae1-c632-4b40-b715-86d6b07720d7`](<../../../sentinelninja/Solutions Docs/content/standalone-content-7098cae1-c632-4b40-b715-86d6b07720d7-58572e04.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`7098cae1-c632-4b40-b715-86d6b07720d7`](<../../../sentinelninja/Solutions Docs/content/standalone-content-7098cae1-c632-4b40-b715-86d6b07720d7-58572e04.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`7098cae1-c632-4b40-b715-86d6b07720d7`](<../../../sentinelninja/Solutions Docs/content/standalone-content-7098cae1-c632-4b40-b715-86d6b07720d7-58572e04.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`7098cae1-c632-4b40-b715-86d6b07720d7`](<../../../sentinelninja/Solutions Docs/content/standalone-content-7098cae1-c632-4b40-b715-86d6b07720d7-58572e04.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`779731f7-8ba0-4198-8524-5701b7defddc`](<../../../sentinelninja/Solutions Docs/content/standalone-content-779731f7-8ba0-4198-8524-5701b7defddc-2c5c50eb.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceProduct startswith "FireWall"`
  - `CommonSecurityLog.DeviceProduct startswith "FortiGate"`
  - `CommonSecurityLog.DeviceProduct startswith "NSSWeblog"`
  - `CommonSecurityLog.DeviceProduct startswith "PAN"`
  - `CommonSecurityLog.DeviceProduct startswith "URL"`
  - `CommonSecurityLog.DeviceProduct startswith "VPN"`
  - `CommonSecurityLog.DeviceVendor has_any "Check Point,Fortinet,Palo Alto Networks,Zscaler"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`84026aa0-7020-45d0-9f85-d526e43de2ab`](<../../../sentinelninja/Solutions Docs/content/standalone-content-84026aa0-7020-45d0-9f85-d526e43de2ab-fe5a3229.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`84026aa0-7020-45d0-9f85-d526e43de2ab`](<../../../sentinelninja/Solutions Docs/content/standalone-content-84026aa0-7020-45d0-9f85-d526e43de2ab-fe5a3229.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`84026aa0-7020-45d0-9f85-d526e43de2ab`](<../../../sentinelninja/Solutions Docs/content/standalone-content-84026aa0-7020-45d0-9f85-d526e43de2ab-fe5a3229.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`84026aa0-7020-45d0-9f85-d526e43de2ab`](<../../../sentinelninja/Solutions Docs/content/standalone-content-84026aa0-7020-45d0-9f85-d526e43de2ab-fe5a3229.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`84026aa0-7020-45d0-9f85-d526e43de2ab`](<../../../sentinelninja/Solutions Docs/content/standalone-content-84026aa0-7020-45d0-9f85-d526e43de2ab-fe5a3229.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`84026aa0-7020-45d0-9f85-d526e43de2ab`](<../../../sentinelninja/Solutions Docs/content/standalone-content-84026aa0-7020-45d0-9f85-d526e43de2ab-fe5a3229.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`84026aa0-7020-45d0-9f85-d526e43de2ab`](<../../../sentinelninja/Solutions Docs/content/standalone-content-84026aa0-7020-45d0-9f85-d526e43de2ab-fe5a3229.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`84026aa0-7020-45d0-9f85-d526e43de2ab`](<../../../sentinelninja/Solutions Docs/content/standalone-content-84026aa0-7020-45d0-9f85-d526e43de2ab-fe5a3229.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`84026aa0-7020-45d0-9f85-d526e43de2ab`](<../../../sentinelninja/Solutions Docs/content/standalone-content-84026aa0-7020-45d0-9f85-d526e43de2ab-fe5a3229.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`860a8df2-8d19-4c60-bf61-de1c02422797`](<../../../sentinelninja/Solutions Docs/content/standalone-content-860a8df2-8d19-4c60-bf61-de1c02422797-185639de.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`860a8df2-8d19-4c60-bf61-de1c02422797`](<../../../sentinelninja/Solutions Docs/content/standalone-content-860a8df2-8d19-4c60-bf61-de1c02422797-185639de.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`860a8df2-8d19-4c60-bf61-de1c02422797`](<../../../sentinelninja/Solutions Docs/content/standalone-content-860a8df2-8d19-4c60-bf61-de1c02422797-185639de.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`860a8df2-8d19-4c60-bf61-de1c02422797`](<../../../sentinelninja/Solutions Docs/content/standalone-content-860a8df2-8d19-4c60-bf61-de1c02422797-185639de.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`860a8df2-8d19-4c60-bf61-de1c02422797`](<../../../sentinelninja/Solutions Docs/content/standalone-content-860a8df2-8d19-4c60-bf61-de1c02422797-185639de.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`860a8df2-8d19-4c60-bf61-de1c02422797`](<../../../sentinelninja/Solutions Docs/content/standalone-content-860a8df2-8d19-4c60-bf61-de1c02422797-185639de.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`860a8df2-8d19-4c60-bf61-de1c02422797`](<../../../sentinelninja/Solutions Docs/content/standalone-content-860a8df2-8d19-4c60-bf61-de1c02422797-185639de.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`860a8df2-8d19-4c60-bf61-de1c02422797`](<../../../sentinelninja/Solutions Docs/content/standalone-content-860a8df2-8d19-4c60-bf61-de1c02422797-185639de.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`860a8df2-8d19-4c60-bf61-de1c02422797`](<../../../sentinelninja/Solutions Docs/content/standalone-content-860a8df2-8d19-4c60-bf61-de1c02422797-185639de.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Fortinet"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`8ea8b2af-f1ce-4464-964c-6763641cc4f6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ea8b2af-f1ce-4464-964c-6763641cc4f6-a9191d0d.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `AuditLogs.OperationName =~ "Read BitLocker key"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`8ea8b2af-f1ce-4464-964c-6763641cc4f6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ea8b2af-f1ce-4464-964c-6763641cc4f6-a9191d0d.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `AuditLogs.OperationName =~ "Read BitLocker key"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`8ea8b2af-f1ce-4464-964c-6763641cc4f6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ea8b2af-f1ce-4464-964c-6763641cc4f6-a9191d0d.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `AuditLogs.OperationName =~ "Read BitLocker key"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`8ea8b2af-f1ce-4464-964c-6763641cc4f6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ea8b2af-f1ce-4464-964c-6763641cc4f6-a9191d0d.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `AuditLogs.OperationName =~ "Read BitLocker key"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`8ea8b2af-f1ce-4464-964c-6763641cc4f6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ea8b2af-f1ce-4464-964c-6763641cc4f6-a9191d0d.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `AuditLogs.OperationName =~ "Read BitLocker key"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`8ea8b2af-f1ce-4464-964c-6763641cc4f6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ea8b2af-f1ce-4464-964c-6763641cc4f6-a9191d0d.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `AuditLogs.OperationName =~ "Read BitLocker key"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`8ea8b2af-f1ce-4464-964c-6763641cc4f6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ea8b2af-f1ce-4464-964c-6763641cc4f6-a9191d0d.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `AuditLogs.OperationName =~ "Read BitLocker key"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`8ea8b2af-f1ce-4464-964c-6763641cc4f6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ea8b2af-f1ce-4464-964c-6763641cc4f6-a9191d0d.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `AuditLogs.OperationName =~ "Read BitLocker key"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`8ea8b2af-f1ce-4464-964c-6763641cc4f6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ea8b2af-f1ce-4464-964c-6763641cc4f6-a9191d0d.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `AuditLogs.OperationName =~ "Read BitLocker key"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`8ee967a2-a645-4832-85f4-72b635bcb3a6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ee967a2-a645-4832-85f4-72b635bcb3a6-5072f9dd.md>) ↔ [`CiscoMeraki(usingRESTAPI)`](<../../../sentinelninja/Solutions Docs/connectors/ciscomeraki-usingrestapi.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "Accepted"`
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### item: [`8ee967a2-a645-4832-85f4-72b635bcb3a6`](<../../../sentinelninja/Solutions Docs/content/standalone-content-8ee967a2-a645-4832-85f4-72b635bcb3a6-5072f9dd.md>) ↔ [`CiscoMerakiNativePoller`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakinativepoller.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.Facility contains "auth"`
  - `Syslog.ProcessName != "sudo"`
  - `Syslog.SyslogMessage has "Accepted"`
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### item: [`959fe0f0-7ac0-467c-944f-5b8c6fdc9e72`](<../../../sentinelninja/Solutions Docs/content/standalone-content-959fe0f0-7ac0-467c-944f-5b8c6fdc9e72-56e135bf.md>) ↔ [`CiscoMeraki(usingRESTAPI)`](<../../../sentinelninja/Solutions Docs/connectors/ciscomeraki-usingrestapi.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.ProcessName contains "squid"`
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### item: [`959fe0f0-7ac0-467c-944f-5b8c6fdc9e72`](<../../../sentinelninja/Solutions Docs/content/standalone-content-959fe0f0-7ac0-467c-944f-5b8c6fdc9e72-56e135bf.md>) ↔ [`CiscoMerakiNativePoller`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakinativepoller.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `Syslog.ProcessName contains "squid"`
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### item: [`98fdd28d-9c13-431b-aca9-e6cfbb90a5a9`](<../../../sentinelninja/Solutions Docs/content/standalone-content-98fdd28d-9c13-431b-aca9-e6cfbb90a5a9-a10fc757.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`98fdd28d-9c13-431b-aca9-e6cfbb90a5a9`](<../../../sentinelninja/Solutions Docs/content/standalone-content-98fdd28d-9c13-431b-aca9-e6cfbb90a5a9-a10fc757.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`98fdd28d-9c13-431b-aca9-e6cfbb90a5a9`](<../../../sentinelninja/Solutions Docs/content/standalone-content-98fdd28d-9c13-431b-aca9-e6cfbb90a5a9-a10fc757.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`98fdd28d-9c13-431b-aca9-e6cfbb90a5a9`](<../../../sentinelninja/Solutions Docs/content/standalone-content-98fdd28d-9c13-431b-aca9-e6cfbb90a5a9-a10fc757.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`98fdd28d-9c13-431b-aca9-e6cfbb90a5a9`](<../../../sentinelninja/Solutions Docs/content/standalone-content-98fdd28d-9c13-431b-aca9-e6cfbb90a5a9-a10fc757.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`98fdd28d-9c13-431b-aca9-e6cfbb90a5a9`](<../../../sentinelninja/Solutions Docs/content/standalone-content-98fdd28d-9c13-431b-aca9-e6cfbb90a5a9-a10fc757.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`98fdd28d-9c13-431b-aca9-e6cfbb90a5a9`](<../../../sentinelninja/Solutions Docs/content/standalone-content-98fdd28d-9c13-431b-aca9-e6cfbb90a5a9-a10fc757.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`98fdd28d-9c13-431b-aca9-e6cfbb90a5a9`](<../../../sentinelninja/Solutions Docs/content/standalone-content-98fdd28d-9c13-431b-aca9-e6cfbb90a5a9-a10fc757.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`98fdd28d-9c13-431b-aca9-e6cfbb90a5a9`](<../../../sentinelninja/Solutions Docs/content/standalone-content-98fdd28d-9c13-431b-aca9-e6cfbb90a5a9-a10fc757.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`a1adce9c-5945-4a20-984e-d95b6071a791`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a1adce9c-5945-4a20-984e-d95b6071a791-6a47b90f.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`a1adce9c-5945-4a20-984e-d95b6071a791`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a1adce9c-5945-4a20-984e-d95b6071a791-6a47b90f.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`a1adce9c-5945-4a20-984e-d95b6071a791`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a1adce9c-5945-4a20-984e-d95b6071a791-6a47b90f.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`a1adce9c-5945-4a20-984e-d95b6071a791`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a1adce9c-5945-4a20-984e-d95b6071a791-6a47b90f.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`a1adce9c-5945-4a20-984e-d95b6071a791`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a1adce9c-5945-4a20-984e-d95b6071a791-6a47b90f.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`a1adce9c-5945-4a20-984e-d95b6071a791`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a1adce9c-5945-4a20-984e-d95b6071a791-6a47b90f.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`a1adce9c-5945-4a20-984e-d95b6071a791`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a1adce9c-5945-4a20-984e-d95b6071a791-6a47b90f.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`a1adce9c-5945-4a20-984e-d95b6071a791`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a1adce9c-5945-4a20-984e-d95b6071a791-6a47b90f.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`a1adce9c-5945-4a20-984e-d95b6071a791`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a1adce9c-5945-4a20-984e-d95b6071a791-6a47b90f.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`a333d8bf-22a3-4c55-a1e9-5f0a135c0253`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a333d8bf-22a3-4c55-a1e9-5f0a135c0253-2e290b6c.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`a333d8bf-22a3-4c55-a1e9-5f0a135c0253`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a333d8bf-22a3-4c55-a1e9-5f0a135c0253-2e290b6c.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`a333d8bf-22a3-4c55-a1e9-5f0a135c0253`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a333d8bf-22a3-4c55-a1e9-5f0a135c0253-2e290b6c.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`a333d8bf-22a3-4c55-a1e9-5f0a135c0253`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a333d8bf-22a3-4c55-a1e9-5f0a135c0253-2e290b6c.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`a333d8bf-22a3-4c55-a1e9-5f0a135c0253`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a333d8bf-22a3-4c55-a1e9-5f0a135c0253-2e290b6c.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`a333d8bf-22a3-4c55-a1e9-5f0a135c0253`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a333d8bf-22a3-4c55-a1e9-5f0a135c0253-2e290b6c.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`a333d8bf-22a3-4c55-a1e9-5f0a135c0253`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a333d8bf-22a3-4c55-a1e9-5f0a135c0253-2e290b6c.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`a333d8bf-22a3-4c55-a1e9-5f0a135c0253`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a333d8bf-22a3-4c55-a1e9-5f0a135c0253-2e290b6c.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`a333d8bf-22a3-4c55-a1e9-5f0a135c0253`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a333d8bf-22a3-4c55-a1e9-5f0a135c0253-2e290b6c.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`a5b3429d-f1da-42b9-883c-327ecb7b91ff`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a5b3429d-f1da-42b9-883c-327ecb7b91ff-31b4d4f1.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`a5b3429d-f1da-42b9-883c-327ecb7b91ff`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a5b3429d-f1da-42b9-883c-327ecb7b91ff-31b4d4f1.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`a5b3429d-f1da-42b9-883c-327ecb7b91ff`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a5b3429d-f1da-42b9-883c-327ecb7b91ff-31b4d4f1.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`a5b3429d-f1da-42b9-883c-327ecb7b91ff`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a5b3429d-f1da-42b9-883c-327ecb7b91ff-31b4d4f1.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`a5b3429d-f1da-42b9-883c-327ecb7b91ff`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a5b3429d-f1da-42b9-883c-327ecb7b91ff-31b4d4f1.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`a5b3429d-f1da-42b9-883c-327ecb7b91ff`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a5b3429d-f1da-42b9-883c-327ecb7b91ff-31b4d4f1.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`a5b3429d-f1da-42b9-883c-327ecb7b91ff`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a5b3429d-f1da-42b9-883c-327ecb7b91ff-31b4d4f1.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`a5b3429d-f1da-42b9-883c-327ecb7b91ff`](<../../../sentinelninja/Solutions Docs/content/standalone-content-a5b3429d-f1da-42b9-883c-327ecb7b91ff-31b4d4f1.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`bac44fe4-c0bc-4e90-aa48-2e346fda803f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bac44fe4-c0bc-4e90-aa48-2e346fda803f-cd84615c.md>) ↔ [`CiscoMeraki(usingRESTAPI)`](<../../../sentinelninja/Solutions Docs/connectors/ciscomeraki-usingrestapi.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### item: [`bac44fe4-c0bc-4e90-aa48-2e346fda803f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bac44fe4-c0bc-4e90-aa48-2e346fda803f-cd84615c.md>) ↔ [`CiscoMerakiNativePoller`](<../../../sentinelninja/Solutions Docs/connectors/ciscomerakinativepoller.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `_Computed.Action == "block"`
  - `_Computed.EventOriginalType == "IDS Alert"`
  - `_Computed.LogType in "bridge_anyconnect_client_vpn_firewall,cellular_firewall,firewall,flows,vpn_firewall"`
  - `_Computed.LogType !contains "firewall"`
  - `_Computed.LogType !contains "flows"`
  - `_Computed.LogType !in "urls,airmarshal_events,security_event,ids-alerts,events"`
  - `_Computed.LogType has "airmarshal_events"`
  - `_Computed.LogType has "events"`
  - `_Computed.LogType has "flows"`
  - `_Computed.LogType has "ids-alerts"`
  - `_Computed.LogType has "security_event"`
  - `_Computed.LogType has "urls"`
  - `_Computed.LogType has_any "flows"`
  - `_Computed.NetworkProtocol has "tcp"`
  - `_Computed.NetworkProtocol has "udp"`
  - `_Computed.Priority in "1,2,3,4"`

#### item: [`bca9c877-2afc-4246-a26d-087ab1cdcd5f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bca9c877-2afc-4246-a26d-087ab1cdcd5f-603c39d3.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`bca9c877-2afc-4246-a26d-087ab1cdcd5f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bca9c877-2afc-4246-a26d-087ab1cdcd5f-603c39d3.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`bca9c877-2afc-4246-a26d-087ab1cdcd5f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bca9c877-2afc-4246-a26d-087ab1cdcd5f-603c39d3.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`bca9c877-2afc-4246-a26d-087ab1cdcd5f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bca9c877-2afc-4246-a26d-087ab1cdcd5f-603c39d3.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`bca9c877-2afc-4246-a26d-087ab1cdcd5f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bca9c877-2afc-4246-a26d-087ab1cdcd5f-603c39d3.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`bca9c877-2afc-4246-a26d-087ab1cdcd5f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bca9c877-2afc-4246-a26d-087ab1cdcd5f-603c39d3.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`bca9c877-2afc-4246-a26d-087ab1cdcd5f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bca9c877-2afc-4246-a26d-087ab1cdcd5f-603c39d3.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`bca9c877-2afc-4246-a26d-087ab1cdcd5f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bca9c877-2afc-4246-a26d-087ab1cdcd5f-603c39d3.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`bca9c877-2afc-4246-a26d-087ab1cdcd5f`](<../../../sentinelninja/Solutions Docs/content/standalone-content-bca9c877-2afc-4246-a26d-087ab1cdcd5f-603c39d3.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`d0a3cb7b-375e-402d-9827-adafe0ce386d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d0a3cb7b-375e-402d-9827-adafe0ce386d-b13db268.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`d0a3cb7b-375e-402d-9827-adafe0ce386d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d0a3cb7b-375e-402d-9827-adafe0ce386d-b13db268.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`d0a3cb7b-375e-402d-9827-adafe0ce386d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d0a3cb7b-375e-402d-9827-adafe0ce386d-b13db268.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`d0a3cb7b-375e-402d-9827-adafe0ce386d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d0a3cb7b-375e-402d-9827-adafe0ce386d-b13db268.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`d0a3cb7b-375e-402d-9827-adafe0ce386d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d0a3cb7b-375e-402d-9827-adafe0ce386d-b13db268.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`d0a3cb7b-375e-402d-9827-adafe0ce386d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d0a3cb7b-375e-402d-9827-adafe0ce386d-b13db268.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`d0a3cb7b-375e-402d-9827-adafe0ce386d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d0a3cb7b-375e-402d-9827-adafe0ce386d-b13db268.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`d0a3cb7b-375e-402d-9827-adafe0ce386d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d0a3cb7b-375e-402d-9827-adafe0ce386d-b13db268.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`d2e6f31b-add1-4f44-b54d-1975a5605c1d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d2e6f31b-add1-4f44-b54d-1975a5605c1d-30418ef1.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`d2e6f31b-add1-4f44-b54d-1975a5605c1d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d2e6f31b-add1-4f44-b54d-1975a5605c1d-30418ef1.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`d2e6f31b-add1-4f44-b54d-1975a5605c1d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d2e6f31b-add1-4f44-b54d-1975a5605c1d-30418ef1.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`d2e6f31b-add1-4f44-b54d-1975a5605c1d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d2e6f31b-add1-4f44-b54d-1975a5605c1d-30418ef1.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`d2e6f31b-add1-4f44-b54d-1975a5605c1d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d2e6f31b-add1-4f44-b54d-1975a5605c1d-30418ef1.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`d2e6f31b-add1-4f44-b54d-1975a5605c1d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d2e6f31b-add1-4f44-b54d-1975a5605c1d-30418ef1.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`d2e6f31b-add1-4f44-b54d-1975a5605c1d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d2e6f31b-add1-4f44-b54d-1975a5605c1d-30418ef1.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`d2e6f31b-add1-4f44-b54d-1975a5605c1d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d2e6f31b-add1-4f44-b54d-1975a5605c1d-30418ef1.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`d2e6f31b-add1-4f44-b54d-1975a5605c1d`](<../../../sentinelninja/Solutions Docs/content/standalone-content-d2e6f31b-add1-4f44-b54d-1975a5605c1d-30418ef1.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`dc5adcc9-70ab-4fba-8690-f57767e8ca02`](<../../../sentinelninja/Solutions Docs/content/standalone-content-dc5adcc9-70ab-4fba-8690-f57767e8ca02-470cbc14.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`dc5adcc9-70ab-4fba-8690-f57767e8ca02`](<../../../sentinelninja/Solutions Docs/content/standalone-content-dc5adcc9-70ab-4fba-8690-f57767e8ca02-470cbc14.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`dc5adcc9-70ab-4fba-8690-f57767e8ca02`](<../../../sentinelninja/Solutions Docs/content/standalone-content-dc5adcc9-70ab-4fba-8690-f57767e8ca02-470cbc14.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`dc5adcc9-70ab-4fba-8690-f57767e8ca02`](<../../../sentinelninja/Solutions Docs/content/standalone-content-dc5adcc9-70ab-4fba-8690-f57767e8ca02-470cbc14.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`dc5adcc9-70ab-4fba-8690-f57767e8ca02`](<../../../sentinelninja/Solutions Docs/content/standalone-content-dc5adcc9-70ab-4fba-8690-f57767e8ca02-470cbc14.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`dc5adcc9-70ab-4fba-8690-f57767e8ca02`](<../../../sentinelninja/Solutions Docs/content/standalone-content-dc5adcc9-70ab-4fba-8690-f57767e8ca02-470cbc14.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`dc5adcc9-70ab-4fba-8690-f57767e8ca02`](<../../../sentinelninja/Solutions Docs/content/standalone-content-dc5adcc9-70ab-4fba-8690-f57767e8ca02-470cbc14.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`dc5adcc9-70ab-4fba-8690-f57767e8ca02`](<../../../sentinelninja/Solutions Docs/content/standalone-content-dc5adcc9-70ab-4fba-8690-f57767e8ca02-470cbc14.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`dc5adcc9-70ab-4fba-8690-f57767e8ca02`](<../../../sentinelninja/Solutions Docs/content/standalone-content-dc5adcc9-70ab-4fba-8690-f57767e8ca02-470cbc14.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - `CommonSecurityLog.DeviceVendor =~ "Palo Alto Networks"`
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

#### item: [`e70fa6e0-796a-4e85-9420-98b17b0bb749`](<../../../sentinelninja/Solutions Docs/content/standalone-content-e70fa6e0-796a-4e85-9420-98b17b0bb749-a9282ff0.md>) ↔ [`AzureActiveDirectoryIdentityProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureactivedirectoryidentityprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Active Directory Identity Protection"`

#### item: [`e70fa6e0-796a-4e85-9420-98b17b0bb749`](<../../../sentinelninja/Solutions Docs/content/standalone-content-e70fa6e0-796a-4e85-9420-98b17b0bb749-a9282ff0.md>) ↔ [`AzureAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/azureadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Advanced Threat Protection"`

#### item: [`e70fa6e0-796a-4e85-9420-98b17b0bb749`](<../../../sentinelninja/Solutions Docs/content/standalone-content-e70fa6e0-796a-4e85-9420-98b17b0bb749-a9282ff0.md>) ↔ [`AzureSecurityCenter`](<../../../sentinelninja/Solutions Docs/connectors/azuresecuritycenter.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`e70fa6e0-796a-4e85-9420-98b17b0bb749`](<../../../sentinelninja/Solutions Docs/content/standalone-content-e70fa6e0-796a-4e85-9420-98b17b0bb749-a9282ff0.md>) ↔ [`IoT`](<../../../sentinelninja/Solutions Docs/connectors/iot.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center for IoT"`

#### item: [`e70fa6e0-796a-4e85-9420-98b17b0bb749`](<../../../sentinelninja/Solutions Docs/content/standalone-content-e70fa6e0-796a-4e85-9420-98b17b0bb749-a9282ff0.md>) ↔ [`MicrosoftCloudAppSecurity`](<../../../sentinelninja/Solutions Docs/connectors/microsoftcloudappsecurity.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft Cloud App Security"`

#### item: [`e70fa6e0-796a-4e85-9420-98b17b0bb749`](<../../../sentinelninja/Solutions Docs/content/standalone-content-e70fa6e0-796a-4e85-9420-98b17b0bb749-a9282ff0.md>) ↔ [`MicrosoftDefenderAdvancedThreatProtection`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderadvancedthreatprotection.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "MDATP"`

#### item: [`e70fa6e0-796a-4e85-9420-98b17b0bb749`](<../../../sentinelninja/Solutions Docs/content/standalone-content-e70fa6e0-796a-4e85-9420-98b17b0bb749-a9282ff0.md>) ↔ [`MicrosoftDefenderForCloudTenantBased`](<../../../sentinelninja/Solutions Docs/connectors/microsoftdefenderforcloudtenantbased.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Azure Security Center"`

#### item: [`e70fa6e0-796a-4e85-9420-98b17b0bb749`](<../../../sentinelninja/Solutions Docs/content/standalone-content-e70fa6e0-796a-4e85-9420-98b17b0bb749-a9282ff0.md>) ↔ [`OfficeATP`](<../../../sentinelninja/Solutions Docs/connectors/officeatp.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProviderName == "OATP"`

#### item: [`e70fa6e0-796a-4e85-9420-98b17b0bb749`](<../../../sentinelninja/Solutions Docs/content/standalone-content-e70fa6e0-796a-4e85-9420-98b17b0bb749-a9282ff0.md>) ↔ [`OfficeIRM`](<../../../sentinelninja/Solutions Docs/connectors/officeirm.md>)

- **Shared tables:** (none)
- **Target predicates:**
  - *(empty)*
- **Connector predicates:**
  - `SecurityAlert.ProductName == "Microsoft 365 Insider Risk Management"`

