cd plays
for i in $(seq 2010 2018);
do
  echo $i
  wget "https://raw.githubusercontent.com/ryurko/nflscrapR-data/master/play_by_play_data/regular_season/reg_pbp_${i}.csv"
done
