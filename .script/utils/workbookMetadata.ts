export interface WorkbookMetadata {
  workbookKey: string;
  logoFileName: string; // svg type
  description: string;
  dataTypesDependencies: string[];
  dataConnectorsDependencies: string[];
  previewImagesFileNames: string[]; // png type
  version: string;
  title: string;
  templateRelativePath: string;
  subtitle: string;
  provider: string;
  featureFlag?: string;
}
