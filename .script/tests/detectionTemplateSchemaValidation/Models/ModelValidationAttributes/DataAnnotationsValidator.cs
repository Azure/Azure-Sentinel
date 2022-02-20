using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Reflection;

namespace Microsoft.Azure.Sentinel.ApiContracts.ModelValidation
{
    public class DataAnnotationsValidator
    {
        public static List<ValidationResult> ValidateObjectRecursive<T>(T obj)
        {
            var validationResults = new List<ValidationResult>();
            TryValidateObjectRecursive(obj, validationResults, new HashSet<object>());

            return validationResults;
        }

        public static void ThrowExceptionIfResultsInvalid(List<ValidationResult> validationResults)
        {
            var results = new List<string>();
            foreach (ValidationResult validationResult in validationResults)
            {
                if(!String.IsNullOrEmpty(validationResult.ErrorMessage))
                results.Add(validationResult.ErrorMessage);
            }
            if (results.Count > 0)
            {
                throw new Exception($"Invalid data model. {String.Join(", ", results.Select(error => $"{error}"))}");
            }
        }

        private static bool TryValidateObject(object obj, ICollection<ValidationResult> results)
        {
            return Validator.TryValidateObject(obj, new ValidationContext(obj), results, true);
        }

        private static bool TryValidateObjectRecursive<T>(T obj, List<ValidationResult> results, ISet<object> validatedObjects)
        {
            //short-circuit to avoid infinite loops on cyclical object graphs
            if (obj == null || validatedObjects.Contains(obj))
            {
                return true;
            }

            validatedObjects.Add(obj);
            bool result = TryValidateObject(obj, results);

            var properties = obj.GetType().GetProperties().Where(prop => prop.CanRead && prop.GetIndexParameters().Length == 0).ToList();

            foreach (var property in properties)
            {
                if (property.PropertyType == typeof(string) || property.PropertyType.IsValueType)
                {
                    continue;
                }

                var value = property.GetValue(obj);
                if (value == null)
                {
                    continue;
                }

                var asEnumerable = value as IEnumerable;
                if (asEnumerable != null)
                {
                    foreach (var enumObj in asEnumerable)
                    {
                        if (enumObj != null)
                        {
                            result = TryValidateObjectRecursiveAndPopulateValidationResults(enumObj, validatedObjects, results, property, result);
                        }
                    }
                }
                else
                {
                    result = TryValidateObjectRecursiveAndPopulateValidationResults(value, validatedObjects, results, property, result);
                }
            }

            return result;
        }

        private static bool TryValidateObjectRecursiveAndPopulateValidationResults(object obj, ISet<object> validatedObjects, List<ValidationResult> results,
                                                                                    PropertyInfo property, bool result)
        {
            var nestedResults = new List<ValidationResult>();
            if (!TryValidateObjectRecursive(obj, nestedResults, validatedObjects))
            {
                result = false;
                foreach (var validationResult in nestedResults)
                {
                    PropertyInfo property1 = property;
                    results.Add(new ValidationResult(validationResult.ErrorMessage, validationResult.MemberNames.Select(x => property1.Name + '.' + x)));
                }
            }

            return result;
        }
    }
}
