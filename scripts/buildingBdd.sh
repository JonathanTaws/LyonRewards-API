#!/bin/bash
# Indique au système que l'argument qui suit est le programme utilisé pour exécuter ce fichier
# En règle générale, les "#" servent à mettre en commentaire le texte qui suit comme ici

#source input.cfg


echo Update groups
x=$(expr $(cat input.cfg | jq '.groups | length') - 1)
for i in $(seq 0 $x)
do
	name=$(cat input.cfg | jq ".groups[$i] | .name")
	curl --data-urlencode name=$name 'https://lyonrewards.antoine-chabert.fr/api/groups/' 
done

echo Update acts
x=$(expr $(cat input.cfg | jq '.acts | length') - 1)
for i in $(seq 0 $x)
do
	title=$(cat input.cfg | jq ".acts[$i] | .title")
	description=$(cat input.cfg | jq ".acts[$i] | .description")
	points=$(cat input.cfg | jq ".acts[$i] | .points")
	curl --data-urlencode title=$title&description=$description&points=$points 'https://lyonrewards.antoine-chabert.fr/api/acts/' 
done

echo Update partners
x=$(expr $(cat input.cfg | jq '.partners | length') - 1)
for i in $(seq 0 $x)
do
	name=$(cat input.cfg | jq ".partners[$i] | .name")
	description=$(cat input.cfg | jq ".partners[$i] | .description")
	adress=$(cat input.cfg | jq ".partners[$i] | .points")
	image_url=$(cat input.cfg | jq ".partners[$i] | .image_url")
	curl --data-urlencode name=$name&description=$description&adress=$adress&image_url=$image_url 'https://lyonrewards.antoine-chabert.fr/api/partners/' 
done

echo Update tags
x=$(expr $(cat input.cfg | jq '.tags | length') - 1)
for i in $(seq 0 $x)
do
	title=$(cat input.cfg | jq ".tags[$i] | .title")
	curl --data-urlencode title=$title 'https://lyonrewards.antoine-chabert.fr/api/tags/' 
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
	curl --data-urlencode username=$username&password=$password&email=$email&first_name=$first_name&last_name=$last_name&date_joined=$date_joined&global_points=$global_points&current_points=$current_points&last_tfh_points=$last_tfh_points&current_month_points=$current_month_points&group=$group 'https://lyonrewards.antoine-chabert.fr/api/users/' 
done

echo Update offers
x=$(expr $(cat input.cfg | jq '.offers | length') - 1)
for i in $(seq 0 $x)
do
	partner=$(cat input.cfg | jq ".offers[$i] | .partner")
	description=$(cat input.cfg | jq ".offers[$i] | .description")
	points=$(cat input.cfg | jq ".offers[$i] | .points")
	title=$(cat input.cfg | jq ".offers[$i] | .title")
	curl --data-urlencode partner=$partner&description=$description&points=$points&title=$title 'https://lyonrewards.antoine-chabert.fr/api/offers/' 
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
	curl --data-urlencode tags=$tags&title=$title&description=$description&publish_date=$publish_date&start_date=$start_date&end_date=$end_date&latitude=$latitude&longitude=$longitude&image_url=$image_url&address=$address&partner=$partner 'https://lyonrewards.antoine-chabert.fr/api/events/' 
done

echo Travail Terminé.

exit 0