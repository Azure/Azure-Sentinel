# Deploy a Function App for collecting Zoom data into Azure Sentinel
This function app will be used to get the zoom reports.

## Configure your Zoom API app.
You also need to configure your Zoom account. To do this go to https://marketplace.zoom.us/ and log in with a user who has admin access to your Zoom account i.e. by signin to zoom with your credentials i.e. username/password & zoom verfication code.
1. Select ‘Develop’ in the top right hand corner and click ‘Build App’.
2. Select ‘Server to Server Oauth App’ as your app type.
3. Give your app a name.
4. Fill out the required Basic Information and click continue.
5. App credentials: View your account ID, client ID and client secret. You'll use these credentials to authenticate with Zoom.so copy these credentials
6. Under the Feature Tab enable the ‘Event Subscriptions’ toggle ,Please make sure to disble it.
7. Scopes: Choose Add Scopes to search for and add all scope for  Report, Marketplace, Billing, Meeting and User.
8. Activation: Your app should be activated. If you see errors that prevent activation, please address them. You will not be able to generate an access token to make API calls unless your app is activated.

Once you have done the above steps
1. Get the App credentials from step 5 i.e. account ID, client ID and client secret use it in during deployment.

If you run into issues while creating for [Server to Server Oauth App](https://developers.zoom.us/docs/internal-apps/create/) .