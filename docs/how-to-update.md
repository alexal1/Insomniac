[< Back to the documentation](/#)

## How to update?
Depends on the way you've installed Insomniac.

##### 1. Installed via _pip_ (`python3 -m pip install insomniac`) => just run `python3 -m pip install --upgrade insomniac`
_Doesn't work for you? If it fails during the update, check that you have the latest pip version: `python -m pip install --upgrade pip`. If update finishes successfully but insomniac version remains the same, check that you don't have insomniac source code in the same folder._

##### 2. Installed via _git clone_ (`git clone https://github.com/alexal1/Insomniac.git`) => run `git pull` to get latest changes

##### 3. Installed via manual code download => delete folder with the source code and download the latest release from https://github.com/alexal1/Insomniac/releases

_Note that you may want to keep all data the bot saved for you (such as usernames it followed, scraped users, etc.). Then just copy "insomniac.db" file to another place before deleting the folder and then put it back._ 

### How to get a specific version?

Again, depends on the way you've installed Insomniac. Say, you want to get `v3.7.25`:

##### 1. Installed via _pip_ (`python3 -m pip install insomniac`) => `python3 -m pip install --force-reinstall insomniac==3.7.25`

##### 2. Installed via _git clone_ (`git clone https://github.com/alexal1/Insomniac.git`) => `git fetch --all --tags && git checkout tags/v3.7.25 -b v3.7.25-branch`

##### 3. Installed via manual code download => delete folder with the source code and download a desired release from https://github.com/alexal1/Insomniac/releases
