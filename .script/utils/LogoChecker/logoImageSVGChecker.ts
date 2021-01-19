import { LogoValidationError } from "../validationError";

export function isValidLogoImageSVGContent(LogoImagesContent: string) {
  if (isLogoSVGHasillegalAttribute(LogoImagesContent)) {
      throw new LogoValidationError(`Ensure raw file of logo does not have any style or ClS formats`);
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
  if(!isLogoSVGHasValidId(LogoImagesContent)){
    throw new LogoValidationError(`Id should be GUID format and uniquely identifiable.`);
  }
};

function isLogoSVGHasillegalAttribute(LogoImagesContent: string) {
 let illegalAttribute = ["style=", "cls="]
 var result=false;
 illegalAttribute.forEach(illegalAttribute=>{
   if(LogoImagesContent.includes(illegalAttribute))
   {
          result=true
   }
 })
    return result;
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

function isValidGuid(guidId: string): boolean {
      const validRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
     return validRegex.test(guidId);
  }
 
 function isLogoSVGHasValidId(LogoImagesContent: string)
 {
  var regex = /id=\"/g;
  var instr = LogoImagesContent;
  var current;
  var AllGuid = [];
  var result=true;
  while ((current = regex.exec(instr)) != null)
  {
    var value= instr.substring(current.index+4,current.index+4+36);
  
    AllGuid.push(value);
    if(!isValidGuid(value))
    {
      result= false
      break;
    }
  }
  if(AllGuid.length>0)
  {
  const setArray = new Set(AllGuid);
  if(AllGuid.length !== setArray.size)
  {
    result= false;
  } 
  }
  return result;
 }


 