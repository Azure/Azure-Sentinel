import { PlaybookValidationError } from "../validationError";
import { ArmTemplate } from "./Models/armTemplateModels";
import { PlaybookMetadataSupportedEntityTypes, PlaybookTemplateMetadata } from "./Models/playbookTemplateMetadata";
import { isNullOrWhitespace, isPlaybookUsingGalleryMetadata } from "./playbookARMTemplateUtils";

export function validateTemplateMetadata(filePath: string, playbookARMTemplate: ArmTemplate<PlaybookTemplateMetadata>): void {
    if (!isPlaybookUsingGalleryMetadata(playbookARMTemplate)) {
        return;
    }

    validateMetadataMandatoryFieldsAreNotEmpty(filePath, playbookARMTemplate);
    validateMetdataLastUpdateTimeIsValidTimestamp(filePath, playbookARMTemplate)
    validateMetdataEntitiesContainsValidEntityTypes(filePath, playbookARMTemplate)
}

function validateMetadataMandatoryFieldsAreNotEmpty(filePath: string, playbookARMTemplate: ArmTemplate<PlaybookTemplateMetadata>): void {
    if (isNullOrWhitespace(playbookARMTemplate.metadata.title)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' missing required field 'title' in metadata.`);
    }
    if (isNullOrWhitespace(playbookARMTemplate.metadata.description)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' missing required field 'description' in metadata.`);
    }
    if (isNullOrWhitespace(playbookARMTemplate.metadata.lastUpdateTime)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' missing required field 'lastUpdateTime' in metadata.`);
    }
    if (isNullOrWhitespace(playbookARMTemplate.metadata.support?.tier)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' missing required field 'support/tier' in metadata.`);
    }
    if (isNullOrWhitespace(playbookARMTemplate.metadata.author?.name)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' missing required field 'author/name' in metadata.`);
    }
}

function validateMetdataLastUpdateTimeIsValidTimestamp(filePath: string, playbookARMTemplate: ArmTemplate<PlaybookTemplateMetadata>): void {
    let parsedLastUpdateTime: Date = new Date(playbookARMTemplate.metadata.lastUpdateTime);
    if (isNaN(parsedLastUpdateTime.getTime())) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' metadata field 'lastUpdateTime' is not a valid timestamp.`);
    }
}

function validateMetdataEntitiesContainsValidEntityTypes(filePath: string, playbookARMTemplate: ArmTemplate<PlaybookTemplateMetadata>): void {
    if (!playbookARMTemplate.metadata.entities) {
        return;
    }

    let invalidEntityTypes: string[] = playbookARMTemplate.metadata.entities
        .filter((entityType: string) => !PlaybookMetadataSupportedEntityTypes.includes(entityType.toLowerCase()));
    if (invalidEntityTypes.length > 0) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' metadata field 'entities' contains invalid entity types '${invalidEntityTypes.join("','")}'. Supported entity types: '${PlaybookMetadataSupportedEntityTypes.join("','")}'.`);
    }
}