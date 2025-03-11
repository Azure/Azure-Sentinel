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
            { Tactic.InitialAccess, new List<string>() { "T1189", "T1190", "T1133", "T1200", "T1566", "T1091", "T1195", "T1199", "T1078", "T0817", "T0819", "T0866", "T0822", "T0883", "T0886", "T0847", "T0848", "T0865", "T0862", "T0864", "T0860", "T1456", "T1461", "T1458", "T1474" } },
            { Tactic.Persistence, new List<string>() { "T1098", "T1197", "T1547", "T1037", "T1176", "T1554", "T1136", "T1543", "T1546", "T1133", "T1574", "T1525", "T1556", "T1137", "T1542", "T1053", "T1505", "T1205", "T1078", "T1398", "T1577", "T1645", "T1624", "T1541", "T1625", "T1603", "T0891", "T0889", "T0839", "T0873", "T0857", "T0859" } },
            { Tactic.PrivilegeEscalation, new List<string>() { "T1548", "T1134", "T1547", "T1037", "T1543", "T1484", "T1611", "T1546", "T1068", "T1574", "T1055", "T1053", "T1078", "T1626", "T1404", "T1631", "T0890", "T0874" } },
            { Tactic.DefenseEvasion, new List<string>() { "T1548", "T1134", "T1197", "T1612", "T1622", "T1140", "T1610", "T1006", "T1484", "T1480", "T1211", "T1222", "T1564", "T1574", "T1562", "T1070", "T1202", "T1036", "T1556", "T1578", "T1112", "T1601", "T1599", "T1027", "T1647", "T1542", "T1055", "T1620", "T1207", "T1014", "T1553", "T1218", "T1216", "T1221", "T1205", "T1127", "T1535", "T1550", "T1078", "T1497", "T1600", "T1220", "T1407", "T1627", "T1541", "T1628", "T1617", "T1629", "T1630", "T1516", "T1575", "T1406", "T1631", "T1604", "T1632", "T1633", "T0858", "T0820", "T0872", "T0849", "T0851", "T0856" } },
            { Tactic.CredentialAccess, new List<string>() { "T1557", "T1110", "T1555", "T1212", "T1187", "T1606", "T1056", "T1556", "T1111", "T1621", "T1040", "T1003", "T1528", "T1539", "T1649", "T1558", "T1552", "T1517", "T1414", "T1634", "T1417", "T1635" } },
            { Tactic.Discovery, new List<string>() { "T1087", "T1010", "T1217", "T1580", "T1538", "T1526", "T1619", "T1613", "T1622", "T1652", "T1482", "T1083", "T1615", "T1046", "T1135", "T1040", "T1201", "T1120", "T1069", "T1057", "T1012", "T1018", "T1518", "T1082", "T1614", "T1016", "T1049", "T1033", "T1007", "T1124", "T1497", "T1420", "T1430", "T1423", "T1424", "T1418", "T1426", "T1422", "T1421", "T0840", "T0842", "T0846", "T0888", "T0887" } },
            { Tactic.LateralMovement, new List<string>() { "T1210", "T1534", "T1570", "T1563", "T1021", "T1091", "T1072", "T1080", "T1550", "T1428", "T1458", "T0812", "T0866", "T0891", "T0867", "T0843", "T0886", "T0859" } },
            { Tactic.Execution, new List<string>() { "T1651", "T1059", "T1609", "T1610", "T1203", "T1559", "T1106", "T1053", "T1648", "T1129", "T1072", "T1569", "T1204", "T1047", "T1623", "T1575", "T1603", "T0858", "T0807", "T0871", "T0823", "T0874", "T0821", "T0834", "T0853", "T0863" } },
            { Tactic.Collection, new List<string>() { "T1557", "T1560", "T1123", "T1119", "T1185", "T1115", "T1074", "T1530", "T1602", "T1213", "T1005", "T1039", "T1025", "T1114", "T1056", "T1113", "T1125", "T1517", "T1638", "T1532", "T1429", "T1616", "T1414", "T1533", "T1417", "T1430", "T1636", "T1513", "T1409", "T1512", "T0830", "T0802", "T0811", "T0893", "T0868", "T0877", "T0801", "T0861", "T0845", "T0852", "T0887" } },
            { Tactic.Exfiltration, new List<string>() { "T1020", "T1030", "T1048", "T1041", "T1011", "T1052", "T1567", "T1029", "T1537", "T1639", "T1646" } },
            { Tactic.CommandAndControl, new List<string>() { "T1071", "T1092", "T1132", "T1001", "T1568", "T1573", "T1008", "T1105", "T1104", "T1095", "T1571", "T1572", "T1090", "T1219", "T1205", "T1102", "T1437", "T1616", "T1637", "T1521", "T1544", "T1509", "T1644", "T1481", "T0885", "T0884", "T0869" } },
            { Tactic.Impact, new List<string>() { "T1531", "T1485", "T1486", "T1565", "T1491", "T1561", "T1499", "T1495", "T1490", "T1498", "T1496", "T1489", "T1529", "T1640", "T1616", "T1471", "T1641", "T1642", "T1643", "T1516", "T1464", "T1582", "T0879", "T0813", "T0815", "T0826", "T0827", "T0828", "T0837", "T0880", "T0829", "T0831", "T0832", "T0882" } },
            { Tactic.ImpairProcessControl, new List<string>() { "T0806","T0836","T0839","T0856","T0855"} },
            { Tactic.InhibitResponseFunction, new List<string>() { "T0800", "T0878", "T0803", "T0804", "T0805", "T0892", "T0809", "T0814", "T0816", "T0835", "T0838", "T0851", "T0881", "T0857" } },
            { Tactic.Reconnaissance, new List<string>() { "T1595", "T1592", "T1589", "T1590", "T1591", "T1598", "T1597", "T1596", "T1593", "T1594" } },
            { Tactic.ResourceDevelopment, new List<string>() { "T1650", "T1583", "T1586", "T1584", "T1587", "T1585", "T1588", "T1608" } }
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
