#!/bin/bash
IP='172.18.79.139'
dir=`pwd`
log=$dir/log.txt
rm $log
cd ../etc && if [ ! -e local.cfg  ]
	then
		echo `pwd` && if [ ! -e local.cfg-sample  ]
			then 
				echo 'WTF? O_O' && exit && rm $log
			else 
				cp local.cfg-sample local.cfg
				sed -i "s/^OS_AUTH_HOST.*/OS_AUTH_HOST ='$IP'/g" local.cfg
			fi
fi
input=`cd .. && tools/get_auth_token`
cd $dir
echo "$input">>$log
sed -i '1,7d' $log
sed -i "s/^Auth token: //g;s/^Tenant.*id: //g" $log
token=`sed -n '1p' $log`
tenant=`sed -n '2p' $log`
rm $log
url="baseurl = \"http://$IP:9000/v0.2/$tenant\""
token="token = \"$token\""
echo "$url">config.txt
echo "$token">>config.txt
