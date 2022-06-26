#!/bin/bash

echo "new ip is: "$1

#echo "old file:"
sed -n '/http:\/\/.*:3000/p' ./apps/lucky_sheet/templates/*

echo "after switch"
#注意：单引号会失效。
sed -i "s/http:\/\/.*:3000/http:\/\/$1:3000/g" ./apps/lucky_sheet/templates/*
#sed -n '/http:\/\/.*:3000/p' ./apps/lucky_sheet/templates/*

SETTING="./luckysheet_obj/settings.py"

vim $SETTING << EOF
:/ALLOWED_HOSTS
AxA, '$1']

:wq
EOF


sed -i "s/http:\/\/.*:.*\/luckysheetloadurl/http:\/\/$1:8080\/luckysheetloadurl/g" $SETTING
sed -i "s/ws:\/\/.*:.*\/luckysheetupdateurl/ws:\/\/$1:8080\/luckysheetupdateurl/g" $SETTING

#redis可能不用切
#sed -i "s/redis:\/\/.*:6379/redis:\/\/$1:6379/g" $SETTING
#sed -i "s/'HOST': '.*'/'HOST': '$1'/g" $SETTING
