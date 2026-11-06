TANBIR YT — WEB PANEL CONNECTED BUILD

Start locally:
  pip install -r requirements.txt
  python app.py

Open the local URL printed in the terminal, sign in, then enter your account UID,
password, nickname and region in the panel. Press Save & Start to launch the bot
worker using the bot engine included in this package.

Default admin login from the inherited panel:
  username: tanvirtcp
  password: tanvirtcp

IMPORTANT: Change the default admin password before exposing this panel publicly.
Set ADMIN_PASS in the environment. For hosted deployment, configure a persistent
DATA_DIR volume so users and bot configuration survive redeploys.

The web interface files (templates/ and static/) come from the second archive.
The bot engine modules come from the first archive. The old hard-coded credential
launcher was intentionally removed; account credentials are entered through the
website and stored in the panel's bot configuration file.
