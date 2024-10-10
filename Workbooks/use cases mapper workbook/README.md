# Use Cases Mapper  - Sentinel workbook & watchlists

## Intro
This Sentinel workbook and the complementary resources (watchlists) are used to map common **Use Cases** to the Mitre ATT&CK framework, i.e. the tactics and techniques listed there.
This gives you a quick overview of the analysis options available in Sentinel (e.g. Analytic Rules & Hunting Queries) according to these **Use Cases**.

The identified **Use Cases** in this context are:

- Credential Exploitation
- Lateral Movement
- Rapid Encryption
- Command and Control Communication
- Insider Risk
- Anomalous Privilege Escalation​
- Third-Party Abuses
- Overexposure
- Data Exfiltration
- Mobile Data Security
- Communication Abuse​
- Web Application Abuse

> ⚠️ These can change over time, as attack & defense strategies and techniques are constantly changing as well.

In order to be able to adapt this information to your own needs, the option of reducing the results to selected **Data Sources** (Content Hub solutions) has also been implemented.

---

## How to use
The available results are presented by selecting the right **Use Cases** and the corresponding **Data Sources**.
There are the appropriate selection options for this (see pictures following :point_down:).

mariocuomo/Azure-Sentinel/Workbooks/Images/Preview/useCaseMapper1.png
<div style="text-align: right"><img src="https://github.com/mariocuomo/Use-Cases-Mapper/blob/main/img/img1.png" width="290" /><img src="https://github.com/mariocuomo/Use-Cases-Mapper/blob/main/img/img2.png" width="350" /></div>

The expected results:

- Analytics Rules (+ graphical representation of the results in the form of 2 pie charts)
- Hunting Queries (+ graphical representation of the results in the form of 2 pie charts)

---

## The structure 

At the top of the workbook you will find a brief description of how to use the workbook, followed by the associated resources. Finally, you will be taken to the selection options (as already mentioned above :point_up: under **How to use**).

---

## How to deploy

Below you can find a button to start the process (custom deployment).

The necessary information to be inserted here are:

- a Subscription (selection possible via dropdown and selection depending on the logged-in tenant)
- a Resource Rroup (please select the resource group in which the Sentinel Workspace was also deployed)
- a Region
- a Workspace Name

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fgist.githubusercontent.com%2Fmariocuomo%2Ffc7458fd2328c41275b24570e50304ee%2Fraw%2F90ad3a7c187ad2eaaa195f9c7a77766827ea97a1%2Fdeploy.json)

> ⚠️ After deployment, it may take a few minutes (10-15 min) until the necessary values from the watchlists are available in the workbook.

---

<div align=center>
  <img src="https://github.com/mariocuomo/Use-Cases-Mapper/blob/main/img/img3.png"/ width="700">
</div>

---

Created by: Mario Cuomo, Thomas Bruendl and Nikolay Salnikov




