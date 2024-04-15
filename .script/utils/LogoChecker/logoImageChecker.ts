import fs from "fs";
import { LogoValidationError } from "../validationError";
function isLogoSVG(LogoImagesFileNames: string) {
    return  LogoImagesFileNames.toLowerCase().endsWith('.svg');
}
function isLogoSizeValid(filePath: string)
{
    var result= true;
    fs.stat(filePath, (error, stats) => { 
        if (error) { 
          result=false; 
        } 
        else { 
          var size= stats.size/1000;
          console.log(size);
          if(size<=5)
          {
              result=true;
          }
          else{
              result=false;
          }
        } 
      });
      
      return result;
}
export function isValidLogoImage(LogoImagesPath: string) {
      if (!isLogoSVG(LogoImagesPath)) {
          throw new LogoValidationError(`Logo must be svg files`);
      }
      if(!isLogoSizeValid(LogoImagesPath))
      {
        throw new LogoValidationError(`Logo size size is  more then 5 kb`);
      }
  };
 