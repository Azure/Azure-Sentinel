# Upgrading to the multi-host (multi-domain) Auth0 Logs connector

Starting with solution version **3.2.0**, the **Auth0 Logs (via Codeless Connector Framework)** data connector supports collecting logs from **multiple Auth0 hosts** from a single connector. Each ingested record is tagged with an **Auth0Domain** column so you can tell the hosts apart (for example: `Auth0Logs_CL | summarize count() by Auth0Domain`).

**What happens when you upgrade:**

1. Update the **Auth0** solution to 3.2.0 (or later) from Content Hub. Your existing Auth0 log collection keeps running during and after the update — no data is lost.
2. Upgrading the solution only refreshes the connector *definition*. It does **not** change the data collection rule or poller already running in your workspace, so the new multi-host experience and the `Auth0Domain` column are **not** applied automatically.
3. To enable multi-host collection, open **Microsoft Sentinel > Data connectors > Auth0 Logs (via Codeless Connector Framework)**, then **reconnect**:
   - In the connection grid, add each Auth0 host as its own connection using **Add Auth0 host**, providing that host's **Domain**, **Client ID**, and **Client Secret**.
   - Reconnecting re-provisions the data collection rule (now including the `Auth0Domain` column) and starts a separate poller per host.
4. New host connections take a cycle or two to warm up (initial token fetch, first backfill window, then ingestion), so a newly added host may lag the first one before data appears.

> **Note:** Records collected before the upgrade remain in `Auth0Logs_CL` with an empty `Auth0Domain`. Records collected after you reconnect a host are tagged with that host's domain.

---

# Steps to Configure Auth0 app
The following are steps to be followed in Auth0 App.

1. Please go to applications and select application from auth0 side, Please find below screen shot for reference :-

![](Images/Applications.png?raw=true)

2. Click on settings of the App and note down the credentials
<br>***a. Copy the domain
    b. Get the client id value
    c. Get the client secret***<br>

3. Under Application properties --> Select Application type as Machine to Machine. Please find below screen shot for reference :-

![](Images/ApplicationProperties.png?raw=true)

4. Under credentials tab --> Select client secret (Post). Please find below screen shot for reference :-

![](Images/Credentials.png?raw=true)

5. Under API tab, please make sure Authorized to scopes, Please find below screen shot for reference :-

![](Images/API.png?raw=true)

6. Please make sure the domain value under settings --> Environment Variables, please refer below screen shot for reference and other values are entered from the above step copied values and Domain should be  starts with https://,then click on Apply  and restart function app

![](Images/functionappvalues.png?raw=true)

