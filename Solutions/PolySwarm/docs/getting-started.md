# Getting started with PolySwarm for Microsoft Sentinel

This guide walks you through setting up PolySwarm in Microsoft Sentinel one step at a
time, with a picture of each screen. You do not need to know how Azure works to follow
it. Plan on about 30 minutes.

When you are done, Microsoft Sentinel will:

- bring in files that match your PolySwarm hunts,
- bring in the PolySwarm curated feed of known bad files, if your plan includes it,
- show what has arrived on a status page, and
- add PolySwarm's verdict to an incident when you ask it to.

If anything here does not match what you see, email customersuccess@polyswarm.io.

## What you need before you start

1. **A Microsoft Sentinel workspace**, and permission to change it. If you can open
   Microsoft Sentinel and see its settings, you probably have enough.
2. **Your PolySwarm API key.** Sign in at polyswarm.network, open your account
   settings, and copy the API key.
3. **Your PolySwarm account number**, only if you will connect the curated feed. It is
   on the same account settings page.
4. **An Azure Key Vault** you can add a secret to. A Key Vault is Azure's locked box for
   passwords and keys. If your company does not have one yet, ask whoever runs your
   Azure account to create one for you.

You will use two websites:

- the **Microsoft Defender portal**, at security.microsoft.com, for everything inside
  Microsoft Sentinel, and
- the **Azure portal**, at portal.azure.com, only for the Key Vault.

If the Defender portal says your account "needs to be added as an external user",
add your directory to the address, like this:
security.microsoft.com/?tid=yourcompany.onmicrosoft.com

## Step 1. Put your PolySwarm API key in the Key Vault

The playbooks read your key from the Key Vault, so it never sits in plain text anywhere.

1. In the Azure portal, search for **Key vaults** and open your vault.
2. On the left, choose **Objects**, then **Secrets**.
3. Choose **Generate/Import**.
4. For **Name**, type `PolySwarmApiKey`.
5. For **Secret value**, paste your PolySwarm API key.
6. Choose **Create**.

<picture><source media="(prefers-color-scheme: dark)" srcset="images/getting-started/01-key-vault-create-secret-dark.png"><img alt="The empty Create a secret form in the Azure portal" src="images/getting-started/01-key-vault-create-secret.png"></picture>

You should now see `PolySwarmApiKey` in the list, with the status **Enabled**. The key
itself is never shown.

<picture><source media="(prefers-color-scheme: dark)" srcset="images/getting-started/02-key-vault-secret-listed-dark.png"><img alt="The Key Vault secrets list showing PolySwarmApiKey as Enabled" src="images/getting-started/02-key-vault-secret-listed.png"></picture>

## Step 2. Install PolySwarm from the Content hub

1. In the Defender portal, open **Microsoft Sentinel**, then **Content management**, then
   **Content hub**.
2. Search for **PolySwarm** and select it.
3. Choose **Install**. It takes a minute or two.

This adds the two data connectors, the status workbook, three analytics rules, four
hunting queries and the playbook templates to your workspace. Nothing runs yet.

## Step 3. Connect PolySwarm Hunting

A hunt is a YARA rule you set up on polyswarm.network. Every time a file anywhere on
PolySwarm matches one of your rules, this connector brings that file's hashes into
Microsoft Sentinel. If you have no live hunts yet, the connector has nothing to bring
in, and that is normal.

1. In Microsoft Sentinel, open **Configuration**, then **Data connectors**.
2. Type **PolySwarm** in the search box. You will see two connectors.

   <picture><source media="(prefers-color-scheme: dark)" srcset="images/getting-started/04-data-connectors-polyswarm-dark.png"><img alt="The data connectors list filtered to the two PolySwarm connectors" src="images/getting-started/04-data-connectors-polyswarm.png"></picture>

3. Select **PolySwarm Hunting**, then **Open connector page**.

   <picture><source media="(prefers-color-scheme: dark)" srcset="images/getting-started/05-hunting-side-pane-dark.png"><img alt="The PolySwarm Hunting side pane" src="images/getting-started/05-hunting-side-pane.png"></picture>

4. Paste your PolySwarm API key into **PolySwarm API Key**.
5. Leave **Community** as `public`, unless your hunts run in a private community. Then
   type its short name instead (lowercase, no spaces). PolySwarm support can tell you
   the short name.
6. Leave **Polling window** at 15 minutes.
7. Select **Connect**. It can take up to a minute, and the page does not show progress
   while it works.

   <picture><source media="(prefers-color-scheme: dark)" srcset="images/getting-started/06-hunting-page-connected-dark.png"><img alt="The PolySwarm Hunting connector page after connecting" src="images/getting-started/06-hunting-page-connected.png"></picture>

When it works, the button changes to **Disconnect** and the status turns **Connected**.
The key box looks empty again afterwards. That is normal: Azure never shows a saved key.

<picture><source media="(prefers-color-scheme: dark)" srcset="images/getting-started/07-hunting-what-to-expect-dark.png"><img alt="The bottom of the connector page, explaining what to expect after you connect" src="images/getting-started/07-hunting-what-to-expect.png"></picture>

## Step 4. Connect the PolySwarm Curated Feed (if your plan includes it)

The curated feed is a large list of known bad files from PolySwarm, about 500,000
indicators a day (roughly 0.5 GB a day). Microsoft Sentinel charges for the data it
takes in, so check Microsoft Sentinel pricing before you connect it.

1. In **Data connectors**, select **PolySwarm Curated Feed**, then **Open connector
   page**.

   <picture><source media="(prefers-color-scheme: dark)" srcset="images/getting-started/08-feed-side-pane-dark.png"><img alt="The PolySwarm Curated Feed side pane, including the data volume note" src="images/getting-started/08-feed-side-pane.png"></picture>

2. Type your PolySwarm account number into **PolySwarm Account Number**.
3. Paste your API key into **PolySwarm API Key**.
4. Choose your feed in **Feed**. If you are not sure, choose **Trust Group 14-day**.
5. Leave **Polling window** at 60 minutes.
6. Select **Connect**.

<picture><source media="(prefers-color-scheme: dark)" srcset="images/getting-started/09-feed-page-connected-dark.png"><img alt="The PolySwarm Curated Feed connector page after connecting" src="images/getting-started/09-feed-page-connected.png"></picture>

After you connect, the boxes look empty and the Feed box shows its hint text instead
of your choice. That is normal.

When both connectors are connected, both show a green bar in the list:

<picture><source media="(prefers-color-scheme: dark)" srcset="images/getting-started/10-both-connectors-connected-dark.png"><img alt="Both PolySwarm connectors connected" src="images/getting-started/10-both-connectors-connected.png"></picture>

## Step 5. Check the status page

The PolySwarm status workbook shows what has arrived from each connector. It only reads
your own workspace. It never calls PolySwarm.

1. In Microsoft Sentinel, open **Threat management**, then **Workbooks**, then the
   **Templates** tab.
2. Select **PolySwarm status**, then **View template**.

   ![The PolySwarm status workbook in the Templates list](images/getting-started/11-workbook-template.png)

You will see one chart for each connector, when each last delivered something, and
tiles for sandbox results and alerts.

![The PolySwarm status workbook with data from both connectors, first part](images/getting-started/12-workbook-a.png)

![The PolySwarm status workbook, second part](images/getting-started/12-workbook-b.png)

Give it an hour after connecting. A tile that says nothing has arrived yet is normal on
a new install; each one fills as its source starts producing data.

## Step 6. Turn on the analytics rules

The three PolySwarm analytics rules ship switched off, so they never surprise you with
alerts.

1. In Microsoft Sentinel, open **Configuration**, then **Analytics**, then the
   **Rule templates** tab.
2. Search for **PolySwarm**.

   ![The PolySwarm analytics rule templates](images/getting-started/13-analytics-rule-templates.png)

3. Select a rule, then **Create rule**, and go through the pages with the defaults.

   ![A PolySwarm rule template with its Create rule button](images/getting-started/14-analytics-rule-details.png)

What each rule does:

- **PolySwarm malicious file observed** raises an alert when a file PolySwarm knows is
  bad shows up in your device or security logs.
- **PolySwarm high-confidence hunt hit** raises an alert when one of your hunts matches
  a file PolySwarm is very sure about.
- **PolySwarm sandbox detonation malicious** raises an alert when a PolySwarm sandbox
  playbook finds a file or link is malicious.

When a rule fires, the alert becomes an incident. If your workspace is onboarded to the
Microsoft Defender portal, PolySwarm incidents appear there too.

![A PolySwarm incident in the Microsoft Defender portal](images/getting-started/21-defender-incident.png)

## Step 7. Add PolySwarm's verdict to incidents

Playbooks are small automations that run on an incident. The simplest one to start with
is **PolySwarm-Enrich-FileHash-IncidentTriggered**: it looks up every file hash on an
incident and adds PolySwarm's verdict as a comment.

1. In the **Content hub**, open **PolySwarm**, then **Manage**.
2. Find **PolySwarm-Enrich-FileHash-IncidentTriggered**, select it, and choose
   **Configuration**. This takes you to the playbook template.
3. Choose **Create playbook**. On the first page, pick your resource group and region.
   Leave the playbook name as it is.

   ![The first page of the Create playbook wizard](images/getting-started/15-create-playbook.png)

4. On the **Parameters** page, type the name of your Key Vault (the vault from step 1).
   Leave everything else as it is.
5. Go through the remaining pages and choose **Create**.
6. Give the new playbook permission to read the key and to comment on incidents. Your
   Azure administrator can follow the "Grant managed identity role assignments" section
   of the deployment guide (docs/deployment.md).

Then tell Microsoft Sentinel when to run it:

1. Open **Configuration**, then **Automation**, then **Create**, then **Automation rule**.
2. Under **Actions**, choose **Run playbook** and pick the PolySwarm playbook.
3. Save.

![The automation rule form with the PolySwarm playbook selected](images/getting-started/16-automation-rule.png)

You can also run a playbook by hand on one incident: in the **Incidents** list, select
the incident (do not open it), choose **Run Playbook** in the pane on the right, and
choose **Run playbook** next to the PolySwarm playbook you want.

![Running a PolySwarm playbook by hand on an incident](images/getting-started/17-run-playbook-on-incident.png)

## Step 8. See it work

When the playbook runs, PolySwarm's answer appears on the incident. Open the incident,
select the **Activities** tab, and select the PolySwarm comment to read it in full. (The
short list of activities runs each comment together on one line; the full view keeps
its lines.)

![A PolySwarm enrichment comment on an incident](images/getting-started/18-incident-comment.png)

The comment gives the verdict, how many scanning engines called the file malicious,
the malware family when known, and a link to the full PolySwarm report.

## Detonate a link in the PolySwarm sandbox

The sandbox playbook runs each link on an incident in a PolySwarm sandbox and reports
what happened. Create it the same way as the enrichment playbook.

1. In the **Content hub**, open **PolySwarm**, then **Manage**.
2. Find **PolySwarm-Sandbox-Url-IncidentTriggered**, select it, and choose
   **Configuration**, then **Playbook templates**, then **Create playbook**.
3. On the **Parameters** page, fill in three values:

   - **WorkspaceName**: the name of your Log Analytics workspace, which must be in the
     same resource group as the playbook.
   - **Community**: the short name of your private PolySwarm community. The playbook
     will not submit to the public community unless you also set
     **AllowPublicCommunity** to true.
   - **KeyVaultName**: the name of your Key Vault (the vault from step 1).

   ![The Parameters page of the sandbox playbook](images/getting-started/19-sandbox-playbook-parameters.png)

4. Go through the remaining pages and choose **Create**. The first deployment also
   creates the table the sandbox results are stored in, and the collection resources
   that feed it. You do not need to set those up yourself.

Then grant the roles and attach it to an incident, as in the steps above for the
enrichment playbook. Detonation is metered and takes minutes, so consider running it by
hand on an incident rather than on every one.

When it finishes, the incident gets a comment with the verdict and the sandbox score out
of 10, the sandbox provider and virtual machine, the malware family and MITRE ATT&CK
techniques when the sandbox finds them, the community, the task id, and a link to the
PolySwarm report. Each result is also written to the sandbox results table, which feeds
the sandbox detonation rule and the status workbook.

## Check your quota

The **PolySwarm-CheckQuota** playbook adds a comment to an incident showing how much of
your PolySwarm quota you have used. Create it from its template the same way, then run
it by hand on an incident.

![A PolySwarm quota check comment on an incident](images/getting-started/20-quota-comment.png)

This lab plan has no limits, so it shows unmetered. On a metered plan the comment shows
used, limit and remaining for API calls and sandbox detonations, and a warning when
either runs low.

## Other playbooks

The solution includes more playbooks: lookups for links, IP addresses and domains, and
sandbox playbooks that run a link or a file in PolySwarm's sandbox and report what it
did. Each one has its own page in the Playbooks folder explaining what it needs.

Two playbooks are in **preview**: the Defender for Endpoint file playbook and the
Outlook attachment playbook. They work in our tests but have not yet been tried on a
live Defender for Endpoint tenant or Exchange Online mailbox. If you try one, please
tell us how it went at customersuccess@polyswarm.io.

## If something goes wrong

- **The connector will not connect.** Check that you pasted the whole API key, and that
  the Community is `public` or the short name of a private community, not its display
  name.
- **Connected, but no data after an hour.** For PolySwarm Hunting, check that you have
  at least one live hunt on polyswarm.network. For the curated feed, check that your
  plan includes the feed you chose.
- **A playbook does nothing.** Open the playbook in the Azure portal and look at its
  **Runs history**. A failed Key Vault step almost always means the playbook has not
  been given permission to read the key yet (step 7).
- **Anything else.** Email customersuccess@polyswarm.io.
