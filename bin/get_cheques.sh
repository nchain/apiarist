port=$1

ports=(
4
7
29
6
28
56
1
22
9
55
5
44
16
40
30
31
2
8
60
42
3
57
33
10
24
12
19)

function check_all {
  for x in "${ports[@]}"
  do
    port=$(( $x + 1634 ))
    echo "port: $port"
    curl "http://localhost:${port}/chequebook/cheque"
  done
}

if [ -z "$port" ];
then
  check_all
else
  x=$port
  echo 'list cheques'
  echo
  curl "http://localhost:${x}/chequebook/cheque" | jq
  echo
  echo 'list addresses'
  echo
  curl "http://localhost:${x}/addresses" | jq
  echo
  echo 'get balance'
  echo
  curl "http://localhost:${x}/chequebook/balance" | jq
fi