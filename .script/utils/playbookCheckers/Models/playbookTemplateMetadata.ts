export interface PlaybookTemplateMetadata {
  title: string;
  description: string;
  prerequisites?: string | string[];
  prerequisitesDeployTemplateFile?: string;
  lastUpdateTime: string;
  entities?: string[];
  tags?: string[],
  support: { tier: string; link?: string };
  author: { name: string };
}

export const PlaybookMetadataSupportedEntityTypes: string[] = [
  "account",
  "host",
  "ip",
  "url",
  "azureresource",
  "cloudapplication",
  "dnsresolution",
  "file",
  "filehash",
  "hostlogonsession",
  "iotdevice",
  "malware",
  "networkconnection",
  "process",
  "registrykey",
  "registryvalue",
  "securitygroup",
  "mailbox",
  "mailcluster",
  "mailmessage",
  "submissionmail"
];