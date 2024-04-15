import { StringMap } from "../playbookARMTemplateUtils";

export interface ArmTemplate<TMetadata> {
  metadata: TMetadata;
  parameters: StringMap<ArmTemplateParameter>;
  variables: StringMap<string>;
  resources: ArmTemplateResource[];
}

export interface ArmTemplateResource {
  type: string;
  kind?: string;
  apiVersion: string;
  name: string;
  location: string;
  properties: any;
  tags?: StringMap<string>;
  dependsOn?: string[];
  resources?: ArmTemplateResource[];
}

export interface ArmTemplateParameter {
  type: string;
  metadata?: { description?: string };
  defaultValue?: any;
  minLength?: number;
  maxLength?: number;
  minValue?: number;
  maxValue?: number;
}