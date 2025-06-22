# It's a BeReal clone

So for a couple of years I really enjoyed the daily reminder to take a photo from the app "BeReal". That being said, the 
app was a photo-hosting social network, so you know eventually the ads would arrive. 

The main thing I wanted was just a daily reminder to take a photo, so I threw together a quick script that's a little 
harder to ignore than an app notification.

So once a day during a set window, this script will start sending emails every 5 minutes.

## Responding

This script includes a fastAPI endpoint for marking the photos as taken, but worth noting that I have an iOS shortcut 
which checks if I've taken a photo today and then sends the API response. It's also set to run automatically when I 
receive an email from this service. That shortcut is not currently included in this repo (I'm not sure if they're 
packagable?), but it's pretty light. 