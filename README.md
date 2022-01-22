
# Welcome to my BB repository!
Hi! I go by the handle of zPrototype here on Github or 0xPrototype on Discord and Twitter. This repository is a collection of tools most of them are written by myself to help me and others who are doing bug bounties. Below is a list of the tools in this repo with a short explanation.

## Subkiller
> I would recommend using the docker version (linux/amd64 and linux/arm/v8)  
> => https://hub.docker.com/r/0xprototype/subkiller

Subkiller is basically a wrapper around a few popular tools together with a sqlite database. The main goal of this tool is to make the asset discovery process faster and easier for you. This tool was developed with the help of my good friend iCaotix who I can't thank enough for always putting up with my weird ideas and being there to help me debug or implement stuff that's just way over my head!

Subkiller requires a few tools to be pre installed on your system
- Amass => https://github.com/OWASP/Amass
- Subfinder => https://github.com/projectdiscovery/subfinder
- Findomain => https://github.com/Findomain/Findomain
- Assetfinder => https://github.com/tomnomnom/assetfinder
- GAU => https://github.com/lc/gau
- Httpx => https://github.com/projectdiscovery/httpx
> Note: It also requires the rich python library and dataclasses-json. **pip3 install rich dataclasses-json**

The usage is as follows:
> `python3 subkiller.py -d <domain> OR -f  <file with domains>`

| Flag|Function|Required?|
|:-------------:|:-------------:|:-----:|
|-f|File containing domains|yes if -d not set|
|-d|The domain you want to scan|yes if -f not set|
|-w|Enables waybackurls|Optional|
|-st|Your securitytrails api key|Optional|
|-sp|Your spyse api key|Optional|

Subkiller will output a sqlite file called `enumsubs.db` as well as five other files:
- master.txt => All found and probed subdomains with the corresponding port
- statuscodes.txt => Complete httpx output including redirect chains and site title
- 403.txt => All subdomains that returned a 403 status code. Use this file with the next tool ;)
- waybacks.txt => Containing all waybackurls for the provided target/s
- screenshot_urls.txt => Containing all urls with a 200 status code to use for screenshotting

All files are already stripped from duplicate entries.

![subkiller in action](https://i.imgur.com/138OH4X.png)

## Bypass forbidden
This tool automates the process of trying various bypasses for 403 status codes. You will find two scripts inside this directory: `bypass.sh` and `wrapper.py`. The usage is very simple you need to supply three arguments:
> `python3 wrapper.py -s bypass.sh -u <file containing 403 urls> -o <output file name>`

Optionally you can also specify the threads with `-t <number of threads>`
The output will be displayed and saved as a JSON file. If the bypass succeeds with a 200 status code you will get the curl command used for the bypass. 

## Dork all the things
This tool is used for automating the process of github dorking. I know there are already a lot of tools out there for the same purpose but I wanted to write my own. The usage is as follows:
> `python3 dork.py -d <file with dorks> -t <Name of the organization> -a <github access token>`
> Optionally you can also specify an output file with `-o <name of the output file>`

## Random stuff
This is just a bunch of random things I came up with and a lot of it is just dirty and hacky but it works somehow, for the usage I recommend looking at the code and deciding if it's something that has value for you.
