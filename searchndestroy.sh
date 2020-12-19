domainlist=$1
host=$2
outfile=$3

cat $domainlist | sed 's~http[s]*://~~g' | grep $host | rev | cut -d. -f 1,2,3 | rev | sort -u \
| xargs -n 1 -I{} assetfinder --subs-only {} | httprobe | sort -u | tee $outfile
