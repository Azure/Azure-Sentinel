using Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsTemplatesService.Interface.Model;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text.RegularExpressions;

namespace Microsoft.Azure.Sentinel.Analytics.Management.AnalyticsManagement.Contracts.Model.ARM.ModelValidation
{
    public static class KillChainTechniquesHelper
    {
        /// <summary>
        /// The current mapping between the known technique ids and <see cref="Tactic"/>.
        /// Mapping based on the MITRE att@ck enterprise matrix model (https://attack.mitre.org/matrices/enterprise/).
        /// </summary>
        private static readonly Dictionary<Tactic, List<string>> _techniquesToIntentMapping = new Dictionary<Tactic, List<string>>()
        {
            { Tactic.Unknown, new List<string>() { } },
            { Tactic.PreAttack, new List<string>() { "T1583", "T1584", "T1585", "T1586", "T1587", "T1588", "T1589", "T1590", "T1591", "T1592", "T1593", "T1594", "T1595", "T1596", "T1597", "T1598" } },
            { Tactic.InitialAccess, new List<string>() { "T1078", "T1091", "T1133", "T1195", "T1199", "T1200", "T1189", "T1190", "T1566", "T0810", "T0817", "T0818", "T0819", "T0822", "T0883", "T0847", "T0848", "T0865", "T0862", "T0860", "T0866", "T0886" } },
            { Tactic.Persistence, new List<string>() { "T1037", "T1053", "T1078", "T1098", "T1136", "T1137", "T1176", "T1197", "T1133", "T1205", "T1505", "T1525", "T1542", "T1543", "T1546", "T1547", "T1554", "T1574", "T0889", "T0839", "T0873", "T0857", "T0859", "T1556" } },
            { Tactic.PrivilegeEscalation, new List<string>() { "T1037", "T1053", "T1055", "T1068", "T1078", "T1134", "T1484", "T1543", "T1546", "T1547", "T1548", "T1574", "T0874", "T0890", "T1611" } },
            { Tactic.DefenseEvasion, new List<string>() { "T1006", "T1014", "T1027", "T1036", "T1055", "T1070", "T1078", "T1112", "T1127", "T1134", "T1140", "T1197", "T1202", "T1205", "T1207", "T1211", "T1216", "T1218", "T1220", "T1221", "T1222", "T1480", "T1484", "T1497", "T1535", "T1542", "T1548", "T1550", "T1553", "T1556", "T1562", "T1564", "T1574", "T1578", "T1599", "T1600", "T1601", "T0858", "T0820", "T0872", "T0849", "T0851", "T0856", "T1612", "T1610" } },
            { Tactic.CredentialAccess, new List<string>() { "T1003", "T1040", "T1056", "T1110", "T1111", "T1187", "T1212", "T1528", "T1539", "T1552", "T1555", "T1556", "T1557", "T1558", "T1606", "T1613", "T1614", "T1606", "T1613", "T1614" ,"T1621"} },
            { Tactic.Discovery, new List<string>() { "T1007", "T1010", "T1012", "T1016", "T1018", "T1033", "T1040", "T1046", "T1049", "T1057", "T1069", "T1082", "T1083", "T1087", "T1120", "T1124", "T1135", "T1201", "T1217", "T1482", "T1497", "T1518", "T1526", "T1538", "T1580", "T0840", "T0842", "T0846", "T0888", "T0887" } },
            { Tactic.LateralMovement, new List<string>() { "T1021", "T1072", "T1080", "T1091", "T1210", "T1534", "T1550", "T1563", "T1570", "T0866", "T0886", "T0859", "T0812", "T0867", "T0843" } },
            { Tactic.Execution, new List<string>() { "T1047", "T1053", "T1059", "T1072", "T1106", "T1129", "T1203", "T1204", "T1559", "T1569", "T0807", "T0871", "T0823", "T0821", "T0834", "T0853", "T0863", "T0874", "T0858" } },
            { Tactic.Collection, new List<string>() { "T1005", "T1025", "T1039", "T1056", "T1074", "T1113", "T1114", "T1115", "T1119", "T1123", "T1125", "T1185", "T1213", "T1530", "T1557", "T1560", "T1602", "T0887", "T0802", "T0811", "T0868", "T0877", "T0830", "T0801", "T0861", "T0845", "T0852", "T1609", "T1610" } },
            { Tactic.Exfiltration, new List<string>() { "T1011", "T1020", "T1029", "T1030", "T1041", "T1048", "T1052", "T1537", "T1567" } },
            { Tactic.CommandAndControl, new List<string>() { "T1001", "T1008", "T1071", "T1090", "T1092", "T1095", "T1102", "T1104", "T1105", "T1132", "T1205", "T1219", "T1568", "T1571", "T1572", "T1573", "T0885", "T0884", "T0869" } },
            { Tactic.Impact, new List<string>() { "T1485", "T1486", "T1489", "T1490", "T1491", "T1495", "T1496", "T1498", "T1499", "T1529", "T1531", "T1561", "T1565", "T0879", "T0813", "T0815", "T0826", "T0827", "T0828", "T0837", "T0880", "T0829", "T0831", "T0832", "T0882" } },
            { Tactic.ImpairProcessControl, new List<string>() { "T806","T836","T839","T856","T855", "T0839", "T0856", "T0806", "T0836", "T0855" } },
            { Tactic.InhibitResponseFunction, new List<string>() { "T800", "T878", "T803", "T804", "T805", "T809", "T814", "T816", "T835", "T838", "T851", "T881", "T857", "T0857", "T0851", "T0800", "T0878", "T0803", "T0804", "T0805", "T0809", "T0814", "T0816", "T0835", "T0838", "T0881" } },
            { Tactic.Reconnaissance, new List<string>() { "T1595", "T1592", "T1589", "T1590", "T1591", "T1598", "T1597", "T1596", "T1593", "T1594" } },
            { Tactic.ResourceDevelopment, new List<string>() { "T1583", "T1586", "T1584", "T1587", "T1585", "T1588", "T1608" } }
        };

        /// <summary>
        /// Method used to get the corresponding <see cref="Tactic"/> for the given technique id according to a static mapping.
        /// The mapping is based on  the MITRE att@ck enterprise matrix model (https://attack.mitre.org/matrices/enterprise/).
        /// </summary>
        /// <param name="technique">The id of the technique.</param>
        /// <returns>All tactics corresponding to the given technique as a <see cref="Tactic"/></returns>
        public static Tactic GetCorrespondingTactics(string technique)
        {
            var result = new Tactic();

            foreach (var key in _techniquesToIntentMapping.Keys)
            {
                if (_techniquesToIntentMapping[key].Contains(technique))
                {
                    result |= key;
                }
            }

            return result;
        }
        
        public static string ExtractTechnique(this string subTechnique)
        {
            return subTechnique.Split('.').First();
        }

    }
}
