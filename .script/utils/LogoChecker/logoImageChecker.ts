import { LogoValidationError } from "../validationError";

function isLogoSVG(LogoImagesFileNames: string) {
    return  LogoImagesFileNames.toLowerCase().endsWith('.svg');
}

export function isValidLogoImage(LogoImagesPath: string) {
      if (!isLogoSVG(LogoImagesPath)) {
          throw new LogoValidationError(`Logo must be svg files`);
      }
  };
 