import { LogoValidationError } from "../validationError";

function isLogoSVGHasStyleTag(LogoImagesContent: string) {
    return  LogoImagesContent.includes("style=");
}
function isLogoSVGHasxmlnsxlink(LogoImagesContent: string) {
    return  LogoImagesContent.includes("xmlns:xlink");
}
function isLogoSVGHasdataname(LogoImagesContent: string) {
    return  LogoImagesContent.includes("data-name");
}
function isLogoSVGHasxlinkhref(LogoImagesContent: string) {
    return  LogoImagesContent.includes("xlink:href");
}
function isLogoSVGHasTitleTag(LogoImagesContent: string) {
    return  LogoImagesContent.includes("<title>");
}
function isLogoSVGHasPNGEmbed(LogoImagesContent: string) {
    if(LogoImagesContent.includes("<image"))
    {
        return LogoImagesContent.includes(".png");
    }
      return false;
}
// function isValid(str: string): boolean {
//     const validRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
//     return validRegex.test(str);
// }

// function isLogoSVGHasValidId(LogoImagesContent: string)
// {

// }

export function isValidLogoImageSVGContent(LogoImagesContent: string) {
      if (isLogoSVGHasStyleTag(LogoImagesContent)) {
          throw new LogoValidationError(`Ensure raw file of logo does not have any style formats`);
      }
      if (isLogoSVGHasxmlnsxlink(LogoImagesContent)) {
        throw new LogoValidationError(`Ensure raw file of logo does not have any xmlns:xlink`);
      }
      if (isLogoSVGHasdataname(LogoImagesContent)) {
        throw new LogoValidationError(`Ensure raw file of logo does not have any data-name`);
      }
      if (isLogoSVGHasxlinkhref(LogoImagesContent)) {
        throw new LogoValidationError(`Ensure raw file of logo does not have any xlink:href`);
      }
      if (isLogoSVGHasTitleTag(LogoImagesContent)) {
        throw new LogoValidationError(`Ensure raw file of logo does not have title tag`);
      }
      if (isLogoSVGHasPNGEmbed(LogoImagesContent)) {
        throw new LogoValidationError(`Ensure raw file of logo does not have embedded png formats`);
      }
  };
 