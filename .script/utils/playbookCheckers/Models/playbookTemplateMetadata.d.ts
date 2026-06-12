export interface PlaybookTemplateMetadata {
    title: string;
    description: string;
    prerequisites?: string | string[];
    prerequisitesDeployTemplateFile?: string;
    lastUpdateTime: string;
    entities?: string[];
    tags?: string[];
    support: {
        tier: string;
        link?: string;
    };
    author: {
        name: string;
    };
}
export declare const PlaybookMetadataSupportedEntityTypes: string[];
//# sourceMappingURL=playbookTemplateMetadata.d.ts.map