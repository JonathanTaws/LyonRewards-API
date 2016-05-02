#!/bin/bash
# Indique au système que l'argument qui suit est le programme utilisé pour exécuter ce fichier
# En règle générale, les "#" servent à mettre en commentaire le texte qui suit comme ici

#source input.cfg


echo Update groups
x=$(expr $(cat input.cfg | jq '.groups | length') - 1)
for i in $(seq 0 $x)
do
	group=$(cat input.cfg | jq ".groups[$i]")
	#curl -H "Content-Type: application/json" -X POST -d group 'https://lyonrewards.antoine-chabert.fr/api/groups' 
	echo $group
done

echo Update acts
x=$(expr $(cat input.cfg | jq '.acts | length') - 1)
for i in $(seq 0 $x)
do
	act=$(cat input.cfg | jq ".acts[$i]")
	#curl -H "Content-Type: application/json" -X POST -d act 'https://lyonrewards.antoine-chabert.fr/api/acts' 
	echo $act
done

echo Update partners
x=$(expr $(cat input.cfg | jq '.partners | length') - 1)
for i in $(seq 0 $x)
do
	partner=$(cat input.cfg | jq ".partners[$i]")
	#curl -H "Content-Type: application/json" -X POST -d partner 'https://lyonrewards.antoine-chabert.fr/api/partners' 
	echo $partner
done

echo Update tags
x=$(expr $(cat input.cfg | jq '.tags | length') - 1)
for i in $(seq 0 $x)
do
	tag=$(cat input.cfg | jq ".tags[$i]")
	#curl -H "Content-Type: application/json" -X POST -d tag 'https://lyonrewards.antoine-chabert.fr/api/tags' 
	echo $tag
done

echo Update users
x=$(expr $(cat input.cfg | jq '.users | length') - 1)
for i in $(seq 0 $x)
do
	user=$(cat input.cfg | jq ".users[$i]")
	#curl -H "Content-Type: application/json" -X POST -d user 'https://lyonrewards.antoine-chabert.fr/api/users' 
	echo $user
done

echo Update offers
x=$(expr $(cat input.cfg | jq '.offers | length') - 1)
for i in $(seq 0 $x)
do
	offer=$(cat input.cfg | jq ".offers[$i]")
	#curl -H "Content-Type: application/json" -X POST -d offer 'https://lyonrewards.antoine-chabert.fr/api/offers' 
	echo $offer
done

echo Update events
x=$(expr $(cat input.cfg | jq '.events | length') - 1)
for i in $(seq 0 $x)
do
	event=$(cat input.cfg | jq ".events[$i]")
	#curl -H "Content-Type: application/json" -X POST -d event 'https://lyonrewards.antoine-chabert.fr/api/events' 
	echo $event
done



exit 0