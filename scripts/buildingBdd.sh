#!/bin/bash
# Indique au système que l'argument qui suit est le programme utilisé pour exécuter ce fichier
# En règle générale, les "#" servent à mettre en commentaire le texte qui suit comme ici

#source input.cfg


echo Update groups
x=$(expr $(cat input.cfg | jq '.groups | length') - 1)
for i in $(seq 0 $x)
do
	name=$(cat input.cfg | jq ".groups[$i] | .name" | sed s/\"//g)
	curl --data-urlencode "name=$name" 'https://lyonrewards.antoine-chabert.fr/api/groups/' 
done

echo Update acts
x=$(expr $(cat input.cfg | jq '.acts | length') - 1)
for i in $(seq 0 $x)
do
	type_of_act=$(cat input.cfg | jq ".acts[$i] | .type_of_act" | sed s/\"//g)
	title=$(cat input.cfg | jq ".acts[$i] | .title" | sed s/\"//g)
	treasure_hunt=$(cat input.cfg | jq ".acts[$i] | .treasure_hunt" | sed s/\"//g)
	type=$(cat input.cfg | jq ".acts[$i] | .type" | sed s/\"//g)
	distance_step=$(cat input.cfg | jq ".acts[$i] | .distance_step" | sed s/\"//g)
	description=$(cat input.cfg | jq ".acts[$i] | .description" | sed s/\"//g)
	points=$(cat input.cfg | jq ".acts[$i] | .points" | sed s/\"//g)
	if [ $type_of_act = "qrcode" ]
	then
		url="https://lyonrewards.antoine-chabert.fr/api/acts/?type=qrcode"
		curl --data-urlencode "title=$title" --data-urlencode "treasure_hunt=$treasure_hunt" --data-urlencode "points=$points" --data-urlencode "description=$description" $url 

	else
		url="https://lyonrewards.antoine-chabert.fr/api/acts/?type=travel"
		curl --data-urlencode "title=$title" --data-urlencode "description=$description" --data-urlencode "points=$points" --data-urlencode "distance_step=$distance_step" --data-urlencode "type=$type" $url 
	fi
done

echo Update partners
x=$(expr $(cat input.cfg | jq '.partners | length') - 1)
for i in $(seq 0 $x)
do
	name=$(cat input.cfg | jq ".partners[$i] | .name")
	description=$(cat input.cfg | jq ".partners[$i] | .description")
	adress=$(cat input.cfg | jq ".partners[$i] | .points")
	image_url=$(cat input.cfg | jq ".partners[$i] | .image_url")
	curl --data-urlencode "name=$name" --data-urlencode "description=$description" --data-urlencode "adress=$adress" --data-urlencode "image_url=$image_url" 'https://lyonrewards.antoine-chabert.fr/api/partners/' 
done

echo Update tags
x=$(expr $(cat input.cfg | jq '.tags | length') - 1)
for i in $(seq 0 $x)
do
	title=$(cat input.cfg | jq ".tags[$i] | .title")
	curl --data-urlencode "title=$title" 'https://lyonrewards.antoine-chabert.fr/api/tags/' 
done

echo Update users
x=$(expr $(cat input.cfg | jq '.users | length') - 1)
for i in $(seq 0 $x)
do
	username=$(cat input.cfg | jq ".users[$i] | .username")
	password=$(cat input.cfg | jq ".users[$i] | .password")
	email=$(cat input.cfg | jq ".users[$i] | .email")
	first_name=$(cat input.cfg | jq ".users[$i] | .first_name")
	last_name=$(cat input.cfg | jq ".users[$i] | .last_name")
	date_joined=$(cat input.cfg | jq ".users[$i] | .date_joined")
	global_points=$(cat input.cfg | jq ".users[$i] | .global_points")
	current_points=$(cat input.cfg | jq ".users[$i] | .current_points")
	last_tfh_points=$(cat input.cfg | jq ".users[$i] | .last_tfh_points")
	current_month_points=$(cat input.cfg | jq ".users[$i] | .current_month_points")
	group=$(cat input.cfg | jq ".users[$i] | .group")
	curl --data-urlencode "username=$username" --data-urlencode "password=$password" --data-urlencode "email=$email" --data-urlencode "first_name=$first_name" --data-urlencode "last_name=$last_name" --data-urlencode "date_joined=$date_joined" --data-urlencode "global_points=$global_points" --data-urlencode "current_points=$current_points" --data-urlencode "last_tfh_points=$last_tfh_points" --data-urlencode "current_month_points=$current_month_points" --data-urlencode "group=$group" 'https://lyonrewards.antoine-chabert.fr/api/users/' 
done

echo Update offers
x=$(expr $(cat input.cfg | jq '.offers | length') - 1)
for i in $(seq 0 $x)
do
	partner=$(cat input.cfg | jq ".offers[$i] | .partner")
	description=$(cat input.cfg | jq ".offers[$i] | .description")
	points=$(cat input.cfg | jq ".offers[$i] | .points")
	title=$(cat input.cfg | jq ".offers[$i] | .title")
	curl --data-urlencode "partner=$partner" --data-urlencode "description=$description" --data-urlencode "points=$points" --data-urlencode "title=$title" 'https://lyonrewards.antoine-chabert.fr/api/offers/' 
done

echo Update events
x=$(expr $(cat input.cfg | jq '.events | length') - 1)
for i in $(seq 0 $x)
do
	tags=$(cat input.cfg | jq ".events[$i] | .tags")
	title=$(cat input.cfg | jq ".events[$i] | .title")
	description=$(cat input.cfg | jq ".events[$i] | .description")
	publish_date=$(cat input.cfg | jq ".events[$i] | .publish_date")
	start_date=$(cat input.cfg | jq ".events[$i] | .start_date")
	end_date=$(cat input.cfg | jq ".events[$i] | .end_date")
	latitude=$(cat input.cfg | jq ".events[$i] | .latitude")
	longitude=$(cat input.cfg | jq ".events[$i] | .longitude")
	image_url=$(cat input.cfg | jq ".events[$i] | .image_url")
	address=$(cat input.cfg | jq ".events[$i] | .address")
	partner=$(cat input.cfg | jq ".events[$i] | .partner")
	curl --data-urlencode "tags=$tags" --data-urlencode "title=$title" --data-urlencode "description=$description" --data-urlencode "publish_date=$publish_date" --data-urlencode "start_date=$start_date" --data-urlencode "end_date=$end_date" --data-urlencode "latitude=$latitude" --data-urlencode "longitude=$longitude" --data-urlencode "image_url=$image_url" --data-urlencode "address=$address" --data-urlencode "partner=$partner" 'https://lyonrewards.antoine-chabert.fr/api/events/' 
done

echo Travail Terminé.

exit 0